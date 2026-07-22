import streamlit as st
import pandas as pd
from datetime import date
import db

st.set_page_config(page_title="경영관리", page_icon="💼", layout="wide")
db.init_db()

st.title("💼 경영관리 (재무·계약·일정·공연·정산)")

tab_budget, tab_contract, tab_schedule, tab_performance, tab_settlement = st.tabs(
    ["예산/재무", "계약 관리", "일정 관리", "공연 관리", "정산 관리"]
)

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

# ================= 공연 관리 =================
with tab_performance:
    st.subheader("공연 현황")
    performances = db.get_performances()
    trainees = db.get_trainees()

    if not performances.empty:
        c1, c2 = st.columns(2)
        with c1:
            status_filter_p = st.multiselect(
                "상태 필터", options=performances["status"].unique().tolist(),
                default=performances["status"].unique().tolist(), key="perf_status_filter"
            )
        with c2:
            artist_filter = st.multiselect(
                "아티스트 필터", options=performances["artist_name"].unique().tolist(),
                default=performances["artist_name"].unique().tolist(), key="perf_artist_filter"
            )
        filtered_p = performances[
            performances["status"].isin(status_filter_p) & performances["artist_name"].isin(artist_filter)
        ]

        total_fee = filtered_p["gross_fee"].sum() if not filtered_p.empty else 0
        m1, m2, m3 = st.columns(3)
        m1.metric("조회된 공연 수", f"{len(filtered_p)}건")
        m2.metric("예정 공연", f"{len(filtered_p[filtered_p['status'] == '예정'])}건")
        m3.metric("총 개런티(수익) 합계", f"{total_fee:,.0f}원")

        st.dataframe(
            filtered_p[["id", "event_date", "title", "artist_name", "venue", "category", "status", "gross_fee", "memo"]].rename(
                columns={
                    "id": "ID", "event_date": "공연일", "title": "공연명", "artist_name": "아티스트",
                    "venue": "장소", "category": "구분", "status": "상태", "gross_fee": "개런티(원)", "memo": "메모"
                }
            ),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("등록된 공연이 없습니다. 아래에서 추가해주세요.")

    st.markdown("---")
    st.subheader("공연 등록")
    with st.form("add_performance_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            event_date_p = st.date_input("공연일", value=date.today(), key="p_date")
            title_p = st.text_input("공연명")
        with c2:
            if not trainees.empty:
                artist_options = trainees["name"].tolist() + ["직접 입력"]
                artist_choice = st.selectbox("아티스트", artist_options)
                if artist_choice == "직접 입력":
                    artist_name = st.text_input("아티스트명 입력")
                else:
                    artist_name = artist_choice
            else:
                artist_name = st.text_input("아티스트명 입력")
            venue = st.text_input("공연 장소")
        with c3:
            category_p = st.selectbox("공연 유형", ["단독 공연", "페스티벌", "행사/축제", "방송 출연", "팬미팅", "기타"])
            status_p = st.selectbox("상태", ["예정", "확정", "완료", "취소"])
            gross_fee = st.number_input("개런티/공연 수익(원)", min_value=0, step=100000)
        memo_p = st.text_area("메모", key="p_memo")

        if st.form_submit_button("공연 등록", type="primary"):
            if not title_p or not artist_name:
                st.error("공연명과 아티스트명은 필수입니다.")
            else:
                db.add_performance({
                    "event_date": event_date_p.isoformat(), "title": title_p, "artist_name": artist_name,
                    "venue": venue, "category": category_p, "status": status_p,
                    "gross_fee": int(gross_fee), "memo": memo_p
                })
                st.success("공연이 등록되었습니다.")
                st.rerun()

# ================= 정산 관리 =================
with tab_settlement:
    st.subheader("정산 현황")
    settlements = db.get_settlements()
    performances = db.get_performances()

    if not settlements.empty:
        pending = settlements[settlements["settlement_status"] == "미정산"]
        m1, m2, m3 = st.columns(3)
        m1.metric("전체 정산 건수", f"{len(settlements)}건")
        m2.metric("미정산 건수", f"{len(pending)}건")
        m3.metric("아티스트 정산 총액", f"{settlements['artist_amount'].sum():,.0f}원")

        st.dataframe(
            settlements[[
                "id", "settlement_date", "performance_title", "artist_name", "gross_revenue",
                "expenses", "company_rate", "artist_rate", "company_amount", "artist_amount", "settlement_status", "memo"
            ]].rename(columns={
                "id": "ID", "settlement_date": "정산일", "performance_title": "공연명", "artist_name": "아티스트",
                "gross_revenue": "총 수익", "expenses": "공제(경비)", "company_rate": "회사 비율(%)",
                "artist_rate": "아티스트 비율(%)", "company_amount": "회사 정산액", "artist_amount": "아티스트 정산액",
                "settlement_status": "상태", "memo": "메모"
            }),
            use_container_width=True,
            hide_index=True,
        )

        st.markdown("##### 정산 상태 변경")
        c1, c2 = st.columns(2)
        with c1:
            target_id = st.number_input("정산 ID", min_value=0, step=1, key="settle_status_id")
        with c2:
            new_status = st.selectbox("변경할 상태", ["미정산", "정산완료"], key="settle_status_new")
        if st.button("상태 변경 적용"):
            if target_id > 0:
                db.update_settlement_status(int(target_id), new_status)
                st.success(f"ID {target_id} 정산 상태를 '{new_status}'로 변경했습니다.")
                st.rerun()
    else:
        st.info("등록된 정산 내역이 없습니다. 아래에서 공연을 선택해 정산을 등록해주세요.")

    st.markdown("---")
    st.subheader("정산 등록")

    if performances.empty:
        st.warning("먼저 '공연 관리' 탭에서 공연을 등록해주세요.")
    else:
        perf_map = dict(
            zip(
                performances["event_date"] + " · " + performances["title"] + " (" + performances["artist_name"] + ")",
                performances["id"],
            )
        )
        selected_perf_label = st.selectbox("정산할 공연 선택", list(perf_map.keys()))
        selected_perf_id = int(perf_map[selected_perf_label])
        selected_perf_row = performances[performances["id"] == selected_perf_id].iloc[0]

        with st.form("add_settlement_form", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            with c1:
                settlement_date = st.date_input("정산일", value=date.today(), key="st_date")
                gross_revenue = st.number_input(
                    "총 정산 대상 수익(원)", min_value=0, step=100000,
                    value=int(selected_perf_row["gross_fee"]) if selected_perf_row["gross_fee"] else 0
                )
            with c2:
                expenses = st.number_input("공제(경비, 원)", min_value=0, step=10000)
                company_rate = st.number_input("회사 분배 비율(%)", min_value=0.0, max_value=100.0, value=30.0, step=1.0)
            with c3:
                artist_rate = st.number_input("아티스트 분배 비율(%)", min_value=0.0, max_value=100.0, value=70.0, step=1.0)
                settlement_status_new = st.selectbox("정산 상태", ["미정산", "정산완료"], key="new_settle_status")

            memo_s = st.text_area("메모", key="st_memo")

            net_amount = max(gross_revenue - expenses, 0)
            company_amount = round(net_amount * company_rate / 100)
            artist_amount = round(net_amount * artist_rate / 100)

            st.caption(
                f"👉 공제 후 정산 대상액: **{net_amount:,.0f}원** "
                f"→ 회사 **{company_amount:,.0f}원** / 아티스트 **{artist_amount:,.0f}원** (자동 계산 미리보기)"
            )
            if round(company_rate + artist_rate, 1) != 100.0:
                st.warning("회사 비율 + 아티스트 비율의 합이 100%가 아닙니다. 확인해주세요.")

            if st.form_submit_button("정산 등록", type="primary"):
                db.add_settlement({
                    "performance_id": selected_perf_id,
                    "settlement_date": settlement_date.isoformat(),
                    "gross_revenue": int(gross_revenue),
                    "expenses": int(expenses),
                    "company_rate": company_rate,
                    "artist_rate": artist_rate,
                    "company_amount": int(company_amount),
                    "artist_amount": int(artist_amount),
                    "settlement_status": settlement_status_new,
                    "memo": memo_s,
                })
                st.success("정산 내역이 등록되었습니다.")
                st.rerun()

    st.caption("⚠️ 본 정산 내역은 관리·기록용 도구입니다. 실제 세금계산서 발행, 원천징수, 세무 신고는 세무사 확인을 거쳐주세요.")
