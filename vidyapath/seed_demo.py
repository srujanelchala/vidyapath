"""Creates a demo class of 12 simulated students so the teacher dashboard has data."""
import random, time
import db
from question_bank import QUESTIONS, TOPICS

NAMES = ["Asha", "Bhavesh", "Chirag", "Divya", "Esha", "Farhan", "Gita", "Hiren", "Isha", "Jignesh", "Kavya", "Lalit"]

def seed():
    r = random.Random(7); have = {s["phone"] for s in db.students()}
    for k, name in enumerate(NAMES):
        phone = f"90000{k:05d}"
        if phone in have:
            continue
        s = db.login(name, phone, r.choice([7, 8, 9]), "Maths", r.choice(["English", "Hindi", "Gujarati"]))
        ability = {t: r.uniform(0.1, 0.95) for t in TOPICS}; t0 = time.time() - 14 * 86400
        for j in range(r.randint(14, 24)):
            qid = r.randrange(len(QUESTIONS)); q = QUESTIONS[qid]
            p = min(0.95, max(0.05, ability[q["topic"]] - 0.22 * (q["diff"] - 1) + 0.25))
            db.add_response(s["id"], qid, q["topic"], q["diff"], r.random() < p, round(r.uniform(10, 60), 1), "diagnostic" if j < 8 else "learn", ts=t0 + j * 43200)
