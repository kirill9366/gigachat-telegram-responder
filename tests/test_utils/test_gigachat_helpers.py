from utils.gigachat_helpers import is_question, ask_llm
from loader import gigachat, store


def test_is_question():
    assert is_question(gigachat, "как твои дела?")
    assert is_question(gigachat, "чем занимаешься?")
    assert not is_question(gigachat, "Мои дела хорошо")
    assert not is_question(gigachat, "1. Мои дела хорошо 2. Как дела?")


def test_ask_llm():
    print(ask_llm(store, gigachat, "Кто создал язык Python?"))
    # print(ask_llm(store, gigachat, "Что такое GigaChat?"))
    # print(ask_llm(store, gigachat, "Какой стандартный менеджер пакетов используется в Python?"))
    # print(ask_llm(store, gigachat, "Что гласит третий закон Ньютона?"))
    # print(ask_llm(store, gigachat, "Какая столица Франции?"))
    # print(ask_llm(store, gigachat, "Что такое язык Java?"))
