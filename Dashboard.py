import streamlit as st
import pandas as pd
from datetime import date, timedelta
import db
from style import apply_style, page_header, kpi_cards, section_title, sidebar_brand

st.set_page_config(
    page_title="Aiven Entertainment 관리 시스템",
    page_icon="🎤",
    layout="wide",
    initial_sidebar_state="expanded",
)

db.init_db()
apply_style()

sidebar_brand()
st.sidebar.markdown("---")
st.sidebar.info("왼쪽 메뉴에서 세부 관리 페이지로 이동하세요.")

page_header("📊", "통합 대시보드", f"오늘 날짜: {date.today().strftime('%Y년 %m월 %d일')}")

trainees = db.get_trainees()
sessions = db.get_sessions()
budget = db.get_budget_items()
contracts = db.get_contracts()
schedule = db.get_schedule_events()
content = db.get_content_calendar()
performances = db.get_performances()
settlements = db.get_settlements()

# ---------------- KPI 계산 ----------------
active_trainees = len(trainees[trainees["status"] == "연습생"]) if not trainees.empty else 0

today_str = date.today().isoformat()
week_later = (date.today() + timedelta(days=7)).isoformat()
upcoming_sessions = 0
if not sessions.empty:
    upcoming_sessions = len(
        sessions[(sessions["session_date"] >= today_str) & (sessions["session_date"] <= week_later)]
    )

if not budget.empty:
    income = budget[budget["direction"] == "수입"]["amount"].sum()
    expense = budget[budget["direction"] == "지출"]["amount"].sum()
    net = income - expense
else:
    income = expense = net = 0

active_contracts = len(contracts[contracts["status"] == "진행중"]) if not contracts.empty else 0
upcoming_perf = len(performances[performances["status"].isin(["예정", "확정"])]) if not performances.empty else 0
pending_settle = len(settlements[settlements["settlement_status"] == "미정산"]) if not settlements.empty else 0

kpi_cards([
    {"label": "현재 연습생 수", "value": f"{active_trainees}명", "icon": "👥", "accent": "violet"},
    {"label": "이번 주 트레이닝", "value": f"{upcoming_sessions}건", "icon": "📅", "accent": "blue"},
    {"label": "누적 순수익", "value": f"{net:,.0f}원", "icon": "💰", "accent": "green",
     "sub": f"수입 {income:,.0f} · 지출 {expense:,.0f}"},
    {"label": "진행 중 계약", "value": f"{active_contracts}건", "icon": "📄", "accent": "amber"},
    {"label": "예정 공연", "value": f"{upcoming_perf}건", "icon": "🎤", "accent": "pink"},
    {"label": "미정산 건수", "value": f"{pending_settle}건", "icon": "🧾", "accent": "rose"},
])

st.markdown("<br>", unsafe_allow_html=True)

left, right = st.columns([1.3, 1])

with left:
    section_title("📅", "다가오는 일정")
    if not schedule.empty:
        upcoming_sched = schedule[schedule["event_date"] >= date.today().isoformat()].head(8)
        if not upcoming_sched.empty:
            st.dataframe(
                upcoming_sched[["event_date", "title", "category", "owner"]].rename(
                    columns={"event_date": "날짜", "title": "제목", "category": "구분", "owner": "담당"}
                ),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.caption("예정된 일정이 없습니다.")
    else:
        st.caption("등록된 일정이 없습니다. '경영관리' 페이지에서 일정을 추가해보세요.")

    section_title("📢", "콘텐츠 발행 예정")
    if not content.empty:
        upcoming_content = content[content["content_date"] >= date.today().isoformat()].head(8)
        if not upcoming_content.empty:
            st.dataframe(
                upcoming_content[["content_date", "channel", "title", "status"]].rename(
                    columns={"content_date": "날짜", "channel": "채널", "title": "제목", "status": "상태"}
                ),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.caption("예정된 콘텐츠가 없습니다.")
    else:
        st.caption("등록된 콘텐츠 계획이 없습니다. '콘텐츠·홍보' 페이지에서 추가해보세요.")

with right:
    section_title("👥", "연습생 현황")
    if not trainees.empty:
        status_counts = trainees["status"].value_counts()
        st.bar_chart(status_counts, color="#7C4DFF")
        st.caption("파트별 인원")
        part_counts = trainees["part"].value_counts()
        st.dataframe(part_counts.rename("인원"), use_container_width=True)
    else:
        st.caption("등록된 연습생이 없습니다. '연습생 관리' 페이지에서 추가해보세요.")

st.markdown("---")
st.caption(
    "⚠️ 본 시스템의 계약·재무 관련 기록은 참고용 정리 도구입니다. "
    "법적 효력이 필요한 최종 계약서는 변호사 검토를, 세무 신고는 세무사 확인을 거쳐야 합니다."
)
