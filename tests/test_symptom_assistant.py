import json
from io import BytesIO

from app.routes import symptoms


def _login_as_patient(client):
    with client.session_transaction() as session:
        session["patient_id"] = 10
        session["role"] = "patient"


def test_symptom_assistant_requires_patient_login(app):
    response = app.test_client().get("/symptom-assistant")

    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_emergency_warning_does_not_call_gemini(app, monkeypatch):
    client = app.test_client()
    _login_as_patient(client)

    def unexpected_gemini_call(*_args):
        raise AssertionError("emergency warning signs should not be sent to Gemini")

    monkeypatch.setattr(symptoms, "_request_gemini", unexpected_gemini_call)
    response = client.post(
        "/symptom-assistant",
        data={"emergency_signs": "yes"},
    )

    assert response.status_code == 200
    assert b"Seek emergency help now" in response.data


def test_symptom_assistant_requires_google_data_consent(app, monkeypatch):
    client = app.test_client()
    _login_as_patient(client)

    def unexpected_gemini_call(*_args):
        raise AssertionError("request without consent should not be sent to Gemini")

    monkeypatch.setattr(symptoms, "_request_gemini", unexpected_gemini_call)
    response = client.post(
        "/symptom-assistant",
        data={"symptoms": "mild cough", "duration": "2 days", "severity": "2"},
    )

    assert response.status_code == 200
    assert b"Confirm that you understand" in response.data


def test_missing_gemini_key_shows_setup_error(app):
    client = app.test_client()
    _login_as_patient(client)
    app.config["GEMINI_API_KEY"] = None

    response = client.post(
        "/symptom-assistant",
        data={
            "symptoms": "mild cough",
            "duration": "2 days",
            "severity": "2",
            "privacy_consent": "yes",
        },
    )

    assert response.status_code == 200
    assert b"API key is not configured" in response.data


def test_gemini_request_returns_validated_specialty_and_urgency(app, monkeypatch):
    response_body = {
        "candidates": [{
            "content": {
                "parts": [{
                    "text": json.dumps({
                        "urgency": "soon",
                        "specialty": "pulmonologist",
                    })
                }]
            }
        }]
    }

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def read(self):
            return json.dumps(response_body).encode("utf-8")

    captured = {}

    def fake_urlopen(api_request, timeout):
        captured["request"] = api_request
        captured["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setattr(symptoms, "urlopen", fake_urlopen)
    with app.app_context():
        app.config["GEMINI_API_KEY"] = "test-only-key"
        result = symptoms._request_gemini("dry cough", "2 days", 3)

    request_body = json.loads(captured["request"].data.decode("utf-8"))
    assert captured["request"].get_header("X-goog-api-key") == "test-only-key"
    assert captured["timeout"] == 20
    assert "dry cough" in request_body["contents"][0]["parts"][0]["text"]
    assert result["specialty"] == "pulmonologist"
    assert result["urgency"] == "soon"
    assert "not a diagnosis" in result["explanation"]
    assert "soon" in result["next_step"]


def test_unknown_specialty_from_gemini_is_rejected(app, monkeypatch):
    response_body = {
        "candidates": [{
            "content": {
                "parts": [{
                    "text": json.dumps({
                        "urgency": "routine",
                        "specialty": "miracle healer",
                    })
                }]
            }
        }]
    }

    class FakeResponse(BytesIO):
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

    monkeypatch.setattr(
        symptoms,
        "urlopen",
        lambda _request, **_kwargs: FakeResponse(json.dumps(response_body).encode("utf-8")),
    )
    with app.app_context():
        app.config["GEMINI_API_KEY"] = "test-only-key"
        try:
            symptoms._request_gemini("symptom", "today", 2)
        except RuntimeError as error:
            assert "invalid response" in str(error)
        else:
            raise AssertionError("unknown specialties must not be shown as recommendations")
