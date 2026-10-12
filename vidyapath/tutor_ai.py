"""Generative AI tutor via IBM watsonx.ai (Granite). Falls back to built-in text when no credentials are set."""
import os

def _watsonx(prompt):
    from ibm_watsonx_ai import Credentials
    from ibm_watsonx_ai.foundation_models import ModelInference
    model = ModelInference(
        model_id=os.getenv("WATSONX_MODEL_ID", "ibm/granite-3-8b-instruct"),
        credentials=Credentials(url=os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com"), api_key=os.environ["WATSONX_API_KEY"]),
        project_id=os.environ["WATSONX_PROJECT_ID"],
        params={"max_new_tokens": 250, "temperature": 0.3},
    )
    return model.generate_text(prompt=prompt)

def _llm(prompt):
    if os.getenv("WATSONX_API_KEY") and os.getenv("WATSONX_PROJECT_ID"):
        try:
            return _watsonx(prompt).strip(), "IBM watsonx.ai"
        except Exception:
            pass
    return None, "offline mode"

def explain(q, chosen, language):
    text, src = _llm(f"You are a kind village-school maths tutor for a Grade 8 student. Reply in {language}, in simple words, under 80 words, "
                     f"with one everyday village-life example.\nQuestion: {q['q']}\nStudent answered: {chosen}\nCorrect answer: {q['opts'][q['ans']]}\n"
                     f"Approved solution (do not contradict it): {q['expl']}\nExplain the mistake gently and show the steps.")
    return (text, src) if text else (q["expl"], "built-in solution (offline mode)")

def answer_doubt(doubt, q, language):
    text, src = _llm(f"You are a kind school maths tutor. Reply in {language}, simply, under 100 words. Answer only school maths or study questions; "
                     f"otherwise politely steer back to maths.\nThe student was last working on: {q['q']} (solution: {q['expl']})\nStudent's doubt: {doubt}")
    return (text, src) if text else (f"Free-form answers need IBM watsonx.ai keys. For now, here is a worked example: {q['expl']}", "offline mode")

def parent_message(name, mastery, gaps, language):
    summary = ", ".join(f"{t} {m:.0%}" for t, m in mastery.items())
    text, src = _llm(f"Write a short, warm WhatsApp message (under 60 words) in {language} to the parent of {name}, a school student. "
                     f"Maths mastery by topic: {summary}. Topics needing practice: {', '.join(gaps) or 'none'}. Suggest one practical way to encourage them.")
    if text:
        return text, src
    todo = f" Needs more practice in: {', '.join(gaps)}." if gaps else " Doing well, please keep encouraging!"
    return f"Hello! Maths progress for {name}: {summary}.{todo}", "offline mode"
