from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings


def main() -> None:
    pdf_path = Path(__file__).with_name("pre.pdf")
    if not pdf_path.exists():
        raise FileNotFoundError(f"找不到同目录下的PDF文件: {pdf_path}")

    reader = PdfReader(str(pdf_path))
    full_text_parts: list[str] = []
    for page in reader.pages:
        text = page.extract_text() or ""
        text = text.strip()
        if text:
            full_text_parts.append(text)

    full_text = "\n\n".join(full_text_parts).strip()
    if not full_text:
        print("PDF里没有提取到可用文本（可能是扫描版图片PDF，需要OCR）。")
        return

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
    )
    chunks = splitter.split_text(full_text)

    print(f"总共切分得到 {len(chunks)} 块。")
    for idx, chunk in enumerate(chunks[:2], start=1):
        print(f"\n===== Chunk {idx} =====")
        print(chunk)

    persist_dir = Path(__file__).with_name("chroma_db")
    collection_name = "pre_pdf_chunks"

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    vectordb = Chroma.from_texts(
        texts=chunks,
        embedding=embeddings,
        collection_name=collection_name,
        persist_directory=str(persist_dir),
    )

    query = "请用一句话总结这份PDF的核心内容是什么？"
    docs = vectordb.similarity_search(query, k=2)

    print("\n===== Similarity Search (Top 2) =====")
    print(f"Query: {query}")
    for rank, doc in enumerate(docs, start=1):
        print(f"\n----- Result {rank} -----")
        print(doc.page_content)


if __name__ == "__main__":
    main()
