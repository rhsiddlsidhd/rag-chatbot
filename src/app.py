import streamlit as st

from generator import generate, GenerationResult

st.set_page_config(page_title="ITF Rules Chatbot", layout="centered")
st.title("ITF Rules of Tennis — Q&A")

query = st.text_input("질문을 입력하세요", placeholder="e.g. How many points are needed to win a game?")

if st.button("검색", disabled=not query):
    with st.spinner("답변 생성 중..."):
        result: GenerationResult = generate(query)

    st.markdown("### 답변")
    st.write(result.answer)

    st.markdown("### 참고 규칙")
    for chunk in result.sources:
        with st.expander(f"{chunk.title} ({chunk.chunk_id})"):
            st.write(chunk.text)
