"""Lightweight database (SQLite). Swap for IBM Db2 / Cloudant for a cloud deployment."""
import os, sqlite3, time
PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vidyapath.db")

def conn():
    c = sqlite3.connect(PATH)
    c.row_factory = sqlite3.Row
    c.executescript("""CREATE TABLE IF NOT EXISTS students(id INTEGER PRIMARY KEY, name TEXT, phone TEXT UNIQUE, grade INT, subject TEXT, language TEXT);
    CREATE TABLE IF NOT EXISTS responses(id INTEGER PRIMARY KEY, student_id INT, ts REAL, qid INT, topic TEXT, level INT, correct INT, seconds REAL, phase TEXT);""")
    return c

def login(name, phone, grade, subject, language):
    with conn() as c:
        c.execute("INSERT OR IGNORE INTO students(name,phone,grade,subject,language) VALUES(?,?,?,?,?)", (name, phone, grade, subject, language))
        c.execute("UPDATE students SET name=?,grade=?,subject=?,language=? WHERE phone=?", (name, grade, subject, language, phone))
        return dict(c.execute("SELECT * FROM students WHERE phone=?", (phone,)).fetchone())

def add_response(sid, qid, topic, level, correct, seconds, phase, ts=None):
    with conn() as c:
        c.execute("INSERT INTO responses(student_id,ts,qid,topic,level,correct,seconds,phase) VALUES(?,?,?,?,?,?,?,?)",
                  (sid, ts or time.time(), qid, topic, level, int(correct), seconds, phase))

def history(sid):
    with conn() as c:
        return [dict(r) for r in c.execute("SELECT * FROM responses WHERE student_id=? ORDER BY ts,id", (sid,))]

def students():
    with conn() as c:
        return [dict(r) for r in c.execute("SELECT * FROM students ORDER BY name")]
