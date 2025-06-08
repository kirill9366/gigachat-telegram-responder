import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher, html, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode, ChatType
from aiogram.filters import CommandStart
from aiogram.types import Message

from loader import gigachat, store
from settings import environments, ANSWER_NOT_FOUND_MESSAGE
from utils.gigachat_helpers import is_question, ask_llm

dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")


def _is_channel_comment(m: Message) -> bool:
    """
    Проверяем, что это комментарий к посту канала:
    1. чат – supergroup (группа-обсуждение);
    2. сообщение — reply на сообщение, присланное от имени канала
       (sender_chat.type == 'channel').
    """
    return (
        m.chat.type == ChatType.SUPERGROUP
        and m.reply_to_message                       # есть родительское сообщение
        and m.reply_to_message.sender_chat           # оно «от имени канала»
        and m.reply_to_message.sender_chat.type == ChatType.CHANNEL
    )


@dp.message(F.text, _is_channel_comment)
async def echo_handler(message: Message) -> None | Message:
    result = is_question(gigachat, message.text)
    if result is False:
        return
    elif result is None:
        return
    response = ask_llm(store, gigachat, message.text)
    if not isinstance(response, dict) or "found" not in response:
        return
    if not response["found"]:
        return await message.reply(ANSWER_NOT_FOUND_MESSAGE)
    else:
        return await message.reply(response["answer"])


async def main() -> None:
    bot = Bot(
        token=environments.token,
        default=DefaultBotProperties(
            parse_mode=ParseMode.MARKDOWN
        )
    )
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
