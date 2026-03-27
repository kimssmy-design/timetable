import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# 1. 페이지 설정
st.set_page_config(page_title="수업일지 매니저", layout="centered")

# CSS 스타일링 (모바일 최적화)
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 3.5em;
        font-size: 1.1em;
        margin-bottom: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 구글 시트 연결 설정 ---
# 시트 URL을 입력하세요 (미리 만들어둔 구글 시트의 주소)
URL = "https://docs.google.com/spreadsheets/d/1d5xIDS0viNHVuvBrviGp4LYYolBCuFfH9bUXLEOL3eA/edit?usp=sharing"
conn = st.connection("gsheets", type=GSheetsConnection)

def get_last_record(class_name):
    """해당 학급의 마지막 기록을 시트에서 가져오는 함수"""
    try:
        df = conn.read(spreadsheet=URL)
        class_data = df[df['학급'] == class_name]
        if not class_data.empty:
            return class_data.iloc[-1] # 가장 마지막 행 리턴
        return None
    except:
        return None

# --- 앱 UI 시작 ---
st.title("📑 수업일지 매니저")

grade = st.radio("학년 선택", ["2학년", "3학년"], horizontal=True)

st.write("📍 **반을 선택하세요**")
col1, col2, col3, col4 = st.columns(4)

if 'selected_class' not in st.session_state:
    st.session_state.selected_class = None

# 버튼 클릭 시 세션 상태 업데이트
with col1:
    if st.button("1반"): st.session_state.selected_class = f"{grade} 1반"
with col2:
    if st.button("2반"): st.session_state.selected_class = f"{grade} 2반"
with col3:
    if st.button("3반"): st.session_state.selected_class = f"{grade} 3반"
with col4:
    if st.button("4반"): st.session_state.selected_class = f"{grade} 4반"

if st.session_state.selected_class:
    selected = st.session_state.selected_class
    st.success(f"✅ **{selected}** 수업 기록 중")
    
    # 2. 지난 기록 불러오기 (자동화)
    last_data = get_last_record(selected)
    with st.expander("📅 지난 수업 복기"):
        if last_data is not None:
            st.info(f"마지막 기록({last_data['날짜']}):\n- {last_data['내용']}\n- 숙제: {last_data['숙제']}")
        else:
            st.write("이전 기록이 없습니다.")

    # 3. 오늘의 루틴 입력
    st.subheader("📝 오늘 수업 루틴")
    c1, c2 = st.columns(2)
    with c1:
        is_writing = st.checkbox("🖊️ 판서 완료")
        is_checking = st.checkbox("🔎 필기 검사")
    with c2:
        is_homework_check = st.checkbox("🏠 숙제 확인")
        
    v_title = st.text_input("🎬 시청한 동영상", placeholder="영상 제목...")
    details = st.text_area("📖 교과서 설명 및 활동", placeholder="주요 활동 내용...", height=100)
    homework_msg = st.text_input("📢 다음 시간 숙제")

    # 4. 저장 버튼
    if st.button("💾 이대로 기록 저장하기"):
        # 저장할 데이터 정리
        new_row = pd.DataFrame([{
            "날짜": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "학급": selected,
            "판서": "O" if is_writing else "X",
            "필기검사": "O" if is_checking else "X",
            "숙제확인": "O" if is_homework_check else "X",
            "동영상": v_title,
            "내용": details,
            "숙제": homework_msg
        }])
        
        # 기존 데이터에 추가하여 업데이트
        try:
            existing_df = conn.read(spreadsheet=URL)
            updated_df = pd.concat([existing_df, new_row], ignore_index=True)
            conn.update(spreadsheet=URL, data=updated_df)
            st.balloons()
            st.success("구글 시트에 성공적으로 저장되었습니다!")
        except Exception as e:
            st.error(f"저장 실패: {e}")
else:
    st.info("위의 학급 버튼을 눌러 수업을 시작해 주세요.")