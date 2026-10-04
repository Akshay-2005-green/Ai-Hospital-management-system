import json
import logging
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from flask import Blueprint, current_app, redirect, render_template, request, session, url_for


symptoms_bp = Blueprint("symptoms", __name__)
logger = logging.getLogger(__name__)

MAX_SYMPTOM_LENGTH = 2000
MAX_DURATION_LENGTH = 120
SPECIALTIES = {
    "general practitioner",
    "cardiologist",
    "dermatologist",
    "endocrinologist",
    "gastroenterologist",
    "neurologist",
    "orthopedist",
    "pediatrician",
    "psychiatrist",
    "pulmonologist",
    "gynecologist",
    "ophthalmologist",
    "ent specialist",
    "urologist",
    "urgent care",
    "emergency department",
}
URGENCY_LEVELS = {"routine", "soon", "urgent"}
CARE_GUIDANCE = {
    "routine": "Consider booking a routine appointment with a clinician. If symptoms persist or worsen, seek care sooner.",
    "soon": "Please arrange an appointment with a clinician soon. If symptoms become severe or worsen, seek urgent care.",
    "urgent": "Please seek urgent medical assessment today. If symptoms are severe or worsening, go to an emergency department.",
}


def _request_gemini(symptoms, duration, severity):
    api_key = current_app.config.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("The Gemini API key is not configured.")

    model = current_app.config.get("GEMINI_MODEL", "gemini-2.5-flash")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    payload = {
        "systemInstruction": {
            "parts": [{
                "text": (
                    "You are a cautious symptom navigation assistant, not a clinician. "
                    "Do not diagnose, rule out serious illness, recommend medication, or "
                    "give treatment instructions. Recommend only an appropriate care "
                    "urgency and one medical specialty. If uncertain, recommend a "
                    "general practitioner. "
                    "Tell the user to seek emergency help for potentially serious symptoms. "
                    "The user has already been asked separately about emergency warning signs. "
                    "Select exactly one specialty and urgency from the provided schema. "
                    "Do not produce free-text advice. Output only JSON."
                )
            }]
        },
        "contents": [{
            "role": "user",
            "parts": [{
                "text": (
                    f"Symptoms: {symptoms}\n"
                    f"Duration: {duration}\n"
                    f"Self-reported severity (1-10): {severity}"
                )
            }]
        }],
        "generationConfig": {
            "temperature": 0.1,
            "responseMimeType": "application/json",
            "responseSchema": {
                "type": "OBJECT",
                "properties": {
                    "urgency": {"type": "STRING", "enum": ["routine", "soon", "urgent"]},
                    "specialty": {"type": "STRING", "enum": sorted(SPECIALTIES)},
                },
                "required": ["urgency", "specialty"],
                "propertyOrdering": ["urgency", "specialty"],
            },
        },
    }
    api_request = Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": api_key,
        },
        method="POST",
    )

    try:
        with urlopen(api_request, timeout=20) as response:
            response_data = json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        logger.error("Gemini symptom assistant returned HTTP %s", error.code)
        raise RuntimeError("The symptom assistant could not complete the request. Please try again later.") from error
    except (URLError, TimeoutError) as error:
        logger.warning("Gemini symptom assistant connection failed: %s", error)
        raise RuntimeError("The symptom assistant is temporarily unavailable. Please try again later.") from error
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        logger.error("Gemini symptom assistant returned an unreadable response")
        raise RuntimeError("The symptom assistant returned an invalid response. Please try again later.") from error

    try:
        response_text = response_data["candidates"][0]["content"]["parts"][0]["text"]
        result = json.loads(response_text)
    except (KeyError, IndexError, TypeError, json.JSONDecodeError) as error:
        logger.error("Gemini symptom assistant response did not match the expected structure")
        raise RuntimeError("The symptom assistant returned an invalid response. Please try again later.") from error

    if not isinstance(result, dict):
        logger.error("Gemini symptom assistant response was not a JSON object")
        raise RuntimeError("The symptom assistant returned an invalid response. Please try again later.")

    urgency = result.get("urgency")
    specialty = result.get("specialty")
    if (
        urgency not in URGENCY_LEVELS
        or not isinstance(specialty, str)
        or specialty.lower() not in SPECIALTIES
    ):
        logger.error("Gemini symptom assistant response contained invalid values")
        raise RuntimeError("The symptom assistant returned an invalid response. Please try again later.")

    return {
        "urgency": urgency,
        "specialty": specialty,
        "explanation": (
            f"Based on the information you entered, {specialty} may be a suitable "
            "place to start. This is a care-navigation suggestion, not a diagnosis."
        ),
        "next_step": CARE_GUIDANCE[urgency],
        "emergency": False,
    }


@symptoms_bp.route("/symptom-assistant", methods=["GET", "POST"])
def assistant():
    if "patient_id" not in session:
        return redirect(url_for("auth.login"))

    form_data = {"symptoms": "", "duration": "", "severity": ""}
    result = None
    error = None

    if request.method == "POST":
        form_data = {
            "symptoms": request.form.get("symptoms", "").strip(),
            "duration": request.form.get("duration", "").strip(),
            "severity": request.form.get("severity", "").strip(),
        }

        if request.form.get("emergency_signs") == "yes":
            result = {
                "emergency": True,
                "urgency": "emergency",
            }
        elif not form_data["symptoms"]:
            error = "Describe the symptoms you want help navigating."
        elif len(form_data["symptoms"]) > MAX_SYMPTOM_LENGTH:
            error = f"Keep the symptom description under {MAX_SYMPTOM_LENGTH} characters."
        elif len(form_data["duration"]) > MAX_DURATION_LENGTH:
            error = f"Keep the duration under {MAX_DURATION_LENGTH} characters."
        elif form_data["severity"] not in {str(value) for value in range(1, 11)}:
            error = "Choose a severity from 1 to 10."
        elif request.form.get("privacy_consent") != "yes":
            error = "Confirm that you understand your symptoms will be sent to Google Gemini for this request."
        else:
            try:
                result = _request_gemini(
                    form_data["symptoms"],
                    form_data["duration"],
                    int(form_data["severity"]),
                )
            except RuntimeError as assistant_error:
                error = str(assistant_error)

    return render_template(
        "symptom_assistant.html",
        form_data=form_data,
        result=result,
        error=error,
    )
