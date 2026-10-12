# VidyaPath: AI Tutor for Rural Students (SDG 4)

Full prototype that follows the four steps in the presentation: Log in, Diagnose, Learn, Track.

## How the project maps to "How it works"
| Step | What happens | Files |
|---|---|---|
| 1. Log in | Student picks grade, subject and language; saved in a database | app.py, db.py |
| 2. Diagnose | 8-question quiz builds a learner profile (Bayesian Knowledge Tracing) | app.py, ml_engine.py |
| 3. Learn | ML picks each question; IBM watsonx.ai explains mistakes by text and voice; students can ask doubts by voice or text | ml_engine.py, tutor_ai.py, voice.py |
| 4. Track | Teacher/parent dashboard: class table, K-Means learner groups, gaps, CSV report, parent WhatsApp message | app.py, ml_engine.py, seed_demo.py |

## AI/ML used
- Gradient Boosting classifier: predicts the chance of a correct answer
- Bayesian Knowledge Tracing: mastery per topic
- Adaptive recommender: next question at ~70% predicted success, favouring weak topics
- K-Means clustering: groups students into Needs support / Developing / On track
- Generative AI (IBM watsonx.ai, Granite): explanations, doubt answering, parent messages
- Speech: gTTS (text-to-speech) and SpeechRecognition (speech-to-text), English, Hindi, Gujarati

## Tools required
Python 3.10+, VS Code, Streamlit, scikit-learn, pandas, numpy, joblib, SQLite (built in), gTTS, SpeechRecognition, ibm-watsonx-ai, IBM Cloud account (free Lite plan), GitHub.

## Run in VS Code
```
python -m venv .venv
.venv\Scripts\activate          (Mac/Linux: source .venv/bin/activate)
pip install -r requirements.txt
python ml_engine.py
streamlit run app.py
```
Optional IBM watsonx: set `WATSONX_API_KEY` and `WATSONX_PROJECT_ID` before running. Without them the app uses built-in solutions.

## Demo tips
1. Choose "Teacher / Parent" and click "Load demo class" to fill the dashboard.
2. Choose "Student", log in, finish the diagnostic, then answer one question wrong to hear the AI explanation.

## Limits and next steps
- The ML model trains on **synthetic** data; retrain on real pilot data (`synth()` in ml_engine.py).
- Demo bank is 12 Grade 8 maths questions; grade/subject choices are stored but only this bank is used.
- Voice needs internet. Check Gujarati/Hindi quality of your watsonx model (set `WATSONX_MODEL_ID`).
- Not included yet: WhatsApp bot, native Android app, cloud database (SQLite is used locally).
