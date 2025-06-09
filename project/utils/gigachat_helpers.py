import json

from gigachat import GigaChat
from typing import Sequence

from langchain_community.embeddings.gigachat import GigaChatEmbeddings
from langchain_community.vectorstores import Qdrant
from qdrant_client import QdrantClient, models

from pathlib import Path
from typing import List, Union

from langchain.schema import Document

from settings import USE_VERIFY_SSL_CERT


def is_question(gigachat_client: GigaChat, text: str) -> bool | None:
    if "?" in text:
        return True
    response = gigachat_client.chat({
        "model": "GigaChat",
        "messages": [
            {
                "role": "system",
                "content": (
                    "Ты — минимальный классификатор. "
                    "Верни JSON вида {\"is_question\": true/false} …"
                )
            },
            {"role": "user", "content": text}
        ],
        "temperature": 0,
        "max_tokens": 7,
        "response_format": {"type": "json_object"}
    })
    try:
        content_dict = json.loads(response.choices[0].message.content)
        if "is_question" not in content_dict:
            return None
        return content_dict["is_question"]
    except json.decoder.JSONDecodeError:
        return None


def load_docs(path: Union[str, Path]) -> List[Document]:
    """
    Load documents from a file or directory into a list of LangChain Documents.

    Args:
        path: Path to a file or directory containing text files (.txt, .md).

    Returns:
        List[Document]: Documents with page_content and metadata {"source": file_path}.
    """
    p = Path(path)
    docs: List[Document] = []

    if p.is_file():
        files = [p]
    elif p.is_dir():
        # consider .txt and .md files
        files = list(p.rglob("*.txt")) + list(p.rglob("*.md"))
    else:
        raise ValueError(f"Path {path} is neither a file nor a directory.")

    for f in files:
        text = f.read_text(encoding="utf-8")
        docs.append(
            Document(
                page_content=text,
                metadata={"source": str(f)}
            )
        )
    return docs


def split_text_into_chunks(
    docs: List[Document],
    chunk_size: int = 500,
    chunk_overlap: int = 100
) -> List[Document]:
    """
    Split Documents into smaller chunks of text.

    Args:
        docs: List of Documents to split.
        chunk_size: Number of words per chunk.
        chunk_overlap: Number of words to overlap between chunks.

    Returns:
        List[Document]: New Documents for each chunk, preserving metadata with chunk index.
    """
    all_chunks: List[Document] = []

    for doc in docs:
        words = doc.page_content.split()
        total_words = len(words)
        start = 0
        chunk_index = 0

        while start < total_words:
            end = start + chunk_size
            chunk_words = words[start:end]
            chunk_text = " ".join(chunk_words)

            meta = doc.metadata.copy() if isinstance(doc.metadata, dict) else {}
            meta.update({
                "chunk_index": chunk_index,
                "source": doc.metadata.get("source") if isinstance(doc.metadata, dict) else None
            })

            all_chunks.append(
                Document(
                    page_content=chunk_text,
                    metadata=meta
                )
            )

            chunk_index += 1
            start += chunk_size - chunk_overlap

    return all_chunks


def prepare_kb_vector_store(
    kb_source: str | Path,
    collection_name: str = "kb",
    qdrant_location: str = ":memory:",          # или Path / URL к удалённому кластеру
    gigachat_token: str | None = None,
) -> Qdrant:
    # 1. Embedding model (lazy - no request yet)
    embeddings = GigaChatEmbeddings(access_token=gigachat_token)
    embeddings.verify_ssl_certs = USE_VERIFY_SSL_CERT

    # 2. Qdrant client (local RAM | local disk | remote)
    client = QdrantClient(path=qdrant_location)

    # 3. Re-use if collection already present
    if client.collection_exists(collection_name):
        return Qdrant(client=client,
                      collection_name=collection_name,
                      embeddings=embeddings)
    else:
        client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=1024, distance=models.Distance.COSINE
            ),
        )

    raw_docs = load_docs(kb_source)
    qdrant = Qdrant(client, collection_name, embeddings)
    qdrant.add_documents(raw_docs, batch_size=1024)
    return qdrant


def retrieve_context(store: Qdrant, query: str, k: int = 4) -> List[str]:
    """Return top‑k chunk texts relevant to the query."""
    docs = store.similarity_search(query, k=k)
    return [d.page_content for d in docs]


def ask_llm(store: Qdrant, gigachat_client: GigaChat, question: str, k: int = 4) -> dict:
    """Query GigaChat with RAG context; returns a JSON dict."""
    context_chunks = retrieve_context(store, question, k=k)
    system_prompt = (
        "Ты — ассистент, который отвечает строго JSON‑объектом вида "
        '{"found": true/false, "answer": "<text>"}. '
        "Используй только факты из блока CONTEXT. "
        "Если фактов недостаточно, верни {\"found\": false}."
    )

    payload = {
        "model": "GigaChat-Max",
        "temperature": 0.001,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "assistant", "content": "CONTEXT:\n" + "\n---\n".join(context_chunks)},
            {"role": "user", "content": question},
        ],
    }

    response = gigachat_client.chat(payload)
    raw = response.choices[0].message.content.strip()
    print(raw)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # если модель "заговорила" — возвращаем found=false
        return {"found": False, "answer": ""}