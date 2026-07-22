import streamlit as st
from datetime import date
import db
from style import apply_style, page_header, sidebar_brand

st.set_page_config(page_title="보고서/회의록", page_icon="📝", layout="wide")
db.init_db()
apply_style()
sidebar_brand()

page_header("📝", "보고서 · 회의록", "회의록 작성 및 핵심 결정사항 관리")
st.title("📝 보고서 · 회의록")

tab1, tab2 = st.tabs(["회의록 목록", "회의록 작성"])

with tab1:
    notes = db.get_meeting_notes()
    if notes.empty:
        st.info("작성된 회의록이 없습니다.")
    else:
        for _, row in notes.iterrows():
            with st.expander(f"{row['meeting_date']} · {row['title']}"):
                st.markdown(f"**핵심 결정사항**\n\n{row['decisions']}")
                st.markdown(f"**참석자**: {row['attendees']}")
                st.markdown(f"**상세 내용**\n\n{row['content']}")

with tab2:
    st.subheader("신규 회의록 작성")
    with st.form("add_meeting_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            meeting_date = st.date_input("회의 날짜", value=date.today())
        with c2:
            title = st.text_input("회의 제목")

        attendees = st.text_input("참석자 (쉼표로 구분)")
        decisions = st.text_area("핵심 결정사항 (요약, 상단 배치)", height=100)
        content = st.text_area("상세 내용", height=200)

        if st.form_submit_button("저장", type="primary"):
            db.add_meeting_note({
                "meeting_date": meeting_date.isoformat(), "title": title, "attendees": attendees,
                "decisions": decisions, "content": content
            })
            st.success("회의록이 저장되었습니다.")
            st.rerun()
