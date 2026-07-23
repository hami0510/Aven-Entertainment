"""
Aiven Entertainment 관리 시스템 - 진입점(라우터)
st.navigation으로 사이드바 메뉴명을 한글로 표시합니다.
pages/ 폴더의 파일을 자동으로 읽어 '숫자_' 접두사를 뗀 이름을 메뉴명으로 사용합니다.
"""
import glob
import os

import streamlit as st

st.set_page_config(
    page_title="Aiven Entertainment 관리 시스템",
    page_icon="🎤",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 메뉴명별 아이콘 (없으면 아이콘 없이 표시)
ICONS = {
    "대시보드": "📊",
    "경영관리": "💼",
    "소속가수관리": "🌟",
    "아티스트관리": "🌟",
    "연습생관리": "👥",
    "콘텐츠홍보": "📢",
    "트레이닝스케줄": "📅",
    "보고서": "📝",
}

nav_pages = [st.Page("home.py", title="대시보드", icon=ICONS.get("대시보드"), default=True)]

for path in sorted(glob.glob(os.path.join(os.path.dirname(__file__), "pages", "*.py"))):
    filename = os.path.splitext(os.path.basename(path))[0]
    # '3_경영관리' -> '경영관리'
    title = filename.split("_", 1)[-1] if "_" in filename else filename
    nav_pages.append(st.Page(path, title=title, icon=ICONS.get(title), url_path=title))

pg = st.navigation(nav_pages)
pg.run()
