import time
import pandas as pd
import streamlit as st
import db
import ml_engine as me
import voice
from question_bank import QUESTIONS, TOPICS
from seed_demo import seed
from tutor_ai import answer_doubt, explain, parent_message

st.set_page_config(page_title="VidyaPath", page_icon="📚")
S = st.session_state
LANGS = {"English": "English", "हिन्दी": "Hindi", "ગુજરાતી": "Gujarati"}
DIAG = sorted(me.diagnostic_ids(), key=lambda i: (QUESTIONS[i]["diff"], QUESTIONS[i]["topic"]))

@st.cache_resource
def get_model():
    return me.load_model()

model = get_model()
st.title("📚 VidyaPath: your personal AI tutor")
role = st.sidebar.radio("I am a", ["Student", "Teacher / Parent"])
voice_on = st.sidebar.toggle("🔊 Read explanations aloud", value=True)
st.sidebar.caption("Set WATSONX_API_KEY and WATSONX_PROJECT_ID to use IBM watsonx.ai.")

def play(text, lang):
    if voice_on:
        audio = voice.speak(text, lang)
        if audio:
            st.audio(audio, format="audio/mp3")

def mastery_chart(hist):
    st.bar_chart(pd.DataFrame({"Mastery (0 to 1)": me.mastery(hist)}))
    g = me.gaps(hist)
    if g:
        st.warning("Learning gaps: " + ", ".join(g))
    else:
        st.info("No learning gaps flagged yet.")

def ask_question(qi, hist, phase):
    q = QUESTIONS[qi]
    if S.get("t0") is None:
        S.t0 = time.time()
    if phase == "learn":
        st.caption(f"{q['topic']} | Level {'⭐' * q['diff']} | ML-predicted chance you get it right: {me.predict(model, qi, hist):.0%}")
    st.subheader(q["q"])
    choice = st.radio("Choose one", q["opts"], index=None, key=f"r{len(hist)}")
    if st.button("Submit", disabled=choice is None):
        ok = q["opts"].index(choice) == q["ans"]
        db.add_response(S.student["id"], qi, q["topic"], q["diff"], ok, round(time.time() - S.t0, 1), phase)
        S.t0 = None
        if phase == "learn":
            text, src = ("", "") if ok else explain(q, choice, S.student["language"])
            S.fb = dict(qid=qi, ok=ok, text=text, src=src)
        st.rerun()

def student_view():
    if "student" not in S:
        st.caption("Step 1 of 4: Log in")
        with st.form("login"):
            name = st.text_input("Your name"); phone = st.text_input("Phone number")
            grade = st.selectbox("Grade", [6, 7, 8, 9, 10], index=2)
            subject = st.selectbox("Subject", ["Maths"])
            lang = st.selectbox("Language", list(LANGS))
            go = st.form_submit_button("Start learning")
        if go:
            if name.strip() and phone.strip():
                S.student = db.login(name.strip(), phone.strip(), grade, subject, LANGS[lang]); S.fb = None; S.t0 = None
                st.rerun()
            else:
                st.error("Please enter your name and phone number.")
        st.caption("Demo question bank: Grade 8 Maths. More subjects can be added in question_bank.py.")
        return
    stu = S.student; lang = stu["language"]; hist = db.history(stu["id"])
    st.sidebar.write(f"👋 {stu['name']} | Grade {stu['grade']} | {stu['subject']} | {lang}")
    if st.sidebar.button("Log out"):
        del S["student"]; S.fb = None
        st.rerun()
    todo = [i for i in DIAG if i not in {h["qid"] for h in hist if h["phase"] == "diagnostic"}]
    if todo:
        st.caption("Step 2 of 4: Diagnose. A quick quiz builds your learner profile.")
        st.progress((len(DIAG) - len(todo)) / len(DIAG), text=f"Question {len(DIAG) - len(todo) + 1} of {len(DIAG)}")
        ask_question(todo[0], hist, "diagnostic")
        return
    t_learn, t_doubt, t_prog = st.tabs(["📖 Learn", "🎤 Ask a doubt", "📊 My progress"])
    with t_learn:
        if S.get("fb"):
            fb = S.fb; q = QUESTIONS[fb["qid"]]
            if fb["ok"]:
                st.success("Correct! 🎉")
            else:
                st.error(f"Not quite. The answer is {q['opts'][q['ans']]}")
                st.info(fb["text"]); st.caption(f"Explanation by: {fb['src']}")
                play(fb["text"], lang)
            if st.button("Next question ➡️"):
                S.fb = None
                st.rerun()
        else:
            st.caption("Step 3 of 4: Learn. Difficulty adapts after every answer.")
            ask_question(me.next_question(model, hist), hist, "learn")
    with t_doubt:
        st.caption("Type your doubt, or record it with your voice.")
        typed = st.text_input("Your doubt")
        rec = st.audio_input("Or speak") if hasattr(st, "audio_input") else None
        if st.button("Ask the tutor"):
            text = typed.strip()
            if not text and rec:
                text = voice.transcribe(rec, lang) or ""
                if text:
                    st.caption(f"You said: {text}")
            if text:
                ans, src = answer_doubt(text, QUESTIONS[hist[-1]["qid"]], lang)
                st.info(ans); st.caption(f"Answer by: {src}")
                play(ans, lang)
            else:
                st.warning("I could not understand that. Please type your doubt.")
    with t_prog:
        st.caption("Step 4 of 4: Track")
        st.metric("Learner profile", me.profile(hist))
        mastery_chart(hist)
        df = pd.DataFrame(hist); df["Accuracy so far"] = df["correct"].expanding().mean()
        st.line_chart(df["Accuracy so far"])

def teacher_view():
    st.caption("Step 4 of 4: Track. Teacher and parent dashboard.")
    if st.sidebar.button("Load demo class (12 students)"):
        seed()
        st.rerun()
    studs = db.students()
    if not studs:
        st.info("No students yet. Ask students to log in, or load the demo class from the sidebar.")
        return
    hists = {s["id"]: db.history(s["id"]) for s in studs}
    mats = {s["id"]: me.mastery(hists[s["id"]]) for s in studs}
    groups = me.cluster(mats)
    df = pd.DataFrame([dict(Name=s["name"], Grade=s["grade"], Language=s["language"], Answered=len(hists[s["id"]]),
                            Accuracy=round(sum(h["correct"] for h in hists[s["id"]]) / max(1, len(hists[s["id"]])), 2),
                            Mastery=round(sum(mats[s["id"]].values()) / len(TOPICS), 2), Group=groups[s["id"]],
                            Gaps=", ".join(me.gaps(hists[s["id"]]))) for s in studs])
    c1, c2, c3 = st.columns(3)
    c1.metric("Students", len(df)); c2.metric("Avg accuracy", f"{df['Accuracy'].mean():.0%}"); c3.metric("Need support", int((df["Group"] == "Needs support").sum()))
    st.subheader("Class overview (groups from K-Means)")
    st.dataframe(df, hide_index=True)
    st.download_button("Download report (CSV)", df.to_csv(index=False), "vidyapath_report.csv")
    st.subheader("Class mastery by topic")
    st.bar_chart(pd.DataFrame(mats).T.mean())
    st.subheader("Student detail and parent message")
    sel = st.selectbox("Student", studs, format_func=lambda s: s["name"])
    h = hists[sel["id"]]
    mastery_chart(h)
    if st.button("Generate parent message"):
        msg, src = parent_message(sel["name"], mats[sel["id"]], me.gaps(h), sel["language"])
        st.text_area("Copy and send on WhatsApp", msg, height=140); st.caption(f"Written by: {src}")

if role == "Student":
    student_view()
else:
    teacher_view()
