# -*- coding: utf-8 -*-

# ! pip install -q -U google-genai
# ! pip install streamlit requests
# API_KEY = ''
# from google import genai
# client = genai.Client(api_key=API_KEY)
# response = client.models.generate_content(
#     model="gemini-2.0-flash",
#     contents="""
#         지식재산처장님의 카이로로 가는 해외출장 3박4일 숙박비를 계산해줘
#     """,
# )

# print(response.text)



import streamlit as st
from google import genai
import time

# 페이지 설정
st.set_page_config(
    page_title="kipi-test",
    page_icon="🔍",
    layout="wide"
)

API_KEY = st.secrets["google_api_key"]

# 사이드바 설정
with st.sidebar:
    st.markdown("### 🔍 Rules")

    # API 키 입력 (선택사항)
    api_key_input = st.text_input(
        "Gemini API Key",
        value="",
        type="password",
        help="API 키를 입력하세요 (선택사항)"
    )

    if api_key_input:
        API_KEY = api_key_input

    # 각종 설정 옵션들
    with st.expander("📁 개요", expanded=False):
        st.write("챗봇 인터페이스")

    with st.expander("📍 출력방법", expanded=False):
        output_method = st.selectbox(
            "출력 방식 선택",
            ["실시간 출력", "일괄 출력"],
            index=0
        )

    with st.expander("🎯 출력설정", expanded=False):
        temperature = st.slider(
            "창의성 수준 (Temperature)",
            min_value=0.0,
            max_value=2.0,
            value=0.7,
            step=0.1
        )

        max_tokens = st.slider(
            "최대 토큰 수",
            min_value=100,
            max_value=2000,
            value=1000,
            step=100
        )

    with st.expander("💭 알고리즘", expanded=False):
        model_name = st.selectbox(
            "모델 선택",
            ["gemini-2.5-flash"],
            index=0
        )

    with st.expander("📄 라이센스", expanded=False):
        st.write("MIT License")

    with st.expander("📊 표시설정", expanded=False):
        show_stats = st.checkbox("통계 표시", value=False)


# 메인 화면
st.markdown("# okauto 테스트 화면")
st.markdown("*Powered by Google Gemini*")

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

if "total_tokens" not in st.session_state:
    st.session_state.total_tokens = 0

# Gemini API 호출 함수
def call_gemini_api(prompt: str) -> str:
    """
    Google Gemini API를 호출하는 함수
    """
    try:
        if not API_KEY or API_KEY == "your-gemini-api-key-here":
            return "⚠️ API 키가 설정되지 않았습니다. 사이드바에서 API 키를 입력하거나 코드의 API_KEY 변수를 설정해주세요.\n\n" \
                   f"데모용 응답: '{prompt}'에 대한 답변입니다. 실제 환경에서는 Gemini API가 연동되어 정확한 답변을 제공할 것입니다."

        # Gemini 클라이언트 초기화
        client = genai.Client(api_key=API_KEY)

        # API 호출
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config={
                "temperature": temperature,
                "max_output_tokens": max_tokens,
            }
        )

        # 토큰 사용량 업데이트 (예시)
        st.session_state.total_tokens += len(prompt.split()) + len(response.text.split())

        return response.text

    except Exception as e:
        error_msg = str(e)
        if "API_KEY" in error_msg or "authentication" in error_msg.lower():
            return f"🔑 API 키 오류: API 키를 확인해주세요.\n\n에러 상세: {error_msg}"
        elif "quota" in error_msg.lower() or "limit" in error_msg.lower():
            return f"📊 사용량 한도 초과: API 사용량을 확인해주세요.\n\n에러 상세: {error_msg}"
        else:
            return f"❌ API 호출 중 오류가 발생했습니다: {error_msg}\n\n" \
                   f"데모용 응답: '{prompt}'에 대한 답변을 드리겠습니다."

# 이전 대화 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 사용자 입력 처리
if prompt := st.chat_input("질문해보세요!"):
    # 사용자 메시지 추가
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # AI 응답 생성
    with st.chat_message("assistant"):
        if output_method == "실시간 출력":
            # 실시간 출력 효과를 위한 스피너
            with st.spinner("Gemini가 답변을 생성하고 있습니다..."):
                response = call_gemini_api(prompt)

            # 타이핑 효과 시뮬레이션
            message_placeholder = st.empty()
            displayed_text = ""

            for char in response:
                displayed_text += char
                message_placeholder.markdown(displayed_text + "▌")
                time.sleep(0.01)  # 타이핑 효과

            message_placeholder.markdown(response)

        else:  # 일괄 출력
            with st.spinner("Gemini가 답변을 생성하고 있습니다..."):
                response = call_gemini_api(prompt)
                st.markdown(response)

    # AI 응답을 세션에 저장
    st.session_state.messages.append({"role": "assistant", "content": response})

# 통계 표시
if show_stats and st.session_state.messages:
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("💬 총 대화 수", len(st.session_state.messages)//2)

    with col2:
        st.metric("🎯 현재 모델", model_name)

    with col3:
        st.metric("🌡️ Temperature", f"{temperature}")

    with col4:
        st.metric("📊 예상 토큰", st.session_state.total_tokens)

# 하단 정보 및 컨트롤
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.info("💡 **팁**: 구체적이고 명확한 질문을 하시면 더 좋은 답변을 받을 수 있습니다.")

with col2:
    if st.button("🗑️ 대화 초기화"):
        st.session_state.messages = []
        st.session_state.total_tokens = 0
        st.rerun()

with col3:
    if st.button("💾 대화 저장"):
        if st.session_state.messages:
            chat_history = ""
            for msg in st.session_state.messages:
                role = "사용자" if msg["role"] == "user" else "AI"
                chat_history += f"**{role}**: {msg['content']}\n\n"

            st.download_button(
                label="📥 대화 내용 다운로드",
                data=chat_history,
                file_name=f"wonq_chat_{time.strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )
        else:
            st.warning("저장할 대화가 없습니다.")

# API 키 안내
if not api_key_input and (not API_KEY or API_KEY == "your-gemini-api-key-here"):
    st.warning("⚠️ Gemini API 키가 설정되지 않았습니다. 사이드바에서 API 키를 입력하거나 코드를 수정해주세요.")
    with st.expander("API 키 설정 방법"):
        st.markdown("""
        1. [Google AI Studio](https://aistudio.google.com/)에서 API 키를 발급받으세요.
        2. 사이드바의 'Gemini API Key' 필드에 입력하거나
        3. 코드의 `API_KEY` 변수를 직접 수정하세요.

        ```python
        API_KEY = "your-actual-api-key-here"
        ```
        """)

# CSS 스타일 추가
st.markdown("""
<style>
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }

    .stTextInput > div > div > input {
        border-radius: 20px;
    }

    .main > div {
        padding-top: 2rem;
    }

    .stSidebar {
        background-color: #f0f2f6;
    }

    .stMetric {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #e0e0e0;
    }
</style>
""", unsafe_allow_html=True)
