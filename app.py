import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# 1. 페이지 설정
st.set_page_config(page_title="수업일지 매니저", layout="centered")

# --- CSS 스타일링 (동일) ---
st.markdown("""
    <style>
    .main { background-color: #fcfcfc; }
    h1 { font-size: 1.8rem !important; padding-bottom: 10px; }
    .stButton>button {
        width: 100%; border-radius: 10px; height: 3.8em;
        font-size: 1rem; font-weight: 600; margin-bottom: 8px; border: 1px solid #ddd;
    }
    .stCheckbox { padding: 10px 0px; font-size: 1.1rem; }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea { font-size: 16px !important; }
    .block-container { padding: 2rem 1rem; }
    </style>
    """, unsafe_allow_html=True)

# --- 구글 시트 연결 설정 ---
conn = st.connection("gsheets", type=GSheetsConnection)

def get_last_record(class_name):
    """시크릿 설정을 사용하여 실시간으로 최신 기록을 가져옴"""
    try:
        # spreadsheet=URL 인자를 제거하고 시크릿의 설정을 따릅니다.
        df = conn.read(ttl=0) 
        
        # 학급명 매칭 (공백 제거 및 문자열 변환)
        df['학급'] = df['학급'].astype(str).str.strip()
        search_target = str(class_name).strip()
        
        class_data = df[df['학급'] == search_target]
        if not class_data.empty:
            return class_data.iloc[-1]
        return None
    except Exception as e:
        # 에러가 나면 화면에 표시하여 원인을 알 수 있게 함
        st.error(f"데이터 읽기 오류: {e}")
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
    
    # 데이터 불러오기
    last_data = get_last_record(selected)
    with st.expander("📅 지난 수업 복기", expanded=False):
        if last_data is not None:
            d_val = last_data.get('날짜', '-')
            c_val = last_data.get('내용', '기록된 내용이 없습니다.')
            h_val = last_data.get('숙제', '없음')
            st.info(f"마지막({d_val}):\n- 내용: {c_val}\n- 숙제: {h_val}")
        else:
            st.warning("이 학급의 이전 기록을 찾을 수 없습니다.")

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
        # 저장할 데이터 프레임 생성 (생략되었던 부분 추가)
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
            # 기존 데이터 읽기 (ttl=0)
            existing_df = conn.read(ttl=0)
            # 데이터 합치기
            updated_df = pd.concat([existing_df, new_row], ignore_index=True)
            # 시트로 업데이트 (spreadsheet=URL 인자 제거)
            conn.update(data=updated_df) 
            
            st.balloons()
            st.success("저장 완료!")
            st.rerun() # 화면 갱신하여 상단 복기 내용 업데이트
        except Exception as e:
            st.error(f"저장 실패: {e}")
else:
    st.info("반 버튼을 클릭해 주세요.")