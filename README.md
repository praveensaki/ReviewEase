# ReviewEase

A research prototype comparing conventional AI code-review feedback with progressive disclosure.

## Current features
- Two interface conditions: Conventional review and Progressive disclosure.
- Deterministic demonstration findings for a Python function.
- Anonymous participant-code sessions.
- Finding decisions and optional comments.
- Interaction event logging.
- Exploratory post-task questionnaire.
- SQLite persistence and aggregate session summary.

## Research limitations
Findings are hand-authored demo data, not LLM output. The questionnaire is exploratory and not a validated measure of AI fatigue or cognitive workload. Do not present demo data as research results. A real study needs a reviewed protocol, suitable validated instruments, consent and appropriate data handling.

## Windows PowerShell setup
Use Python 3.11, 3.12 or 3.13 in a fresh virtual environment:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

## Structure
- `app.py`: application entry point
- `src/review_data.py`: demo task and findings
- `src/review_ui.py`: review interface
- `src/database.py`: SQLite persistence
- `tests/`: automated tests (to be expanded)

## Automated Tests

The project includes automated tests covering:

- Session creation
- Interaction event logging
- Saving and updating review decisions
- Questionnaire submission
- Session summary calculations
- Analytics data loading

Run the tests using:

```powershell
python -m pytest -v