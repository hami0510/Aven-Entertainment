import streamlit as st
import pandas as pd
from datetime import date
import db
from style import apply_style, page_header, sidebar_brand, section_title

st.set_page_config(page_title="소속가수 관리", page_icon="🌟", layout="wide")
db.init_db()
apply_style()
sidebar_brand()

page_header("🌟", "소속가수 관리", "데뷔 아티스트 프로필 및 활동 상태 관리")

tab1, tab2 = st.tabs(["소속가수 목록", "소속가수 등록"])

# ---------------- 목록 ----------------
with tab1:
    artists = db.get_artists()
    if artists.empty:
        st.info("등록된 소속가수가 없습니다. '소속가수 등록' 탭에서 추가해주세요.")
    else:
        c1, c2 = st.columns(2)
        with c1:
            status_filter = st.multiselect(
                "상태 필터", options=artists["status"].unique().tolist(),
                default=artists["status"].unique().tolist()
            )
        with c2:
            group_filter = st.multiselect(
                "그룹 필터", options=artists["group_name"].dropna().unique().tolist(),
                default=artists["group_name"].dropna().unique().tolist()
            )
        filtered = artists[
            artists["status"].isin(status_filter)
            & (artists["group_name"].isin(group_filter) | artists["group_name"].isna())
        ]

        m1, m2, m3 = st.columns(3)
        m1.metric("전체 소속가수", f"{len(artists)}명")
        m2.metric("활동중", f"{len(artists[artists['status'] == '활동중'])}명")
        m3.metric("그룹 수", f"{artists['group_name'].dropna().nunique()}개")

        st.dataframe(
            filtered[["id", "name", "group_name", "part", "debut_date", "status", "phone", "sns_instagram", "memo"]].rename(
                columns={
                    "id": "ID", "name": "이름", "group_name": "그룹명", "part": "파트",
                    "debut_date": "데뷔일", "status": "상태", "phone": "연락처",
                    "sns_instagram": "인스타그램", "memo": "메모"
                }
            ),
            use_container_width=True,
            hide_index=True,
        )

        st.markdown("---")
        section_title("🔄", "상태 변경")
        c1, c2 = st.columns(2)
        with c1:
            target_id = st.number_input("소속가수 ID", min_value=0, step=1, key="artist_status_id")
        with c2:
            new_status = st.selectbox("변경할 상태", ["활동중", "휴식", "계약종료", "탈퇴"], key="artist_status_new")
        if st.button("상태 변경 적용"):
            if target_id > 0:
                db.update_artist_status(int(target_id), new_status)
                st.success(f"ID {target_id} 소속가수 상태를 '{new_status}'로 변경했습니다.")
                st.rerun()

        st.markdown("---")
        section_title("🗑", "소속가수 삭제")
        del_id = st.number_input("삭제할 소속가수 ID", min_value=0, step=1, key="del_artist")
        if st.button("삭제", type="secondary"):
            if del_id > 0:
                db.delete_row("artists", del_id)
                st.success(f"ID {del_id} 소속가수를 삭제했습니다.")
                st.rerun()

# ---------------- 등록 ----------------
with tab2:
    st.subheader("신규 소속가수 등록")

    trainees = db.get_trainees()
    debuted_trainees = trainees[trainees["status"].isin(["데뷔", "데뷔조"])] if not trainees.empty else trainees

    prefill = {}
    if not debuted_trainees.empty:
        st.caption("💡 데뷔 처리된 연습생 정보를 불러와 바로 등록할 수 있습니다.")
        pick_options = ["직접 입력"] + (debuted_trainees["name"] + " (ID:" + debuted_trainees["id"].astype(str) + ")").tolist()
        picked = st.selectbox("연습생 목록에서 불러오기", pick_options)
        if picked != "직접 입력":
            picked_id = int(picked.split("ID:")[1].replace(")", ""))
            row = debuted_trainees[debuted_trainees["id"] == picked_id].iloc[0]
            prefill = {
                "name": row["name"], "part": row["part"], "birth_date": row["birth_date"],
                "gender": row["gender"], "phone": row["phone"], "trainee_id": picked_id
            }

    with st.form("add_artist_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            name = st.text_input("이름 *", value=prefill.get("name", ""))
            group_name = st.text_input("소속 그룹명 (없으면 솔로)")
            part = st.selectbox(
                "파트", ["보컬", "댄스", "랩", "비주얼/올라운더", "미정"],
                index=["보컬", "댄스", "랩", "비주얼/올라운더", "미정"].index(prefill["part"]) if prefill.get("part") in ["보컬", "댄스", "랩", "비주얼/올라운더", "미정"] else 0
            )
        with c2:
            birth_date = st.date_input(
                "생년월일",
                value=date.fromisoformat(prefill["birth_date"]) if prefill.get("birth_date") else date(2000, 1, 1)
            )
            gender = st.selectbox("성별", ["여", "남"], index=(0 if prefill.get("gender", "여") == "여" else 1))
            debut_date = st.date_input("데뷔일", value=date.today())
        with c3:
            status = st.selectbox("상태", ["활동중", "휴식", "계약종료", "탈퇴"])
            phone = st.text_input("연락처", value=prefill.get("phone", ""))
            sns_instagram = st.text_input("인스타그램 계정 (예: @aiven.official)")

        memo = st.text_area("메모")

        if st.form_submit_button("등록", type="primary"):
            if not name:
                st.error("이름은 필수입니다.")
            else:
                db.add_artist({
                    "name": name,
                    "group_name": group_name,
                    "part": part,
                    "birth_date": birth_date.isoformat(),
                    "gender": gender,
                    "debut_date": debut_date.isoformat(),
                    "status": status,
                    "phone": phone,
                    "sns_instagram": sns_instagram,
                    "trainee_id": prefill.get("trainee_id"),
                    "memo": memo,
                })
                st.success(f"{name} 소속가수가 등록되었습니다.")
                st.rerun()

    st.caption("⚠️ 미성년 소속가수의 콘텐츠·홍보·스케줄 관련 사항은 청소년 보호 기준을 항상 확인해주세요.")
