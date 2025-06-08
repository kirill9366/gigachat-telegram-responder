from gigachat import GigaChat
from langchain_community.vectorstores import Qdrant

from settings import environments, BASE_DIR, CERT_FILE
from utils.gigachat_helpers import prepare_kb_vector_store

gigachat = GigaChat(
    credentials=environments.gigachat_credentials,
    scope="GIGACHAT_API_PERS",
    model="GigaChat",
    verify_ssl_certs=False,
)

store: Qdrant = prepare_kb_vector_store(
    kb_source=BASE_DIR.joinpath("knowledge"),            # folder with *.txt / *.md files
    collection_name="kb",
    qdrant_location="docker_volumes/qdrant_data",    # on‑disk directory, change as needed
    gigachat_token=gigachat.get_token().access_token,
)
