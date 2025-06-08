from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).parent
ANSWER_NOT_FOUND_MESSAGE = "Вернемся с ответом позже! #ответ"


BOT_DEBUG = False


class Environments(BaseSettings):
    token: str
    gigachat_credentials: str = Field(alias="GIGACHAT_CREDENTIALS")

    class Config:

        env_prefix = "BOT_"


environments = Environments(
    _env_file=Path(__file__).parent.parent / ".env"
)
