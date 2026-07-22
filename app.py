import streamlit as st
import pandas as pd
from datetime import date, timedelta
import db

st.set_page_config(
    page_title="Aven Entertainment 관리 시스템",
    page_icon="🎤",
    layout="wide",
    initial_sidebar_state="expanded",
)

db.init_db()

st.sidebar.title("🎤 Aven Entertainment")
st.sidebar.caption("경영·육성 통합 관리 시스템")
st.sidebar.markdown("---")
st.sidebar.info("왼쪽 메뉴에서 세부 관리 페이지로 이동하세요.")

st.title("📊 통합 대시보드")
st.caption(f"오늘 날짜: {date.today().strftime('%Y년 %m월 %d일')}")

trainees = db.get_trainees()
sessions = db.get_sessions()
budget = db.get_budget_items()
contracts = db.get_contracts()
schedule = db.get_schedule_events()
content = db.get_content_calendar()

# ---------------- KPI 카드 ----------------
col1, col2, col3, col4 = st.columns(4)

with col1:
    active_trainees = len(trainees[trainees["status"] == "연습생"]) if not trainees.empty else 0
    st.metric("현재 연습생 수", f"{active_trainees}명")

with col2:
    today_str = date.today().isoformat()
    week_later = (date.today() + timedelta(days=7)).isoformat()
    if not sessions.empty:
        upcoming = sessions[(sessions["session_date"] >= today_str) & (sessions["session_date"] <= week_later)]
        st.metric("이번 주 트레이닝 세션", f"{len(upcoming)}건")
    else:
        st.metric("이번 주 트레이닝 세션", "0건")

with col3:
    if not budget.empty:
        income = budget[budget["direction"] == "수입"]["amount"].sum()
        expense = budget[budget["direction"] == "지출"]["amount"].sum()
        net = income - expense
        st.metric("누적 순수익", f"{net:,.0f}원", delta=f"수입 {income:,.0f} / 지출 {expense:,.0f}")
    else:
        st.metric("누적 순수익", "0원")

with col4:
    if not contracts.empty:
        active_contracts = len(contracts[contracts["status"] == "진행중"])
        st.metric("진행 중 계약", f"{active_contracts}건")
    else:
        st.metric("진행 중 계약", "0건")

st.markdown("---")

left, right = st.columns([1.3, 1])

with left:
    st.subheader("📅 다가오는 일정")
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
            st.write("예정된 일정이 없습니다.")
    else:
        st.write("등록된 일정이 없습니다. '경영관리' 페이지에서 일정을 추가해보세요.")

    st.subheader("📢 콘텐츠 발행 예정")
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
            st.write("예정된 콘텐츠가 없습니다.")
    else:
        st.write("등록된 콘텐츠 계획이 없습니다. '콘텐츠·홍보' 페이지에서 추가해보세요.")

with right:
    st.subheader("👥 연습생 현황")
    if not trainees.empty:
        status_counts = trainees["status"].value_counts()
        st.bar_chart(status_counts)
        part_counts = trainees["part"].value_counts()
        st.write("파트별 인원")
        st.dataframe(part_counts.rename("인원"), use_container_width=True)
    else:
        st.write("등록된 연습생이 없습니다. '연습생 관리' 페이지에서 추가해보세요.")

st.markdown("---")
st.caption(
    "⚠️ 본 시스템의 계약·재무 관련 기록은 참고용 정리 도구입니다. "
    "법적 효력이 필요한 최종 계약서는 변호사 검토를, 세무 신고는 세무사 확인을 거쳐야 합니다."
)
