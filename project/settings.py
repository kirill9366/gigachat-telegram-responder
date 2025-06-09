from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).parent
ANSWER_NOT_FOUND_MESSAGE = "Вернемся с ответом позже! #ответ"

USE_VERIFY_SSL_CERT = False
BOT_DEBUG = False
QDRANT_DATA_LOCATION = "docker_volumes/qdrant_data"


class Environments(BaseSettings):
    token: str
    gigachat_credentials: str = Field(alias="GIGACHAT_CREDENTIALS")

    class Config:

        env_prefix = "BOT_"


environments = Environments(
    _env_file=Path(__file__).parent.parent / ".env"
)
