import streamlit as st
import pandas as pd
from datetime import date
import db
from style import apply_style, page_header, sidebar_brand

st.set_page_config(page_title="콘텐츠·홍보", page_icon="📢", layout="wide")
db.init_db()
apply_style()
sidebar_brand()

page_header("📢", "콘텐츠·홍보 기획 관리", "채널별 콘텐츠 캘린더 관리")
st.title("📢 콘텐츠·홍보 기획 관리")

tab1, tab2 = st.tabs(["콘텐츠 캘린더", "콘텐츠 등록"])

with tab1:
    content = db.get_content_calendar()
    if content.empty:
        st.info("등록된 콘텐츠 계획이 없습니다. '콘텐츠 등록' 탭에서 추가해주세요.")
    else:
        c1, c2 = st.columns(2)
        with c1:
            channel_filter = st.multiselect(
                "채널 필터", options=content["channel"].unique().tolist(),
                default=content["channel"].unique().tolist()
            )
        with c2:
            status_filter = st.multiselect(
                "상태 필터", options=content["status"].unique().tolist(),
                default=content["status"].unique().tolist()
            )
        filtered = content[content["channel"].isin(channel_filter) & content["status"].isin(status_filter)]
        st.dataframe(
            filtered[["content_date", "channel", "content_type", "title", "status", "memo"]].rename(
                columns={"content_date": "발행(예정)일", "channel": "채널", "content_type": "유형", "title": "제목", "status": "상태", "memo": "메모"}
            ),
            use_container_width=True,
            hide_index=True,
        )

        st.write("채널별 콘텐츠 수")
        st.bar_chart(content["channel"].value_counts())

    st.caption("⚠️ 미성년 아티스트/연습생이 포함된 콘텐츠는 청소년 보호 기준(초상권, 과도한 노출·이미지 연출 지양 등)을 항상 확인해주세요.")

with tab2:
    st.subheader("신규 콘텐츠 등록")
    with st.form("add_content_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            content_date = st.date_input("발행(예정)일", value=date.today())
            channel = st.selectbox("채널", ["Instagram", "YouTube", "TikTok", "Weverse/팬카페", "X(트위터)", "보도자료", "기타"])
        with c2:
            content_type = st.selectbox("콘텐츠 유형", ["숏폼", "브이로그", "챌린지", "라이브방송", "화보/포토", "인터뷰", "티저/예고", "보도자료"])
            status = st.selectbox("상태", ["기획중", "제작중", "검수중", "발행예정", "발행완료"])
        with c3:
            title = st.text_input("제목/주제")
        memo = st.text_area("메모(기획 의도, 담당자 등)")

        if st.form_submit_button("등록", type="primary"):
            db.add_content({
                "content_date": content_date.isoformat(), "channel": channel, "content_type": content_type,
                "title": title, "status": status, "memo": memo
            })
            st.success("콘텐츠 계획이 등록되었습니다.")
            st.rerun()
