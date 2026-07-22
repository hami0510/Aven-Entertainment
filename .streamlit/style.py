"""
Aven Entertainment 관리 시스템 - 공통 스타일 모듈
모든 페이지 상단에서 apply_style() / page_header() / kpi_cards() 를 불러와 사용합니다.
"""
import streamlit as st

PRIMARY = "#7C4DFF"
INK = "#201A34"
MUTED = "#6B6580"
BG_SOFT = "#F6F3FC"
BORDER = "#E7E2F5"

ACCENTS = {
    "violet": "#7C4DFF",
    "blue": "#3B82F6",
    "green": "#10B981",
    "amber": "#F59E0B",
    "pink": "#EC4899",
    "rose": "#EF4444",
}


def apply_style():
    st.markdown(f"""
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        html, body, [class*="css"] {{
            font-family: 'Noto Sans KR', sans-serif;
        }}
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}

        [data-testid="stSidebar"] {{
            background-color: {BG_SOFT};
            border-right: 1px solid {BORDER};
        }}
        [data-testid="stSidebarNav"] li a {{
            border-radius: 8px;
            font-weight: 500;
            color: {INK};
        }}
        [data-testid="stSidebarNav"] li a:hover {{
            background-color: #ECE6FB;
        }}

        .aven-header {{
            display: flex; align-items: center; gap: 14px;
            padding: 18px 22px;
            border-radius: 16px;
            background: linear-gradient(135deg, {PRIMARY} 0%, #A78BFA 100%);
            color: white; margin-bottom: 22px;
            box-shadow: 0 6px 18px rgba(124, 77, 255, 0.25);
        }}
        .aven-header .icon {{ font-size: 30px; line-height: 1; }}
        .aven-header .title {{ font-size: 22px; font-weight: 800; margin: 0; }}
        .aven-header .subtitle {{ font-size: 13px; opacity: 0.9; margin: 2px 0 0 0; }}

        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
            gap: 14px;
            margin-bottom: 10px;
        }}
        .kpi-card {{
            background: white;
            border: 1px solid {BORDER};
            border-left: 5px solid var(--accent);
            border-radius: 12px;
            padding: 16px 18px;
            box-shadow: 0 2px 8px rgba(32, 26, 52, 0.05);
        }}
        .kpi-card .kpi-label {{
            font-size: 12.5px; color: {MUTED}; font-weight: 600;
            display: flex; align-items: center; gap: 6px; margin-bottom: 8px;
        }}
        .kpi-card .kpi-value {{
            font-size: 24px; font-weight: 800; color: {INK};
        }}
        .kpi-card .kpi-sub {{
            font-size: 11.5px; color: {MUTED}; margin-top: 4px;
        }}

        .section-title {{
            font-size: 16px; font-weight: 700; color: {INK};
            margin: 10px 0 10px 0; display: flex; align-items: center; gap: 8px;
        }}

        .aven-badge {{
            display: inline-block; padding: 2px 10px; border-radius: 999px;
            font-size: 11.5px; font-weight: 700;
        }}

        div[data-testid="stForm"] {{
            border: 1px solid {BORDER};
            border-radius: 14px;
            padding: 18px 20px 6px 20px;
            background: #FCFBFF;
        }}

        button[kind="primary"] {{
            border-radius: 8px !important;
        }}
    </style>
    """, unsafe_allow_html=True)


def page_header(icon: str, title: str, subtitle: str = ""):
    st.markdown(f"""
    <div class="aven-header">
        <div class="icon">{icon}</div>
        <div>
            <p class="title">{title}</p>
            <p class="subtitle">{subtitle}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)


def kpi_cards(cards):
    """
    cards: [{ "label": str, "value": str, "icon": str, "accent": "violet|blue|green|amber|pink|rose", "sub": str(optional) }, ...]
    """
    html = '<div class="kpi-grid">'
    for c in cards:
        color = ACCENTS.get(c.get("accent", "violet"), PRIMARY)
        sub = f'<div class="kpi-sub">{c["sub"]}</div>' if c.get("sub") else ""
        html += f"""
        <div class="kpi-card" style="--accent:{color}">
            <div class="kpi-label">{c.get('icon', '')} {c['label']}</div>
            <div class="kpi-value">{c['value']}</div>
            {sub}
        </div>
        """
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def section_title(icon: str, text: str):
    st.markdown(f'<div class="section-title">{icon} {text}</div>', unsafe_allow_html=True)


def sidebar_brand():
    st.sidebar.markdown(f"""
    <div style="padding: 10px 4px 16px 4px;">
        <div style="font-size:20px; font-weight:800; color:{INK};">🎤 Aven Entertainment</div>
        <div style="font-size:12.5px; color:{MUTED}; margin-top:2px;">경영 · 육성 통합 관리 시스템</div>
    </div>
    """, unsafe_allow_html=True)
