"""
Aiven Entertainment 관리 시스템 - 공통 스타일 모듈
브랜드 로고(블랙&화이트, 볼드 산세리프, 미니멀)를 기준으로 한 모노크롬 톤앤매너.
모든 페이지 상단에서 apply_style() / page_header() / kpi_cards() 를 불러와 사용합니다.
"""
import streamlit as st

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


def apply_style():
    st.markdown(f"""
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
    </style>
    """, unsafe_allow_html=True)


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
    st.sidebar.markdown('<div style="padding: 18px 0 10px 0;">', unsafe_allow_html=True)
    st.sidebar.image("assets/logo.png", width=150)
    st.sidebar.markdown('</div>', unsafe_allow_html=True)
