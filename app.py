import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# 1. 페이지 설정 (중요: 모바일은 기본이 좁으므로 centered 유지)
st.set_page_config(page_title="수업일지 매니저", layout="centered")

# --- CSS 스타일링 (갤럭시 핸드폰 화면에 꽉 차게 전면 수정) ---
st.markdown("""
    <style>
    /* 전체 배경색 살짝 조정 */
    .main { background-color: #fcfcfc; }
    
    /* 제목 폰트 크기 조절 */
    h1 { font-size: 1.8rem !important; padding-bottom: 10px; }
    
    /* 버튼: 가독성 높이고 터치하기 좋게 크게 */
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3.8em;
        font-size: 1rem;
        font-weight: 600;
        margin-bottom: 8px;
        border: 1px solid #ddd;
    }
    
    /* 체크박스 크기 및 간격 */
    .stCheckbox {
        padding: 10px 0px;
        font-size: 1.1rem;
    }
    
    /* 입력창(Text Input/Area) 높이 조절 */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        font-size: 16px !important; /* 모바일 아이폰/갤럭시 줌 방지 */
    }

    /* 위젯 간 간격 좁히기 */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 구글 시트 연결 설정 (기존과 동일) ---
URL = "선생님의_구글_시트_주소를_여기에_넣으세요"
conn = st.connection("gsheets", type=GSheetsConnection)

def get_last_record(class_name):
    try:
        df = conn.read(spreadsheet=URL)
        class_data = df[df['학급'] == class_name]
        if not class_data.empty:
            return class_data.iloc[-1]
        return None
    except:
        return None

# --- 앱 UI 시작 ---
st.title("📑 수업일지 매니저")

# 학년 선택 (가로로 넓게 배치)
grade = st.radio("학년 선택", ["2학년", "3학년"], horizontal=True)

st.write("📍 **반 선택**")
# 4열에서 2열로 변경 (모바일에서 버튼이 안 깨지도록)
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
    
    # 2. 지난 기록 불러오기
    last_data = get_last_record(selected)
    with st.expander("📅 지난 수업 복기", expanded=False):
        if last_data is not None:
            st.info(f"마지막({last_data['날짜']}):\n- {last_data['내용']}\n- 숙제: {last_data['숙제']}")
        else:
            st.write("기록 없음")

    # 3. 오늘의 루틴 (모바일은 가로 columns보다 세로가 나음)
    st.subheader("📝 수업 루틴")
    
    is_writing = st.checkbox("🖊️ 판서 완료")
    is_checking = st.checkbox("🔎 필기 검사")
    is_homework_check = st.checkbox("🏠 숙제 확인")
        
    v_title = st.text_input("🎬 시청한 동영상")
    details = st.text_area("📖 활동 내용", height=100)
    homework_msg = st.text_input("📢 다음 시간 숙제")

    # 4. 저장 버튼 (눈에 띄게 배치)
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
            existing_df = conn.read(spreadsheet=URL)
            updated_df = pd.concat([existing_df, new_row], ignore_index=True)
            conn.update(spreadsheet=URL, data=updated_df)
            st.balloons()
            st.success("저장 완료!")
        except Exception as e:
            st.error(f"실패: {e}")
else:
    st.info("반 버튼을 클릭해 주세요.")