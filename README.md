# HealthForge AI

Hospital Flow Management System.

## Included modules

- Patient registration/login
- Doctor portal
- Receptionist dashboard
- Admin command center
- Appointment booking and approval
- Receptionist scheduling, walk-in registration, emergency queue priority, and doctor-shift conflict checks
- Doctor daily schedule and queue progression
- Token generation
- Queue management
- Emergency priority flag
- Doctor availability
- Bed availability
- Waiting-time prediction baseline
- Medical PDF text extraction and prototype summarization
- MySQL/SQLite-compatible SQLAlchemy database
- Flask architecture ready for expansion

## Run

1. Create virtual environment:
   python -m venv venv

2. Activate:
   Windows: venv\Scripts\activate
   Linux/macOS: source venv/bin/activate

3. Install:
   pip install -r requirements.txt

4. Seed demo data:
   python seed.py

5. Start:
   python run.py

Open http://127.0.0.1:5000

The receptionist dashboard supports Today, This Week, and All appointment views, patient search, check-in/cancellation actions, booking for existing or new walk-in patients, and emergency arrivals. Appointment slots use configured doctor availability or doctor shift timings; emergency cases bypass normal appointment slots, require an on-duty doctor, and are placed before routine waiting cases for clinician assessment.

Demo passwords are 123456. Change them before real deployment.

## MySQL

Set DATABASE_URL before starting, for example:
mysql+pymysql://root:password@localhost/healthforge

## Symptom assistant

The patient symptom assistant uses Google Gemini to suggest a care urgency and medical specialty. Configure the API key on the server; never commit it to source control:

```powershell
$env:GEMINI_API_KEY = "your-key"
$env:GEMINI_MODEL = "gemini-2.5-flash" # Optional; defaults to this model
```

Restart the application after setting the environment variables. The assistant sends only the symptom description, duration, and severity to Google for the request. This feature does not save those inputs. Do not enter identifying information. Its output is general care navigation, not a diagnosis or a substitute for a clinician. Emergency warning signs are handled locally and are not sent to Gemini.

## Important

The ML waiting-time component is intentionally a transparent baseline. For the final academic system, train and evaluate a model such as RandomForestRegressor/XGBoost on a properly collected and de-identified hospital dataset.

The document summarization code currently performs PDF text extraction and extractive-style keyword selection. For a production/advanced NLP version, integrate a validated summarization model such as T5/BART and add healthcare-specific evaluation, privacy controls, and human review.
#
Abhishek Singh
