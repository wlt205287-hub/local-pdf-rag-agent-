from __future__ import annotations

import hashlib
from io import BytesIO
from typing import Iterable

import jieba
import streamlit as st
from openai import OpenAI
from pypdf import PdfReader

from langchain_community.retrievers import BM25Retriever
from langchain_text_splitters import RecursiveCharacterTextSplitter


def extract_pdf_text(pdf_bytes: bytes) -> str:
    reader = PdfReader(BytesIO(pdf_bytes))
    parts: list[str] = []
    for page in reader.pages:
        text = (page.extract_text() or "").strip()
        if text:
            parts.append(text)
    return "\n\n".join(parts).strip()


def jieba_tokenizer(text: str) -> list[str]:
    return jieba.lcut(text)


def build_retriever_from_pdf_bytes(pdf_bytes: bytes) -> BM25Retriever:
    full_text = extract_pdf_text(pdf_bytes)
    if not full_text:
        raise ValueError("PDF里没有提取到可用文本（可能是扫描版图片PDF，需要OCR）。")

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.create_documents([full_text])
    if not chunks:
        raise ValueError("切片结果为空。")

    retriever = BM25Retriever.from_texts(
        [chunk.page_content for chunk in chunks],
        preprocess_func=jieba_tokenizer,
    )
    retriever.k = 3
    return retriever


def deepseek_stream_answer(api_key: str, prompt: str) -> Iterable[str]:
    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
    stream = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}],
        stream=True,
    )
    for event in stream:
        delta = event.choices[0].delta
        chunk = getattr(delta, "content", None)
        if chunk:
            yield chunk


st.set_page_config(page_title="PDF 智能问答", layout="wide")
st.title("PDF 智能问答（RAG + DeepSeek）")

with st.sidebar:
    st.header("配置")
    uploaded = st.file_uploader("上传 PDF", type=["pdf"])
    api_key = st.text_input("DeepSeek API Key", type="password")
    st.caption("提示：当前使用 BM25（纯文本检索），无需本地向量模型。")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "retriever" not in st.session_state:
    st.session_state.retriever = None
if "pdf_hash" not in st.session_state:
    st.session_state.pdf_hash = None


if uploaded is not None:
    pdf_bytes = uploaded.getvalue()
    pdf_hash = hashlib.sha256(pdf_bytes).hexdigest()

    if st.session_state.retriever is None or st.session_state.pdf_hash != pdf_hash:
        with st.spinner("正在读取PDF、切片并构建 BM25 检索器（内存）..."):
            st.session_state.retriever = build_retriever_from_pdf_bytes(pdf_bytes)
            st.session_state.pdf_hash = pdf_hash
        st.success("检索器已就绪。")
else:
    st.info("请先在左侧上传一个 PDF。")


for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


user_question = st.chat_input("输入你的问题并回车…")
if user_question:
    st.session_state.messages.append({"role": "user", "content": user_question})
    with st.chat_message("user"):
        st.markdown(user_question)

    if st.session_state.retriever is None:
        with st.chat_message("assistant"):
            st.markdown("请先上传 PDF，完成检索器构建后再提问。")
        st.stop()

    if not api_key:
        with st.chat_message("assistant"):
            st.markdown("请先在左侧输入 DeepSeek API Key。")
        st.stop()

    docs = st.session_state.retriever.invoke(user_question)
    context = "\n\n".join(d.page_content for d in docs)
    prompt = f"基于以下上下文信息：\n{context}\n请回答用户的问题：{user_question}"

    with st.chat_message("assistant"):
        answer = st.write_stream(deepseek_stream_answer(api_key, prompt))

    st.session_state.messages.append({"role": "assistant", "content": answer})

