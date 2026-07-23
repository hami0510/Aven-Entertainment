"""
Aiven Entertainment 관리 시스템 - 공통 스타일 모듈
브랜드 로고(블랙&화이트, 볼드 산세리프, 미니멀)를 기준으로 한 모노크롬 톤앤매너.
모든 페이지 상단에서 apply_style() / page_header() / kpi_cards() 를 불러와 사용합니다.
"""
import streamlit as st
import pandas as pd
from datetime import date, timedelta
import db

INK = "#0D0D0D"
MUTED = "#767676"
FAINT = "#ADADAD"
BG_SOFT = "#FAFAFA"
BORDER = "#111111"
BORDER_SOFT = "#E4E4E4"
ALERT = "#D64545"

ACCENTS = {
    "ink": INK,
    "alert": ALERT,
}

# 사이드바 하단에 표시할 SNS 계정. 계정별로 그룹지어 표시됩니다.
SIDEBAR_ACCOUNTS = [
    {
        "name": "Aiven Official",
        "links": [
            {"icon": "📷", "label": "Instagram", "url": "https://www.instagram.com/aiven.official"},
            {"icon": "🎵", "label": "TikTok", "url": "https://www.tiktok.com/@aiven.official"},
            {"icon": "▶️", "label": "YouTube", "url": "https://youtube.com/@aivenent"},
            {"icon": "✕", "label": "X", "url": "https://x.com/aivenent"},
        ],
    },
    {
        "name": "Hytes",
        "links": [
            {"icon": "📷", "label": "Instagram", "url": "https://www.instagram.com/official.hytes"},
            {"icon": "🎵", "label": "TikTok", "url": "https://www.tiktok.com/@hytes.official"},
            {"icon": "▶️", "label": "YouTube", "url": "https://youtube.com/@hytesofficial"},
            {"icon": "✕", "label": "X", "url": "https://x.com/hytesofficial"},
        ],
    },
    {
        "name": "리채",
        "links": [
            {"icon": "📷", "label": "Instagram", "url": "https://www.instagram.com/leechaeisasa"},
            {"icon": "▶️", "label": "YouTube", "url": "https://www.youtube.com/@leechaezip"},
            {"icon": "🎵", "label": "TikTok", "url": "https://www.tiktok.com/@leechae__official"},
        ],
    },
]


def apply_style():
    css = f"""
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@500;600;700;800;900&family=Noto+Sans+KR:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
    <style>
        html, body, [class*="css"] {{
            font-family: 'Inter', 'Noto Sans KR', sans-serif;
        }}
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}

        [data-testid="stSidebar"] {{
            background-color: {BG_SOFT};
            border-right: 1px solid {BORDER_SOFT};
        }}
        [data-testid="stSidebarNav"] li a {{
            border-radius: 6px;
            font-weight: 500;
            color: {INK};
        }}
        [data-testid="stSidebarNav"] li a:hover {{
            background-color: #EFEFEF;
        }}
        [data-testid="stSidebarNav"] li a[aria-current="page"] {{
            background-color: {INK} !important;
            font-weight: 700;
        }}
        [data-testid="stSidebarNav"] li a[aria-current="page"],
        [data-testid="stSidebarNav"] li a[aria-current="page"] span,
        [data-testid="stSidebarNav"] li a[aria-current="page"] p,
        [data-testid="stSidebarNav"] li a[aria-current="page"] * {{
            color: #FFFFFF !important;
        }}

        /* ---------- 헤더 ---------- */
        .aven-header {{
            display: flex; align-items: center; gap: 14px;
            padding: 20px 24px;
            border-radius: 10px;
            background: {INK};
            color: white; margin-bottom: 24px;
        }}
        .aven-header .icon {{ font-size: 26px; line-height: 1; }}
        .aven-header .title {{ font-size: 20px; font-weight: 800; margin: 0; letter-spacing: 0.2px; }}
        .aven-header .subtitle {{ font-size: 12.5px; color: #B8B8B8; margin: 3px 0 0 0; }}

        /* ---------- KPI 카드 ---------- */
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
            gap: 14px;
            margin-bottom: 10px;
        }}
        .kpi-card {{
            position: relative;
            background: white;
            border: 1px solid {BORDER_SOFT};
            border-radius: 8px;
            padding: 18px 18px 16px 18px;
            overflow: hidden;
        }}
        .kpi-card::before {{
            content: "";
            position: absolute; top: 0; left: 0; right: 0; height: 3px;
            background: var(--accent);
        }}
        .kpi-card .kpi-label {{
            font-size: 11px; letter-spacing: 0.6px; text-transform: uppercase;
            color: {MUTED}; font-weight: 700;
            display: flex; align-items: center; gap: 6px; margin-bottom: 10px;
        }}
        .kpi-card .kpi-value {{
            font-size: 25px; font-weight: 900; color: {INK};
        }}
        .kpi-card .kpi-sub {{
            font-size: 11px; color: {FAINT}; margin-top: 5px;
        }}

        /* ---------- 섹션 타이틀 ---------- */
        .section-title {{
            font-size: 15px; font-weight: 800; color: {INK};
            margin: 10px 0 10px 0; display: flex; align-items: center; gap: 8px;
            text-transform: uppercase; letter-spacing: 0.4px;
        }}

        .aven-badge {{
            display: inline-block; padding: 2px 10px; border-radius: 999px;
            font-size: 11px; font-weight: 700;
        }}

        /* ---------- 폼 ---------- */
        div[data-testid="stForm"] {{
            border: 1px solid {BORDER_SOFT};
            border-radius: 10px;
            padding: 18px 20px 6px 20px;
            background: #FCFCFC;
        }}

        button[kind="primary"] {{
            border-radius: 6px !important;
            background-color: {INK} !important;
            border: 1px solid {INK} !important;
        }}
        button[kind="primary"]:hover {{
            background-color: #2B2B2B !important;
        }}

        hr {{ border-color: {BORDER_SOFT} !important; }}

        /* ---------- 캘린더 ---------- */
        .cal-nav-title {{
            text-align: center; font-weight: 800; font-size: 16px; color: {INK};
            padding-top: 4px;
        }}
        .cal-grid {{
            display: grid;
            grid-template-columns: repeat(7, 1fr);
            gap: 4px;
            margin-top: 8px;
        }}
        .cal-head {{
            text-align: center; font-size: 11.5px; font-weight: 700; color: {MUTED};
            padding-bottom: 4px; text-transform: uppercase; letter-spacing: 0.4px;
        }}
        .cal-head-sun {{ color: {ALERT}; }}
        .cal-cell {{
            min-height: 78px;
            border: 1px solid {BORDER_SOFT};
            border-radius: 6px;
            padding: 4px 5px;
            background: white;
        }}
        .cal-empty {{ background: #FAFAFA; border-color: #F0F0F0; }}
        .cal-today {{ border: 1.5px solid {INK}; background: #F7F7F7; }}
        .cal-daynum {{ font-size: 11.5px; font-weight: 700; color: {INK}; margin-bottom: 3px; }}
        .cal-daynum-sun {{ color: {ALERT}; }}
        .cal-event {{
            font-size: 10px; color: {INK}; background: #F0F0F0; border-radius: 4px;
            padding: 1px 4px; margin-bottom: 2px; overflow: hidden; text-overflow: ellipsis;
            white-space: nowrap;
        }}
        .cal-more {{ font-size: 9.5px; color: {MUTED}; }}

        /* 오늘 날짜 버튼: 선택 여부와 무관하게 항상 굵은 테두리로 강조 */
        .st-key-cal_today_btn button,
        button.st-key-cal_today_btn {{
            border: 2px solid {INK} !important;
            font-weight: 800 !important;
        }}
    </style>
    """
    # 줄바꿈이 있으면 마크다운이 코드블록/일반 텍스트로 오인할 수 있어
    # 완전히 한 줄로 압축해서 렌더링합니다 (CSS는 줄바꿈과 무관하게 동작).
    css = " ".join(line.strip() for line in css.split("\n") if line.strip())
    st.markdown(css, unsafe_allow_html=True)


def month_calendar(events_by_date: dict, year: int, month: int):
    """
    events_by_date: {'2026-07-23': [('🗓️', '제목1'), ('🎤', '제목2')], ...}
    해당 월의 달력을 그리드 형태로 렌더링합니다.
    """
    import calendar as _cal
    from datetime import date as _date

    cal = _cal.Calendar(firstweekday=6)  # 일요일 시작
    weeks = cal.monthdayscalendar(year, month)
    days_kr = ["일", "월", "화", "수", "목", "금", "토"]

    html = '<div class="cal-grid">'
    for i, d in enumerate(days_kr):
        cls = "cal-head cal-head-sun" if i == 0 else "cal-head"
        html += f'<div class="{cls}">{d}</div>'

    today = _date.today()
    for week in weeks:
        for i, day in enumerate(week):
            if day == 0:
                html += '<div class="cal-cell cal-empty"></div>'
                continue
            d_obj = _date(year, month, day)
            is_today = d_obj == today
            cell_cls = "cal-cell" + (" cal-today" if is_today else "")
            num_cls = "cal-daynum" + (" cal-daynum-sun" if i == 0 else "")
            evts = events_by_date.get(d_obj.isoformat(), [])
            html += f'<div class="{cell_cls}"><div class="{num_cls}">{day}</div>'
            for icon, title in evts[:3]:
                short = title if len(title) <= 8 else title[:8] + "…"
                html += f'<div class="cal-event">{icon} {short}</div>'
            if len(evts) > 3:
                html += f'<div class="cal-more">+{len(evts) - 3}건 더보기</div>'
            html += '</div>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


def page_header(icon: str, title: str, subtitle: str = ""):
    html = (
        '<div class="aven-header">'
        f'<div class="icon">{icon}</div>'
        '<div>'
        f'<p class="title">{title}</p>'
        f'<p class="subtitle">{subtitle}</p>'
        '</div>'
        '</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def kpi_cards(cards):
    """
    cards: [{ "label": str, "value": str, "icon": str, "accent": "ink|alert"(optional, default ink), "sub": str(optional) }, ...]
    """
    html = '<div class="kpi-grid">'
    for c in cards:
        color = ACCENTS.get(c.get("accent", "ink"), INK)
        sub_html = f'<div class="kpi-sub">{c["sub"]}</div>' if c.get("sub") else ""
        html += (
            f'<div class="kpi-card" style="--accent:{color}">'
            f'<div class="kpi-label">{c.get("icon", "")} {c["label"]}</div>'
            f'<div class="kpi-value">{c["value"]}</div>'
            f'{sub_html}'
            '</div>'
        )
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


def section_title(icon: str, text: str):
    st.markdown(f'<div class="section-title">{icon} {text}</div>', unsafe_allow_html=True)


def sidebar_brand():
    st.logo("logo.png", size="large")

    # ---- 배지/오늘 일정/검색에 쓸 데이터 조회 (캐시되어 있어 빠름) ----
    try:
        db.init_db()
        trainees_sb = db.get_trainees()
        artists_sb = db.get_artists()
        contracts_sb = db.get_contracts()
        settlements_sb = db.get_settlements()
        schedule_sb = db.get_schedule_events()
        performances_sb = db.get_performances()
        sessions_sb = db.get_sessions()
    except Exception:
        empty = pd.DataFrame()
        trainees_sb = artists_sb = contracts_sb = settlements_sb = empty
        schedule_sb = performances_sb = sessions_sb = empty

    today_iso = date.today().isoformat()
    soon_iso = (date.today() + timedelta(days=30)).isoformat()

    pending_settle_n = 0
    if not settlements_sb.empty:
        pending_settle_n = len(settlements_sb[settlements_sb["settlement_status"] == "미정산"])

    expiring_contracts_n = 0
    if not contracts_sb.empty:
        expiring_contracts_n = len(contracts_sb[
            (contracts_sb["status"] == "진행중")
            & (contracts_sb["end_date"] >= today_iso)
            & (contracts_sb["end_date"] <= soon_iso)
        ])

    # ---- 1. 알림 배지 ----
    if pending_settle_n > 0 or expiring_contracts_n > 0:
        badge_html = (
            '<div style="margin:14px 4px 4px 4px; padding:10px 12px; border:1px solid #D64545; '
            'border-radius:8px; background:#FDF2F2;">'
            '<div style="font-size:11px; font-weight:800; color:#D64545; margin-bottom:4px;">⚠ 확인 필요</div>'
        )
        if pending_settle_n > 0:
            badge_html += f'<div style="font-size:12px; color:#0D0D0D;">🧾 미정산 {pending_settle_n}건</div>'
        if expiring_contracts_n > 0:
            badge_html += f'<div style="font-size:12px; color:#0D0D0D;">📄 계약 만료 임박(30일 내) {expiring_contracts_n}건</div>'
        badge_html += '</div>'
        st.sidebar.markdown(badge_html, unsafe_allow_html=True)

    # ---- 2. 오늘 일정 미리보기 ----
    today_items = []
    if not schedule_sb.empty:
        for _, r in schedule_sb[schedule_sb["event_date"] == today_iso].iterrows():
            today_items.append(("🗓️", r["title"]))
    if not performances_sb.empty:
        for _, r in performances_sb[performances_sb["event_date"] == today_iso].iterrows():
            today_items.append(("🎤", r["title"]))
    if not sessions_sb.empty:
        for _, r in sessions_sb[sessions_sb["session_date"] == today_iso].iterrows():
            today_items.append(("📅", r.get("category", "트레이닝")))

    today_html = (
        '<div style="margin:10px 4px 4px 4px; padding:10px 12px; border:1px solid #E4E4E4; '
        'border-radius:8px; background:#FCFCFC;">'
        '<div style="font-size:11px; font-weight:800; color:#767676; text-transform:uppercase; '
        'margin-bottom:5px;">📌 오늘 일정</div>'
    )
    if today_items:
        for icon, title in today_items[:3]:
            short = title if len(title) <= 14 else title[:14] + "…"
            today_html += f'<div style="font-size:12px; color:#0D0D0D; margin-bottom:2px;">{icon} {short}</div>'
        if len(today_items) > 3:
            today_html += f'<div style="font-size:11px; color:#ADADAD;">+{len(today_items) - 3}건 더</div>'
    else:
        today_html += '<div style="font-size:12px; color:#ADADAD;">오늘 일정 없음</div>'
    today_html += '</div>'
    st.sidebar.markdown(today_html, unsafe_allow_html=True)

    # ---- 3. 빠른 검색 ----
    st.sidebar.markdown(
        '<div style="margin:12px 4px 2px 4px; font-size:11px; font-weight:800; color:#767676; '
        'text-transform:uppercase;">🔍 빠른 검색</div>',
        unsafe_allow_html=True,
    )
    query = st.sidebar.text_input(
        "이름으로 검색", key="sidebar_quick_search", label_visibility="collapsed",
        placeholder="연습생·소속가수 이름 검색"
    )
    if query:
        results = []
        if not trainees_sb.empty:
            matched = trainees_sb[trainees_sb["name"].str.contains(query, case=False, na=False)]
            for _, r in matched.iterrows():
                results.append(("👤 연습생", r["name"], r["status"]))
        if not artists_sb.empty:
            matched = artists_sb[artists_sb["name"].str.contains(query, case=False, na=False)]
            for _, r in matched.iterrows():
                results.append(("🌟 소속가수", r["name"], r["status"]))
        if results:
            for tag, name, status in results[:6]:
                st.sidebar.caption(f"{tag} · {name} ({status})")
        else:
            st.sidebar.caption("검색 결과가 없습니다.")

    # ---- SNS 계정 ----
    html = '<div style="padding: 14px 4px 4px 4px;">'
    for account in SIDEBAR_ACCOUNTS:
        html += (
            '<div style="margin-bottom:18px;">'
            f'<div style="font-size:12.5px; font-weight:800; letter-spacing:0.4px; color:#767676; '
            f'text-transform:uppercase; margin-bottom:8px;">{account["name"]}</div>'
            '<div style="display:flex; gap:16px;">'
        )
        for link in account["links"]:
            html += (
                f'<a href="{link["url"]}" target="_blank" title="{link["label"]}" '
                'style="text-decoration:none; font-size:26px; line-height:1;">'
                f'{link["icon"]}</a>'
            )
        html += '</div></div>'
    html += '</div>'

    st.sidebar.markdown("---")
    st.sidebar.markdown(html, unsafe_allow_html=True)

    # ---- 4. 데이터 새로고침 ----
    st.sidebar.markdown("---")
    if st.sidebar.button("🔄 데이터 새로고침", key="sidebar_refresh", use_container_width=True):
        db.refresh_cache()
        st.rerun()
