import streamlit as st
import pandas as pd
from datetime import date, time
import db
from style import apply_style, page_header, sidebar_brand

st.set_page_config(page_title="트레이닝 스케줄", page_icon="📅", layout="wide")
db.init_db()
apply_style()
sidebar_brand()

page_header("📅", "트레이닝 스케줄 관리", "세션 등록 및 일정 조회")
st.title("📅 트레이닝 스케줄 관리")

tab1, tab2 = st.tabs(["스케줄 목록", "세션 등록"])

with tab1:
    sessions = db.get_sessions()
    if sessions.empty:
        st.info("등록된 트레이닝 세션이 없습니다. '세션 등록' 탭에서 추가해주세요.")
    else:
        c1, c2 = st.columns(2)
        with c1:
            start_filter = st.date_input("시작일", value=date.today())
        with c2:
            category_filter = st.multiselect(
                "카테고리 필터",
                options=sessions["category"].unique().tolist(),
                default=sessions["category"].unique().tolist(),
            )
        filtered = sessions[
            (sessions["session_date"] >= start_filter.isoformat())
            & (sessions["category"].isin(category_filter))
        ]
        st.dataframe(
            filtered[["id", "session_date", "start_time", "end_time", "category", "trainer", "room", "participants", "memo"]].rename(
                columns={
                    "id": "ID", "session_date": "날짜", "start_time": "시작", "end_time": "종료",
                    "category": "구분", "trainer": "강사", "room": "연습실", "participants": "참여 연습생", "memo": "메모"
                }
            ),
            use_container_width=True,
            hide_index=True,
        )

        st.markdown("---")
        del_id = st.number_input("삭제할 세션 ID", min_value=0, step=1)
        if st.button("세션 삭제"):
            if del_id > 0:
                db.delete_row("training_sessions", del_id)
                st.success(f"ID {del_id} 세션을 삭제했습니다.")
                st.rerun()

with tab2:
    st.subheader("신규 트레이닝 세션 등록")
    trainees = db.get_trainees()
    with st.form("add_session_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            session_date = st.date_input("날짜", value=date.today())
            start_t = st.time_input("시작 시간", value=time(14, 0))
        with c2:
            end_t = st.time_input("종료 시간", value=time(16, 0))
            category = st.selectbox("카테고리", ["보컬", "댄스", "랩", "인성교육", "체력/컨디셔닝", "종합/합주", "기타"])
        with c3:
            trainer = st.text_input("담당 강사")
            room = st.text_input("연습실")

        if not trainees.empty:
            participants = st.multiselect("참여 연습생", trainees["name"].tolist())
        else:
            participants = []
            st.caption("등록된 연습생이 없습니다.")

        memo = st.text_area("메모")

        if st.form_submit_button("등록", type="primary"):
            db.add_session({
                "session_date": session_date.isoformat(),
                "start_time": start_t.strftime("%H:%M"),
                "end_time": end_t.strftime("%H:%M"),
                "category": category,
                "trainer": trainer,
                "room": room,
                "participants": ", ".join(participants),
                "memo": memo,
            })
            st.success("트레이닝 세션이 등록되었습니다.")
            st.rerun()
