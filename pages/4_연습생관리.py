import streamlit as st
import pandas as pd
from datetime import date
import db
from style import apply_style, page_header, sidebar_brand

st.set_page_config(page_title="연습생 관리", page_icon="👥", layout="wide")
db.init_db()
apply_style()
sidebar_brand()

page_header("👥", "연습생 육성·관리", "등록, 목록 관리, 평가 및 성장 추이")

st.title("👥 연습생 육성·관리")

tab1, tab2, tab3 = st.tabs(["연습생 목록", "연습생 등록", "평가 기록"])

# ---------------- 목록 ----------------
with tab1:
    trainees = db.get_trainees()
    if trainees.empty:
        st.info("등록된 연습생이 없습니다. '연습생 등록' 탭에서 추가해주세요.")
    else:
        status_filter = st.multiselect(
            "상태 필터", options=trainees["status"].unique().tolist(),
            default=trainees["status"].unique().tolist()
        )
        filtered = trainees[trainees["status"].isin(status_filter)]
        st.dataframe(
            filtered[["id", "name", "birth_date", "gender", "part", "join_date", "status", "phone", "memo"]].rename(
                columns={
                    "id": "ID", "name": "이름", "birth_date": "생년월일", "gender": "성별",
                    "part": "파트", "join_date": "입사일", "status": "상태",
                    "phone": "연락처", "memo": "메모"
                }
            ),
            use_container_width=True,
            hide_index=True,
        )

        st.markdown("---")
        st.subheader("연습생 삭제")
        del_id = st.number_input("삭제할 연습생 ID", min_value=0, step=1, key="del_trainee")
        if st.button("삭제", type="secondary"):
            if del_id > 0:
                db.delete_row("trainees", del_id)
                st.success(f"ID {del_id} 연습생을 삭제했습니다.")
                st.rerun()

# ---------------- 등록 ----------------
with tab2:
    st.subheader("신규 연습생 등록")
    with st.form("add_trainee_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            name = st.text_input("이름 *")
            birth_date = st.date_input("생년월일", value=date(2008, 1, 1))
            gender = st.selectbox("성별", ["여", "남"])
        with c2:
            part = st.selectbox("담당 파트", ["보컬", "댄스", "랩", "비주얼/올라운더", "미정"])
            join_date = st.date_input("입사(연습생 계약)일", value=date.today())
            status = st.selectbox("상태", ["연습생", "데뷔조", "데뷔", "휴식", "계약종료"])
        with c3:
            phone = st.text_input("본인 연락처")
            guardian_contact = st.text_input("보호자 연락처 (미성년자인 경우 필수)")
            memo = st.text_area("메모", height=68)

        submitted = st.form_submit_button("등록", type="primary")
        if submitted:
            if not name:
                st.error("이름은 필수입니다.")
            else:
                db.add_trainee({
                    "name": name,
                    "birth_date": birth_date.isoformat(),
                    "gender": gender,
                    "part": part,
                    "join_date": join_date.isoformat(),
                    "status": status,
                    "phone": phone,
                    "guardian_contact": guardian_contact,
                    "memo": memo,
                })
                st.success(f"{name} 연습생이 등록되었습니다.")
                st.rerun()

    st.caption("⚠️ 미성년 연습생의 경우 대중문화예술산업발전법 등 관련 법규에 따른 보호 조치(교육시간, 보호자 동의 등)를 별도로 확인해주세요.")

# ---------------- 평가 기록 ----------------
with tab3:
    trainees = db.get_trainees()
    if trainees.empty:
        st.info("먼저 연습생을 등록해주세요.")
    else:
        st.subheader("평가 기록 추가")
        with st.form("add_eval_form", clear_on_submit=True):
            trainee_map = dict(zip(trainees["name"] + " (ID:" + trainees["id"].astype(str) + ")", trainees["id"]))
            selected = st.selectbox("연습생 선택", list(trainee_map.keys()))
            eval_date = st.date_input("평가일", value=date.today())
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                vocal = st.slider("보컬", 0, 100, 70)
            with c2:
                dance = st.slider("댄스", 0, 100, 70)
            with c3:
                rap = st.slider("랩", 0, 100, 70)
            with c4:
                attitude = st.slider("태도/인성", 0, 100, 70)
            eval_memo = st.text_area("평가 메모")

            if st.form_submit_button("평가 등록", type="primary"):
                db.add_evaluation({
                    "trainee_id": int(trainee_map[selected]),
                    "eval_date": eval_date.isoformat(),
                    "vocal_score": vocal,
                    "dance_score": dance,
                    "rap_score": rap,
                    "attitude_score": attitude,
                    "memo": eval_memo,
                })
                st.success("평가 기록이 저장되었습니다.")
                st.rerun()

        st.markdown("---")
        st.subheader("평가 이력")
        evals = db.get_evaluations()
        if evals.empty:
            st.write("평가 기록이 없습니다.")
        else:
            st.dataframe(
                evals[["eval_date", "trainee_name", "vocal_score", "dance_score", "rap_score", "attitude_score", "memo"]].rename(
                    columns={
                        "eval_date": "평가일", "trainee_name": "이름", "vocal_score": "보컬",
                        "dance_score": "댄스", "rap_score": "랩", "attitude_score": "태도", "memo": "메모"
                    }
                ),
                use_container_width=True,
                hide_index=True,
            )

            st.subheader("연습생별 성장 추이")
            pick = st.selectbox("연습생 선택 (그래프)", trainees["name"].tolist())
            pick_id = trainees[trainees["name"] == pick]["id"].iloc[0]
            trend = db.get_evaluations(int(pick_id))
            if not trend.empty:
                trend = trend.sort_values("eval_date")
                chart_df = trend.set_index("eval_date")[["vocal_score", "dance_score", "rap_score", "attitude_score"]]
                chart_df.columns = ["보컬", "댄스", "랩", "태도"]
                st.line_chart(chart_df)
            else:
                st.write("해당 연습생의 평가 기록이 없습니다.")
