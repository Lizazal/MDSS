#!/usr/bin/env python3

import justpy as jp
import asyncio
import threading
import webbrowser

from functools import partial
from enum import Enum
from dataclasses import dataclass
from queue import Queue
from pyke import knowledge_engine
from typing import Any, List, Union, NamedTuple


class Alternative(NamedTuple):
    choice: int
    text: str


@dataclass
class Question:
    question: str
    alternatives: List[Alternative]


@dataclass
class Solution:
    answer: str


class Flow(Enum):
    Continue = "continue"
    Break = "break"


class PykeDone(Exception):
    pass


class PykeWrapper(threading.Thread):
    def __init__(self, *, ask_module, answers: Queue, questions: Queue,
                 **kwargs):
        self._ask_module = ask_module
        self._questions = questions
        self._answers = answers
        super().__init__(**kwargs)

    def run(self):
        engine = knowledge_engine.engine(__file__)
        engine.ask_module = self._ask_module
        while True:
            try:
                engine.reset()
                engine.activate('ca_rules_questions')
                vals, _plans = engine.prove_1_goal(
                    'ca_rules_questions.what_therapy($therapy)')
                self._questions.put(Solution(vals['therapy']))
                next_step = self._answers.get()
                if next_step == Flow.Break:
                    break
            except PykeDone:
                break


def make_checkbox(parent, text):
    row = jp.Div(classes="flex flex-row content-center items-center justify-center", a=parent)
    jp.Label(text=text, a=row, classes='m-2 p-2 inline-block content-center items-center justify-center')
    return jp.Input(type='checkbox', classes='m-2 p-2 form-checkbox content-center items-center justify-center', a=row)


def make_question_label(parent, text):
    return jp.Div(
        text=text,
        classes="font-bold text-xl mb-2 content-center items-center justify-center ml-8",
        a=parent,
    )


async def open_app():
    loop = asyncio.get_event_loop()
    loop.call_later(1.0, partial(webbrowser.open, "http://127.0.0.1:8000"))


class AskMe:
    def __init__(self):
        self._questions_queue = Queue()
        self._answers_queue = Queue()
        self._engine = PykeWrapper(ask_module=self,
                                   answers=self._answers_queue,
                                   questions=self._questions_queue)
        self._engine.start()

    @classmethod
    def create(cls):
        obj = AskMe()
        return obj()

    def __call__(self):
        page = jp.WebPage()
        root = jp.Div(a=page)
        jp.H1(
            text="Терапия при фибрилляции предсердий",
            a=root,
            classes="font-bold text-green-700 text-xl mb-2 content-center ml-8",
        )
        question_div = jp.Div(a=root, classes="flex content-center items-center justify-center my-8 ml-8 mr-8")
        answers_div = jp.Div(
            a=root,
            classes=
            "flex gap-4 flex-col bg-green-500 text-white text-sm font-bold content-center items-center justify-center mx-24",
        )

        def reply(question: Question, choice: int, answer: str, *_args):
            #print(f"Answer to {question}: {answer}")
            question_div.delete_components()
            jp.P(text=f"{question.question} -> {answer}", a=answers_div)
            self._answers_queue.put(choice)
            update_ui(self._questions_queue.get())

        def restart_quiz(*_):
            question_div.delete_components()
            answers_div.delete_components()
            self._answers_queue.put(Flow.Continue)
            update_ui(self._questions_queue.get())

        async def start_quiz(*_):
            #print("start_quiz")
            update_ui(self._questions_queue.get())

        start_button = jp.Button(text="Начать", a=question_div)
        start_button.on("click", start_quiz)

        def update_ui(question):
            try:
                #print("Build", question)
                question_div.delete_components()
                if isinstance(question, Solution):
                    col = jp.Div(classes="flex gap-4 flex-col", a=question_div)
                    jp.Div(
                        text=f"Решение: {question.answer}",
                        classes="font-bold text-red-700 text-xl mb-2",
                        a=col,
                    )
                    button = jp.Button(
                        text="Начать заново",
                        a=col,
                        classes=
                        "bg-red-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded",
                    )
                    button.on('click', restart_quiz)
                elif isinstance(question, Question):
                    col = jp.Div(classes="flex gap-4 flex-col", a=question_div) #отвечает за кнопки
                    make_question_label(col, question.question)
                    row = jp.Div(classes="flex gap-4 flex-col", a=col)
                    for choice, answer in question.alternatives:
                        next_step = partial(reply, question, choice, answer)
                        button = jp.Button(
                            text=answer,
                            a=row,
                            classes=
                            "bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded",)
                        button.on("click", next_step)
                else:
                    raise ValueError(f"Unknown question {question}")
            except BaseException as err:
                print(f"Got {err}")
                self._answers_queue.put(Flow.Break)

        page.on('page_ready', start_quiz)
        return page

    def ask_yn(self, question, review=None):
        #print("YN")
        return self.ask_select_1(question,
                                 alternatives=[
                                     Alternative(True, "Да"),
                                     Alternative(False, "Нет"),
                                 ])

    def ask_select_1(self, question, alternatives, review=None):
        self._questions_queue.put(
            Question(
                question=question,
                alternatives=[Alternative(*a) for a in alternatives],
            ))
        answer = self._answers_queue.get()
        if answer is Flow.Break:
            raise Exception("Done")
        return answer


if __name__ == "__main__":
    jp.justpy(AskMe.create, startup=open_app)