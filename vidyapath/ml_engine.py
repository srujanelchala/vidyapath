"""ML core. (1) Gradient Boosting predicts P(correct); (2) Bayesian Knowledge Tracing tracks mastery;
(3) adaptive picker chooses the next question; (4) K-Means groups learners for the teacher dashboard.
Training data is SYNTHETIC; retrain on real pilot data."""
import os
from collections import Counter
import joblib
import numpy as np
from sklearn.cluster import KMeans
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.model_selection import train_test_split
from question_bank import QUESTIONS, TOPICS

P_INIT, P_LEARN, P_GUESS, P_SLIP = 0.3, 0.15, 0.25, 0.1
PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model.joblib")

def synth(n=6000, seed=42):
    r = np.random.default_rng(seed)
    m = r.uniform(0, 1, n); d = r.integers(1, 4, n)
    rec = np.clip(m + r.normal(0, 0.15, n), 0, 1); att = r.integers(0, 20, n)
    t = np.clip(r.normal(45 - 20 * m + 6 * d, 8, n), 5, 120)
    p = 0.2 + 0.75 / (1 + np.exp(-6 * (m - 0.3 * d + 0.2)))
    return np.c_[m, d, rec, att, t], (r.random(n) < p).astype(int)

def train():
    X, y = synth()
    Xt, Xv, yt, yv = train_test_split(X, y, test_size=0.2, random_state=1)
    model = GradientBoostingClassifier(random_state=1).fit(Xt, yt)
    acc = accuracy_score(yv, model.predict(Xv)); auc = roc_auc_score(yv, model.predict_proba(Xv)[:, 1])
    joblib.dump(model, PATH)
    return model, acc, auc

def load_model():
    return joblib.load(PATH) if os.path.exists(PATH) else train()[0]

def bkt(p, ok):
    post = p * (1 - P_SLIP) / (p * (1 - P_SLIP) + (1 - p) * P_GUESS) if ok else p * P_SLIP / (p * P_SLIP + (1 - p) * (1 - P_GUESS))
    return post + (1 - post) * P_LEARN

def mastery(hist):
    """Replay a student's answers through BKT to get mastery per topic."""
    m = {t: P_INIT for t in TOPICS}
    for h in hist:
        m[h["topic"]] = bkt(m[h["topic"]], h["correct"])
    return m

def predict(model, i, hist, secs=30):
    q = QUESTIONS[i]; m = mastery(hist); h = [x for x in hist if x["topic"] == q["topic"]]
    rec = float(np.mean([x["correct"] for x in h[-5:]])) if h else 0.5
    return float(model.predict_proba([[m[q["topic"]], q["diff"], rec, len(h), secs]])[0][1])

def next_question(model, hist):
    """Pick a question with ~70% predicted success, favouring weak topics."""
    seen = {h["qid"] for h in hist}
    pool = [i for i in range(len(QUESTIONS)) if i not in seen] or [i for i in range(len(QUESTIONS)) if not hist or i != hist[-1]["qid"]]
    m = mastery(hist)
    return min(pool, key=lambda i: abs(predict(model, i, hist) - 0.7) - 0.3 * (1 - m[QUESTIONS[i]["topic"]]))

def diagnostic_ids():
    return [i for i, q in enumerate(QUESTIONS) if q["diff"] <= 2]

def gaps(hist):
    m = mastery(hist); n = Counter(h["topic"] for h in hist)
    return [t for t in TOPICS if n[t] >= 2 and m[t] < 0.5]

def label(avg):
    return "Needs support" if avg < 0.4 else "Developing" if avg < 0.65 else "On track"

def profile(hist):
    return label(float(np.mean(list(mastery(hist).values()))))

def cluster(mats):
    """K-Means (k=3) on mastery vectors groups the class into learner profiles."""
    ids = list(mats); X = np.array([[mats[s][t] for t in TOPICS] for s in ids])
    if len(ids) < 3:
        return {s: label(X[k].mean()) for k, s in enumerate(ids)}
    km = KMeans(3, n_init=10, random_state=0).fit(X)
    names = {int(c): n for c, n in zip(np.argsort(km.cluster_centers_.mean(1)), ["Needs support", "Developing", "On track"])}
    return {s: names[int(l)] for s, l in zip(ids, km.labels_)}

if __name__ == "__main__":
    _, acc, auc = train()
    print(f"Model trained on synthetic data: accuracy={acc:.2f}, AUC={auc:.2f}")
