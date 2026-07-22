"""
Aven Entertainment 관리 시스템 - 데이터베이스 레이어
SQLite 기반. 앱 최초 실행 시 자동으로 테이블을 생성합니다.
"""
import sqlite3
import os
from datetime import date
import pandas as pd

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "aven.db")


def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS trainees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            birth_date TEXT,
            gender TEXT,
            part TEXT,
            join_date TEXT,
            status TEXT DEFAULT '연습생',
            phone TEXT,
            guardian_contact TEXT,
            memo TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS evaluations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trainee_id INTEGER NOT NULL,
            eval_date TEXT,
            vocal_score INTEGER,
            dance_score INTEGER,
            rap_score INTEGER,
            attitude_score INTEGER,
            memo TEXT,
            FOREIGN KEY (trainee_id) REFERENCES trainees(id) ON DELETE CASCADE
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS training_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_date TEXT,
            start_time TEXT,
            end_time TEXT,
            category TEXT,
            trainer TEXT,
            room TEXT,
            participants TEXT,
            memo TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS budget_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_date TEXT,
            category TEXT,
            item_name TEXT,
            amount INTEGER,
            direction TEXT,
            memo TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS contracts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            party_name TEXT,
            contract_type TEXT,
            start_date TEXT,
            end_date TEXT,
            status TEXT,
            memo TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS schedule_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_date TEXT,
            title TEXT,
            category TEXT,
            owner TEXT,
            memo TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS content_calendar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content_date TEXT,
            channel TEXT,
            content_type TEXT,
            title TEXT,
            status TEXT,
            memo TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS meeting_notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            meeting_date TEXT,
            title TEXT,
            attendees TEXT,
            decisions TEXT,
            content TEXT
        )
    """)

    conn.commit()
    conn.close()


# ---------- 공통 유틸 ----------
def run_query(query, params=()):
    conn = get_conn()
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df


def execute(query, params=()):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(query, params)
    conn.commit()
    last_id = cur.lastrowid
    conn.close()
    return last_id


def delete_row(table, row_id):
    execute(f"DELETE FROM {table} WHERE id = ?", (row_id,))


# ---------- Trainees ----------
def add_trainee(data: dict):
    return execute(
        """INSERT INTO trainees
        (name, birth_date, gender, part, join_date, status, phone, guardian_contact, memo)
        VALUES (?,?,?,?,?,?,?,?,?)""",
        (data["name"], data["birth_date"], data["gender"], data["part"],
         data["join_date"], data["status"], data["phone"],
         data["guardian_contact"], data["memo"])
    )


def get_trainees():
    return run_query("SELECT * FROM trainees ORDER BY id DESC")


def add_evaluation(data: dict):
    return execute(
        """INSERT INTO evaluations
        (trainee_id, eval_date, vocal_score, dance_score, rap_score, attitude_score, memo)
        VALUES (?,?,?,?,?,?,?)""",
        (data["trainee_id"], data["eval_date"], data["vocal_score"],
         data["dance_score"], data["rap_score"], data["attitude_score"], data["memo"])
    )


def get_evaluations(trainee_id=None):
    if trainee_id:
        return run_query("SELECT * FROM evaluations WHERE trainee_id = ? ORDER BY eval_date DESC", (trainee_id,))
    return run_query("""
        SELECT e.*, t.name as trainee_name FROM evaluations e
        JOIN trainees t ON e.trainee_id = t.id
        ORDER BY e.eval_date DESC
    """)


# ---------- Training Sessions ----------
def add_session(data: dict):
    return execute(
        """INSERT INTO training_sessions
        (session_date, start_time, end_time, category, trainer, room, participants, memo)
        VALUES (?,?,?,?,?,?,?,?)""",
        (data["session_date"], data["start_time"], data["end_time"], data["category"],
         data["trainer"], data["room"], data["participants"], data["memo"])
    )


def get_sessions():
    return run_query("SELECT * FROM training_sessions ORDER BY session_date DESC, start_time ASC")


# ---------- Budget ----------
def add_budget_item(data: dict):
    return execute(
        """INSERT INTO budget_items (item_date, category, item_name, amount, direction, memo)
        VALUES (?,?,?,?,?,?)""",
        (data["item_date"], data["category"], data["item_name"], data["amount"],
         data["direction"], data["memo"])
    )


def get_budget_items():
    return run_query("SELECT * FROM budget_items ORDER BY item_date DESC")


# ---------- Contracts ----------
def add_contract(data: dict):
    return execute(
        """INSERT INTO contracts (party_name, contract_type, start_date, end_date, status, memo)
        VALUES (?,?,?,?,?,?)""",
        (data["party_name"], data["contract_type"], data["start_date"], data["end_date"],
         data["status"], data["memo"])
    )


def get_contracts():
    return run_query("SELECT * FROM contracts ORDER BY start_date DESC")


# ---------- Schedule ----------
def add_schedule_event(data: dict):
    return execute(
        """INSERT INTO schedule_events (event_date, title, category, owner, memo)
        VALUES (?,?,?,?,?)""",
        (data["event_date"], data["title"], data["category"], data["owner"], data["memo"])
    )


def get_schedule_events():
    return run_query("SELECT * FROM schedule_events ORDER BY event_date ASC")


# ---------- Content Calendar ----------
def add_content(data: dict):
    return execute(
        """INSERT INTO content_calendar (content_date, channel, content_type, title, status, memo)
        VALUES (?,?,?,?,?,?)""",
        (data["content_date"], data["channel"], data["content_type"], data["title"],
         data["status"], data["memo"])
    )


def get_content_calendar():
    return run_query("SELECT * FROM content_calendar ORDER BY content_date ASC")


# ---------- Meeting Notes ----------
def add_meeting_note(data: dict):
    return execute(
        """INSERT INTO meeting_notes (meeting_date, title, attendees, decisions, content)
        VALUES (?,?,?,?,?)""",
        (data["meeting_date"], data["title"], data["attendees"], data["decisions"], data["content"])
    )


def get_meeting_notes():
    return run_query("SELECT * FROM meeting_notes ORDER BY meeting_date DESC")
