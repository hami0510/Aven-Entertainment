import streamlit as st
import pandas as pd
from datetime import date, time, timedelta
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
artists = db.get_artists()

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
    {"label": "현재 연습생 수", "value": f"{active_trainees}명", "icon": "👥", "accent": "ink"},
    {"label": "이번 주 트레이닝", "value": f"{upcoming_sessions}건", "icon": "📅", "accent": "ink"},
    {"label": "누적 순수익", "value": f"{net:,.0f}원", "icon": "💰", "accent": "alert" if net < 0 else "ink",
     "sub": f"수입 {income:,.0f} · 지출 {expense:,.0f}"},
    {"label": "진행 중 계약", "value": f"{active_contracts}건", "icon": "📄", "accent": "ink"},
    {"label": "예정 공연", "value": f"{upcoming_perf}건", "icon": "🎤", "accent": "ink"},
    {"label": "미정산 건수", "value": f"{pending_settle}건", "icon": "🧾", "accent": "alert" if pending_settle > 0 else "ink"},
])

st.markdown("<br>", unsafe_allow_html=True)

# ==================== 캘린더 ====================
section_title("🗓️", "일정 캘린더")
st.caption("날짜를 클릭하면 그 날의 일정을 확인하고 바로 등록할 수 있습니다.")

if "cal_year" not in st.session_state:
    st.session_state.cal_year = date.today().year
    st.session_state.cal_month = date.today().month

nav1, nav2, nav3 = st.columns([1, 6, 1])
with nav1:
    if st.button("◀", key="cal_prev", use_container_width=True):
        m = st.session_state.cal_month - 1
        y = st.session_state.cal_year
        if m < 1:
            m, y = 12, y - 1
        st.session_state.cal_month, st.session_state.cal_year = m, y
        st.rerun()
with nav3:
    if st.button("▶", key="cal_next", use_container_width=True):
        m = st.session_state.cal_month + 1
        y = st.session_state.cal_year
        if m > 12:
            m, y = 1, y + 1
        st.session_state.cal_month, st.session_state.cal_year = m, y
        st.rerun()
with nav2:
    st.markdown(
        f'<div class="cal-nav-title">{st.session_state.cal_year}년 {st.session_state.cal_month}월</div>',
        unsafe_allow_html=True,
    )

# ---------------- 이벤트 취합 ----------------
events_by_date = {}


def _add_event(date_str, icon, title):
    if not date_str:
        return
    events_by_date.setdefault(date_str, []).append((icon, title))


if not schedule.empty:
    for _, r in schedule.iterrows():
        _add_event(r["event_date"], "🗓️", r["title"])

if not performances.empty:
    for _, r in performances.iterrows():
        _add_event(r["event_date"], "🎤", r["title"])

if not sessions.empty:
    for _, r in sessions.iterrows():
        _add_event(r["session_date"], "📅", r.get("category", "트레이닝"))

# 생일 / 데뷔 기념일 (매년 반복되므로, 캘린더에 표시 중인 연도에 맞춰 날짜를 다시 계산)
_cal_year = st.session_state.cal_year


def _add_yearly_event(month_day_source, icon, title):
    if not month_day_source:
        return
    try:
        d = date.fromisoformat(month_day_source)
        key = date(_cal_year, d.month, d.day).isoformat()
        _add_event(key, icon, title)
    except (ValueError, TypeError):
        pass


if not trainees.empty:
    for _, r in trainees.iterrows():
        _add_yearly_event(r.get("birth_date"), "🎂", f"{r['name']} 생일")

if not artists.empty:
    for _, r in artists.iterrows():
        _add_yearly_event(r.get("birth_date"), "🎂", f"{r['name']} 생일")
        debut = r.get("debut_date")
        if debut:
            try:
                years = _cal_year - date.fromisoformat(debut).year
                label = f"{r['name']} 데뷔 {years}주년" if years > 0 else f"{r['name']} 데뷔일"
            except (ValueError, TypeError):
                label = f"{r['name']} 데뷔일"
            _add_yearly_event(debut, "🎉", label)

st.caption("🗓️ 일정 · 🎤 공연 · 📅 트레이닝 · 🎂 생일 · 🎉 데뷔 기념일")

# ---------------- 클릭 가능한 캘린더 그리드 ----------------
import calendar as _cal

cal_obj = _cal.Calendar(firstweekday=6)  # 일요일 시작
weeks = cal_obj.monthdayscalendar(st.session_state.cal_year, st.session_state.cal_month)
days_kr = ["일", "월", "화", "수", "목", "금", "토"]

head_cols = st.columns(7)
for i, d in enumerate(days_kr):
    with head_cols[i]:
        color = "color:#D64545;" if i == 0 else "color:#767676;"
        st.markdown(
            f"<div style='text-align:center;font-size:11.5px;font-weight:700;{color}'>{d}</div>",
            unsafe_allow_html=True,
        )

today = date.today()
for week in weeks:
    row_cols = st.columns(7)
    for i, day in enumerate(week):
        with row_cols[i]:
            if day == 0:
                st.write("")
                continue
            d_obj = date(st.session_state.cal_year, st.session_state.cal_month, day)
            evts = events_by_date.get(d_obj.isoformat(), [])
            is_today = d_obj == today
            is_selected = st.session_state.get("selected_cal_date") == d_obj.isoformat()
            label = f"{day}" + (f" · {len(evts)}건" if evts else "")
            btn_type = "primary" if is_selected else "secondary"
            btn_key = "cal_today_btn" if is_today else f"caldate_{d_obj.isoformat()}"

            clicked = st.button(label, key=btn_key, use_container_width=True, type=btn_type)

            if clicked:
                st.session_state.selected_cal_date = d_obj.isoformat()
                st.rerun()
            if evts:
                first_icon, first_title = evts[0]
                short = first_title if len(first_title) <= 6 else first_title[:6] + "…"
                extra = f" 외{len(evts) - 1}건" if len(evts) > 1 else ""
                st.caption(f"{first_icon} {short}{extra}")

if st.button("오늘로 이동", key="cal_today"):
    st.session_state.cal_year = date.today().year
    st.session_state.cal_month = date.today().month
    st.rerun()

# ---------------- 선택한 날짜: 조회 + 빠른 등록 ----------------
st.markdown("---")
sel = st.session_state.get("selected_cal_date")
if sel:
    sel_date = date.fromisoformat(sel)
    section_title("📌", f"{sel_date.strftime('%Y년 %m월 %d일')} 일정")

    evts = events_by_date.get(sel, [])
    if evts:
        for icon, title in evts:
            st.write(f"{icon} {title}")
    else:
        st.caption("이 날짜에 등록된 일정이 없습니다.")

    with st.expander("➕ 이 날짜에 새 항목 등록", expanded=False):
        add_type = st.radio(
            "등록 유형", ["일정", "공연", "트레이닝 세션"], horizontal=True, key="quickadd_type"
        )

        if add_type == "일정":
            with st.form("quickadd_schedule", clear_on_submit=True):
                c1, c2 = st.columns(2)
                with c1:
                    q_title = st.text_input("제목", key="qa_sched_title")
                    q_category = st.selectbox(
                        "구분", ["오디션/캐스팅", "데뷔/컴백", "촬영", "공연/행사", "미팅", "기타"], key="qa_sched_cat"
                    )
                with c2:
                    q_owner = st.text_input("담당자", key="qa_sched_owner")
                q_memo = st.text_area("메모", key="qa_sched_memo")
                if st.form_submit_button("등록", type="primary"):
                    if not q_title:
                        st.error("제목은 필수입니다.")
                    else:
                        db.add_schedule_event({
                            "event_date": sel, "title": q_title, "category": q_category,
                            "owner": q_owner, "memo": q_memo
                        })
                        st.success("일정이 등록되었습니다.")
                        st.rerun()

        elif add_type == "공연":
            artist_name_list = []
            if not artists.empty:
                artist_name_list += artists["name"].tolist()
            if not trainees.empty:
                artist_name_list += [n for n in trainees["name"].tolist() if n not in artist_name_list]
            artist_options = artist_name_list + ["직접 입력"]

            with st.form("quickadd_perf", clear_on_submit=True):
                c1, c2 = st.columns(2)
                with c1:
                    q_artist_choice = st.selectbox("아티스트", artist_options, key="qa_perf_artist_choice")
                    if q_artist_choice == "직접 입력":
                        q_artist = st.text_input("아티스트명 입력", key="qa_perf_artist_text")
                    else:
                        q_artist = q_artist_choice
                    q_title_p = st.text_input("공연명", key="qa_perf_title")
                with c2:
                    q_venue = st.text_input("장소", key="qa_perf_venue")
                    q_category_p = st.selectbox(
                        "공연 유형", ["단독 공연", "페스티벌", "행사/축제", "방송 출연", "팬미팅", "기타"], key="qa_perf_cat"
                    )
                    q_fee = st.number_input("개런티(원)", min_value=0, step=100000, key="qa_perf_fee")
                if st.form_submit_button("등록", type="primary"):
                    if not q_title_p or not q_artist:
                        st.error("공연명과 아티스트명은 필수입니다.")
                    else:
                        db.add_performance({
                            "event_date": sel, "title": q_title_p, "artist_name": q_artist,
                            "venue": q_venue, "category": q_category_p, "status": "예정",
                            "gross_fee": int(q_fee), "memo": ""
                        })
                        st.success("공연이 등록되었습니다.")
                        st.rerun()

        else:  # 트레이닝 세션
            with st.form("quickadd_session", clear_on_submit=True):
                c1, c2 = st.columns(2)
                with c1:
                    q_start = st.time_input("시작 시간", value=time(14, 0), key="qa_sess_start")
                    q_end = st.time_input("종료 시간", value=time(16, 0), key="qa_sess_end")
                with c2:
                    q_cat_s = st.selectbox(
                        "카테고리", ["보컬", "댄스", "랩", "인성교육", "체력/컨디셔닝", "종합/합주", "기타"], key="qa_sess_cat"
                    )
                    q_trainer = st.text_input("담당 강사", key="qa_sess_trainer")
                q_participants = st.multiselect(
                    "참여 연습생", trainees["name"].tolist() if not trainees.empty else [], key="qa_sess_part"
                )
                if st.form_submit_button("등록", type="primary"):
                    db.add_session({
                        "session_date": sel, "start_time": q_start.strftime("%H:%M"),
                        "end_time": q_end.strftime("%H:%M"), "category": q_cat_s,
                        "trainer": q_trainer, "room": "", "participants": ", ".join(q_participants), "memo": ""
                    })
                    st.success("트레이닝 세션이 등록되었습니다.")
                    st.rerun()

    if st.button("날짜 선택 닫기", key="close_quickadd"):
        del st.session_state["selected_cal_date"]
        st.rerun()

st.markdown("---")

# ==================== 소속가수 / 연습생 / 콘텐츠 3분할 ====================
col1, col2, col3 = st.columns(3)

with col1:
    section_title("🌟", "소속가수 현황")
    if not artists.empty:
        st.metric("전체 소속가수", f"{len(artists)}명")
        status_counts = artists["status"].value_counts()
        st.bar_chart(status_counts, color="#0D0D0D")
        group_count = artists["group_name"].dropna().nunique()
        st.caption(f"활동 그룹 수: {group_count}개")
    else:
        st.caption("등록된 소속가수가 없습니다. '소속가수관리' 페이지에서 추가해보세요.")

with col2:
    section_title("👥", "연습생 현황")
    if not trainees.empty:
        st.metric("전체 연습생", f"{len(trainees)}명")
        status_counts = trainees["status"].value_counts()
        st.bar_chart(status_counts, color="#0D0D0D")
        part_counts = trainees["part"].value_counts()
        st.caption("파트별 인원")
        st.dataframe(part_counts.rename("인원"), use_container_width=True)
    else:
        st.caption("등록된 연습생이 없습니다. '연습생관리' 페이지에서 추가해보세요.")

with col3:
    section_title("📢", "콘텐츠 발행 예정")
    if not content.empty:
        upcoming_content = content[content["content_date"] >= date.today().isoformat()].head(6)
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
        st.caption("채널별 콘텐츠 수")
        st.bar_chart(content["channel"].value_counts(), color="#0D0D0D")
    else:
        st.caption("등록된 콘텐츠 계획이 없습니다. '콘텐츠홍보' 페이지에서 추가해보세요.")

st.markdown("---")
st.caption(
    "⚠️ 본 시스템의 계약·재무 관련 기록은 참고용 정리 도구입니다. "
    "법적 효력이 필요한 최종 계약서는 변호사 검토를, 세무 신고는 세무사 확인을 거쳐야 합니다."
)
