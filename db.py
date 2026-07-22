"""
Aiven Entertainment 관리 시스템 - 데이터베이스 레이어
Streamlit Secrets에 DB_URL(PostgreSQL/Supabase)이 있으면 영구 DB를 사용하고,
없으면 로컬 SQLite(data/aven.db)로 동작합니다. 앱 최초 실행 시 테이블을 자동 생성합니다.
"""
import os
import pandas as pd
from sqlalchemy import create_engine, text

try:
    import streamlit as st
    _DB_URL = st.secrets.get("DB_URL", None)
except Exception:
    _DB_URL = None

if _DB_URL:
    engine = create_engine(_DB_URL, pool_pre_ping=True)
    IS_PG = True
else:
    _base = os.path.dirname(__file__)
    os.makedirs(os.path.join(_base, "data"), exist_ok=True)
    engine = create_engine(f"sqlite:///{os.path.join(_base, 'data', 'aven.db')}")
    IS_PG = False

_ID = "SERIAL PRIMARY KEY" if IS_PG else "INTEGER PRIMARY KEY AUTOINCREMENT"

_initialized = False


def init_db():
    global _initialized
    if _initialized:
        return
    ddl = [
        f"""CREATE TABLE IF NOT EXISTS trainees (
            id {_ID},
            name TEXT NOT NULL,
            birth_date TEXT,
            gender TEXT,
            part TEXT,
            join_date TEXT,
            status TEXT DEFAULT '연습생',
            phone TEXT,
            guardian_contact TEXT,
            memo TEXT
        )""",
        f"""CREATE TABLE IF NOT EXISTS evaluations (
            id {_ID},
            trainee_id INTEGER NOT NULL,
            eval_date TEXT,
            vocal_score INTEGER,
            dance_score INTEGER,
            rap_score INTEGER,
            attitude_score INTEGER,
            memo TEXT
        )""",
        f"""CREATE TABLE IF NOT EXISTS training_sessions (
            id {_ID},
            session_date TEXT,
            start_time TEXT,
            end_time TEXT,
            category TEXT,
            trainer TEXT,
            room TEXT,
            participants TEXT,
            memo TEXT
        )""",
        f"""CREATE TABLE IF NOT EXISTS budget_items (
            id {_ID},
            item_date TEXT,
            category TEXT,
            item_name TEXT,
            amount BIGINT,
            direction TEXT,
            memo TEXT
        )""",
        f"""CREATE TABLE IF NOT EXISTS contracts (
            id {_ID},
            party_name TEXT,
            contract_type TEXT,
            start_date TEXT,
            end_date TEXT,
            status TEXT,
            memo TEXT
        )""",
        f"""CREATE TABLE IF NOT EXISTS schedule_events (
            id {_ID},
            event_date TEXT,
            title TEXT,
            category TEXT,
            owner TEXT,
            memo TEXT
        )""",
        f"""CREATE TABLE IF NOT EXISTS content_calendar (
            id {_ID},
            content_date TEXT,
            channel TEXT,
            content_type TEXT,
            title TEXT,
            status TEXT,
            memo TEXT
        )""",
        f"""CREATE TABLE IF NOT EXISTS meeting_notes (
            id {_ID},
            meeting_date TEXT,
            title TEXT,
            attendees TEXT,
            decisions TEXT,
            content TEXT
        )""",
        f"""CREATE TABLE IF NOT EXISTS performances (
            id {_ID},
            event_date TEXT,
            title TEXT,
            artist_name TEXT,
            venue TEXT,
            category TEXT,
            status TEXT,
            gross_fee BIGINT,
            memo TEXT
        )""",
        f"""CREATE TABLE IF NOT EXISTS settlements (
            id {_ID},
            performance_id INTEGER,
            settlement_date TEXT,
            gross_revenue BIGINT,
            expenses BIGINT,
            company_rate REAL,
            artist_rate REAL,
            company_amount BIGINT,
            artist_amount BIGINT,
            settlement_status TEXT,
            memo TEXT
        )""",
        f"""CREATE TABLE IF NOT EXISTS artists (
            id {_ID},
            name TEXT NOT NULL,
            group_name TEXT,
            part TEXT,
            birth_date TEXT,
            gender TEXT,
            debut_date TEXT,
            status TEXT DEFAULT '활동중',
            phone TEXT,
            sns_instagram TEXT,
            trainee_id INTEGER,
            memo TEXT
        )""",
    ]
    with engine.begin() as conn:
        for stmt in ddl:
            conn.execute(text(stmt))
    _initialized = True


# ---------- 공통 유틸 ----------
def run_query(sql, params=None):
    with engine.connect() as conn:
        return pd.read_sql_query(text(sql), conn, params=params or {})


def execute(sql, params=None):
    with engine.begin() as conn:
        conn.execute(text(sql), params or {})


def insert_returning_id(sql, params):
    if IS_PG:
        with engine.begin() as conn:
            return conn.execute(text(sql + " RETURNING id"), params).scalar()
    else:
        with engine.begin() as conn:
            res = conn.execute(text(sql), params)
            return res.lastrowid


def delete_row(table, row_id):
    allowed = {
        "trainees", "evaluations", "training_sessions", "budget_items", "contracts",
        "schedule_events", "content_calendar", "meeting_notes", "performances",
        "settlements", "artists",
    }
    if table not in allowed:
        raise ValueError("허용되지 않은 테이블입니다.")
    execute(f"DELETE FROM {table} WHERE id = :id", {"id": int(row_id)})


# ---------- Trainees ----------
def add_trainee(data: dict):
    return insert_returning_id(
        """INSERT INTO trainees
        (name, birth_date, gender, part, join_date, status, phone, guardian_contact, memo)
        VALUES (:name, :birth_date, :gender, :part, :join_date, :status, :phone, :guardian_contact, :memo)""",
        data,
    )


def get_trainees():
    return run_query("SELECT * FROM trainees ORDER BY id DESC")


def add_evaluation(data: dict):
    return insert_returning_id(
        """INSERT INTO evaluations
        (trainee_id, eval_date, vocal_score, dance_score, rap_score, attitude_score, memo)
        VALUES (:trainee_id, :eval_date, :vocal_score, :dance_score, :rap_score, :attitude_score, :memo)""",
        data,
    )


def get_evaluations(trainee_id=None):
    if trainee_id:
        return run_query(
            "SELECT * FROM evaluations WHERE trainee_id = :tid ORDER BY eval_date DESC",
            {"tid": int(trainee_id)},
        )
    return run_query("""
        SELECT e.*, t.name as trainee_name FROM evaluations e
        JOIN trainees t ON e.trainee_id = t.id
        ORDER BY e.eval_date DESC
    """)


# ---------- Training Sessions ----------
def add_session(data: dict):
    return insert_returning_id(
        """INSERT INTO training_sessions
        (session_date, start_time, end_time, category, trainer, room, participants, memo)
        VALUES (:session_date, :start_time, :end_time, :category, :trainer, :room, :participants, :memo)""",
        data,
    )


def get_sessions():
    return run_query("SELECT * FROM training_sessions ORDER BY session_date DESC, start_time ASC")


# ---------- Budget ----------
def add_budget_item(data: dict):
    return insert_returning_id(
        """INSERT INTO budget_items (item_date, category, item_name, amount, direction, memo)
        VALUES (:item_date, :category, :item_name, :amount, :direction, :memo)""",
        data,
    )


def get_budget_items():
    return run_query("SELECT * FROM budget_items ORDER BY item_date DESC")


# ---------- Contracts ----------
def add_contract(data: dict):
    return insert_returning_id(
        """INSERT INTO contracts (party_name, contract_type, start_date, end_date, status, memo)
        VALUES (:party_name, :contract_type, :start_date, :end_date, :status, :memo)""",
        data,
    )


def get_contracts():
    return run_query("SELECT * FROM contracts ORDER BY start_date DESC")


# ---------- Schedule ----------
def add_schedule_event(data: dict):
    return insert_returning_id(
        """INSERT INTO schedule_events (event_date, title, category, owner, memo)
        VALUES (:event_date, :title, :category, :owner, :memo)""",
        data,
    )


def get_schedule_events():
    return run_query("SELECT * FROM schedule_events ORDER BY event_date ASC")


# ---------- Content Calendar ----------
def add_content(data: dict):
    return insert_returning_id(
        """INSERT INTO content_calendar (content_date, channel, content_type, title, status, memo)
        VALUES (:content_date, :channel, :content_type, :title, :status, :memo)""",
        data,
    )


def get_content_calendar():
    return run_query("SELECT * FROM content_calendar ORDER BY content_date ASC")


# ---------- Meeting Notes ----------
def add_meeting_note(data: dict):
    return insert_returning_id(
        """INSERT INTO meeting_notes (meeting_date, title, attendees, decisions, content)
        VALUES (:meeting_date, :title, :attendees, :decisions, :content)""",
        data,
    )


def get_meeting_notes():
    return run_query("SELECT * FROM meeting_notes ORDER BY meeting_date DESC")


# ---------- Performances (아티스트 공연) ----------
def add_performance(data: dict):
    return insert_returning_id(
        """INSERT INTO performances
        (event_date, title, artist_name, venue, category, status, gross_fee, memo)
        VALUES (:event_date, :title, :artist_name, :venue, :category, :status, :gross_fee, :memo)""",
        data,
    )


def get_performances():
    return run_query("SELECT * FROM performances ORDER BY event_date DESC")


def update_performance_status(performance_id, status):
    execute(
        "UPDATE performances SET status = :status WHERE id = :id",
        {"status": status, "id": int(performance_id)},
    )


# ---------- Settlements (정산 관리) ----------
def add_settlement(data: dict):
    return insert_returning_id(
        """INSERT INTO settlements
        (performance_id, settlement_date, gross_revenue, expenses, company_rate, artist_rate,
         company_amount, artist_amount, settlement_status, memo)
        VALUES (:performance_id, :settlement_date, :gross_revenue, :expenses, :company_rate, :artist_rate,
         :company_amount, :artist_amount, :settlement_status, :memo)""",
        data,
    )


def get_settlements():
    return run_query("""
        SELECT s.*, p.title as performance_title, p.artist_name, p.event_date
        FROM settlements s
        LEFT JOIN performances p ON s.performance_id = p.id
        ORDER BY s.settlement_date DESC
    """)


def update_settlement_status(settlement_id, status):
    execute(
        "UPDATE settlements SET settlement_status = :status WHERE id = :id",
        {"status": status, "id": int(settlement_id)},
    )


# ---------- Artists (소속가수) ----------
def add_artist(data: dict):
    payload = dict(data)
    payload.setdefault("trainee_id", None)
    return insert_returning_id(
        """INSERT INTO artists
        (name, group_name, part, birth_date, gender, debut_date, status, phone, sns_instagram, trainee_id, memo)
        VALUES (:name, :group_name, :part, :birth_date, :gender, :debut_date, :status, :phone, :sns_instagram, :trainee_id, :memo)""",
        payload,
    )


def get_artists():
    return run_query("SELECT * FROM artists ORDER BY id DESC")


def update_artist_status(artist_id, status):
    execute(
        "UPDATE artists SET status = :status WHERE id = :id",
        {"status": status, "id": int(artist_id)},
    )
