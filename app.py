import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# 1. 페이지 설정
st.set_page_config(page_title="수업일지 매니저", layout="centered")

# --- CSS 스타일링 (갤럭시 모바일 최적화) ---
st.markdown("""
    <style>
    .main { background-color: #fcfcfc; }
    h1 { font-size: 1.8rem !important; padding-bottom: 10px; }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3.8em;
        font-size: 1rem;
        font-weight: 600;
        margin-bottom: 8px;
        border: 1px solid #ddd;
    }
    .stCheckbox { padding: 10px 0px; font-size: 1.1rem; }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        font-size: 16px !important;
    }
    .block-container {
        padding-top: 2rem; padding-bottom: 2rem;
        padding-left: 1rem; padding-right: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 구글 시트 연결 설정 ---

conn = st.connection("gsheets", type=GSheetsConnection)

def get_last_record(class_name):
    """해당 학급의 마지막 기록을 시트에서 실시간으로 가져옴 (ttl=0 수정)"""
    try:
        # ttl=0 추가: 캐시를 사용하지 않고 즉시 시트에서 읽어옴
        df = conn.read(spreadsheet=URL, ttl=0)
        class_data = df[df['학급'] == class_name]
        if not class_data.empty:
            return class_data.iloc[-1]
        return None
    except:
        return None

# --- 앱 UI 시작 ---
st.title("📑 수업일지 매니저")

grade = st.radio("학년 선택", ["2학년", "3학년"], horizontal=True)

st.write("📍 **반 선택**")
col_a, col_b = st.columns(2)

if 'selected_class' not in st.session_state:
    st.session_state.selected_class = None

with col_a:
    if st.button("1반"): st.session_state.selected_class = f"{grade} 1반"
    if st.button("3반"): st.session_state.selected_class = f"{grade} 3반"
with col_b:
    if st.button("2반"): st.session_state.selected_class = f"{grade} 2반"
    if st.button("4반"): st.session_state.selected_class = f"{grade} 4반"

if st.session_state.selected_class:
    selected = st.session_state.selected_class
    st.success(f"**{selected}** 기록 중")
    
    # 2. 지난 기록 불러오기 (ttl=0이 적용된 함수 호출)
    last_data = get_last_record(selected)
    with st.expander("📅 지난 수업 복기", expanded=False):
        if last_data is not None:
            # 시트의 컬럼명과 일치하는지 확인하세요 (날짜, 내용, 숙제)
            st.info(f"마지막({last_data['날짜']}):\n- {last_data['내용']}\n- 숙제: {last_data['숙제']}")
        else:
            st.write("기록 없음")

    # 3. 오늘의 루틴 입력
    st.subheader("📝 수업 루틴")
    
    is_writing = st.checkbox("🖊️ 판서 완료")
    is_checking = st.checkbox("🔎 필기 검사")
    is_homework_check = st.checkbox("🏠 숙제 확인")
        
    v_title = st.text_input("🎬 시청한 동영상")
    details = st.text_area("📖 활동 내용", height=100)
    homework_msg = st.text_input("📢 다음 시간 숙제")

    # 4. 저장 버튼
    st.markdown("---")
    if st.button("💾 기록 저장하기"):
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
        
        try:
            # 저장할 때도 최신 데이터를 읽어와서 합침
            existing_df = conn.read(spreadsheet=URL, ttl=0)
            updated_df = pd.concat([existing_df, new_row], ignore_index=True)
            conn.update(spreadsheet=URL, data=updated_df)
            
            st.balloons()
            st.success("저장 완료!")
            
            # 중요: 저장 후 앱을 새로고침하여 상단 '복기' 내용을 최신화함
            st.rerun()
            
        except Exception as e:
            st.error(f"실패: {e}")
else:
    st.info("반 버튼을 클릭해 주세요.")