import streamlit as st
import pandas as pd
from datetime import date
import db

st.set_page_config(page_title="경영관리", page_icon="💼", layout="wide")
db.init_db()

st.title("💼 경영관리 (재무·계약·일정)")

tab_budget, tab_contract, tab_schedule = st.tabs(["예산/재무", "계약 관리", "일정 관리"])

# ================= 예산 =================
with tab_budget:
    st.subheader("예산 · 비용 현황")
    budget = db.get_budget_items()

    if not budget.empty:
        income = budget[budget["direction"] == "수입"]["amount"].sum()
        expense = budget[budget["direction"] == "지출"]["amount"].sum()
        c1, c2, c3 = st.columns(3)
        c1.metric("총 수입", f"{income:,.0f}원")
        c2.metric("총 지출", f"{expense:,.0f}원")
        c3.metric("순수익", f"{income - expense:,.0f}원")

        st.dataframe(
            budget[["item_date", "category", "item_name", "direction", "amount", "memo"]].rename(
                columns={"item_date": "날짜", "category": "분류", "item_name": "항목", "direction": "구분", "amount": "금액", "memo": "메모"}
            ),
            use_container_width=True,
            hide_index=True,
        )

        st.write("분류별 지출/수입")
        pivot = budget.pivot_table(index="category", columns="direction", values="amount", aggfunc="sum", fill_value=0)
        st.bar_chart(pivot)
    else:
        st.info("등록된 예산 항목이 없습니다.")

    st.markdown("---")
    st.subheader("항목 추가")
    with st.form("add_budget_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            item_date = st.date_input("날짜", value=date.today(), key="b_date")
            direction = st.selectbox("구분", ["지출", "수입"])
        with c2:
            category = st.selectbox("분류", ["트레이닝/레슨", "숙소/생활", "의상/스타일링", "콘텐츠 제작", "마케팅/홍보", "인건비", "수익(음원/공연 등)", "기타"])
            item_name = st.text_input("항목명")
        with c3:
            amount = st.number_input("금액(원)", min_value=0, step=10000)
            memo = st.text_input("메모")

        if st.form_submit_button("추가", type="primary"):
            db.add_budget_item({
                "item_date": item_date.isoformat(), "category": category, "item_name": item_name,
                "amount": int(amount), "direction": direction, "memo": memo
            })
            st.success("예산 항목이 추가되었습니다.")
            st.rerun()

    st.caption("⚠️ 본 내역은 참고용 관리 도구입니다. 실제 세무 신고·회계 처리는 반드시 세무사 확인을 거쳐주세요.")

# ================= 계약 =================
with tab_contract:
    st.subheader("계약 현황")
    contracts = db.get_contracts()
    if not contracts.empty:
        st.dataframe(
            contracts[["id", "party_name", "contract_type", "start_date", "end_date", "status", "memo"]].rename(
                columns={"id": "ID", "party_name": "계약 대상", "contract_type": "계약 유형", "start_date": "시작일", "end_date": "종료일", "status": "상태", "memo": "메모"}
            ),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("등록된 계약이 없습니다.")

    st.markdown("---")
    st.subheader("계약 추가")
    with st.form("add_contract_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            party_name = st.text_input("계약 대상 (연습생/아티스트명 등)")
            contract_type = st.selectbox("계약 유형", ["전속계약", "연습생 계약", "출연 계약", "협찬/광고 계약", "외주 용역 계약", "기타"])
        with c2:
            start_date = st.date_input("시작일", value=date.today(), key="c_start")
            end_date = st.date_input("종료일", value=date.today().replace(year=date.today().year + 1), key="c_end")
        with c3:
            status = st.selectbox("상태", ["검토중", "진행중", "만료", "해지"])
            memo = st.text_input("메모")

        if st.form_submit_button("추가", type="primary"):
            db.add_contract({
                "party_name": party_name, "contract_type": contract_type,
                "start_date": start_date.isoformat(), "end_date": end_date.isoformat(),
                "status": status, "memo": memo
            })
            st.success("계약이 추가되었습니다.")
            st.rerun()

    st.caption("⚠️ 이 시스템에서 작성하는 계약 정보는 관리용 초안/기록입니다. 법적 효력이 필요한 최종 계약서는 반드시 변호사 등 법률 전문가의 검토를 거쳐야 합니다.")

# ================= 일정 =================
with tab_schedule:
    st.subheader("전사 일정")
    schedule = db.get_schedule_events()
    if not schedule.empty:
        st.dataframe(
            schedule[["event_date", "title", "category", "owner", "memo"]].rename(
                columns={"event_date": "날짜", "title": "제목", "category": "구분", "owner": "담당", "memo": "메모"}
            ),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("등록된 일정이 없습니다.")

    st.markdown("---")
    st.subheader("일정 추가")
    with st.form("add_schedule_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            event_date = st.date_input("날짜", value=date.today(), key="s_date")
        with c2:
            title = st.text_input("제목")
            category = st.selectbox("구분", ["오디션/캐스팅", "데뷔/컴백", "촬영", "공연/행사", "미팅", "기타"])
        with c3:
            owner = st.text_input("담당자")
        memo = st.text_area("메모", key="s_memo")

        if st.form_submit_button("추가", type="primary"):
            db.add_schedule_event({
                "event_date": event_date.isoformat(), "title": title, "category": category,
                "owner": owner, "memo": memo
            })
            st.success("일정이 추가되었습니다.")
            st.rerun()
