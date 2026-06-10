import streamlit as st

from app.config import MIN_SCORE, TOP_K
from app.generator import ask


DEMO_QUESTIONS = [
    "Что смешалось в доме Облонских?",
    "Какая фамилия была у чиновника?",
    "Что сказал незнакомец после слов Без имени нельзя?",
    "Как перезапустить кластер Kubernetes?",
]


st.set_page_config(page_title="RusLit RAG", page_icon="R", layout="wide")

st.title("RusLit RAG")
st.caption("Локальный учебный RAG: RusLit -> chunks -> TF-IDF -> ответ с источниками")

with st.sidebar:
    st.header("Настройки")
    top_k = st.slider("Количество источников", min_value=1, max_value=10, value=TOP_K)
    st.caption(f"Порог отказа: score >= {MIN_SCORE:.2f}")
    st.header("Demo-вопросы")
    selected = st.radio("Выберите вопрос", DEMO_QUESTIONS, label_visibility="collapsed")

question = st.text_input("Вопрос", value=selected)
run = st.button("Найти ответ", type="primary")

if run or question:
    result = ask(question, k=top_k)
    st.subheader("Ответ")
    st.markdown(result["answer"])

    st.subheader("Источники")
    if not result["sources"]:
        st.info("Источники не найдены.")
    for index, source in enumerate(result["sources"], start=1):
        with st.expander(
            f"[{index}] doc_id={source['doc_id']} | score={source['score']:.3f} | {source['title']}",
            expanded=index == 1,
        ):
            st.write(f"chunk_id: `{source['chunk_id']}`")
            st.write(f"source: {source['source']}")
            st.write(source["text"])
