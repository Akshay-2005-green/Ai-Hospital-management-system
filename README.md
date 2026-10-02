# HealthForge AI

Hospital Flow Management System.

## Included modules

- Patient registration/login
- Doctor portal
- Receptionist dashboard
- Admin command center
- Appointment booking and approval
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

Demo passwords are 123456. Change them before real deployment.

## MySQL

Set DATABASE_URL before starting, for example:
mysql+pymysql://root:password@localhost/healthforge

## Important

The ML waiting-time component is intentionally a transparent baseline. For the final academic system, train and evaluate a model such as RandomForestRegressor/XGBoost on a properly collected and de-identified hospital dataset.

The document summarization code currently performs PDF text extraction and extractive-style keyword selection. For a production/advanced NLP version, integrate a validated summarization model such as T5/BART and add healthcare-specific evaluation, privacy controls, and human review.
