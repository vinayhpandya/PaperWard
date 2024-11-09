from __future__ import annotations
import os
import logging
from openai import OpenAI
from dataclasses import dataclass, field
from typing import Literal, TypedDict, Union

MessageRole = Literal["system", "user", "assistant"]


class MessageDict(TypedDict):
    role: MessageRole
    content: str


@dataclass
class Message:
    """OpenAI Message object containing a role and the message content"""

    role: MessageRole
    content: str

    def __init__(self, role: MessageRole, content: str):
        self.role = role
        self.content = content

    def raw(self) -> MessageDict:
        return {"role": self.role, "content": self.content}

    @classmethod
    def from_json(cls, json_dict: dict):
        return cls(role=json_dict["role"], content=json_dict["content"])


@dataclass
class ChatSequence:
    """Utility container for a chat sequence"""

    messages: list[Message] = field(default_factory=list)

    def __getitem__(self, i: int):
        return self.messages[i]

    def append(self, message: Message):
        return self.messages.append(message)

    def raw(self) -> list[dict]:
        return [message.raw() for message in self.messages]

    def pop(self, i: int = -1):
        return self.messages.pop(i)

    @classmethod
    def from_json(cls, json_list: list[dict]):
        return cls(messages=[Message.from_json(json_dict) for json_dict in json_list])


class LLMHandler:
    llm_model = None
    record_messages = False
    record_file = None
    client = None
    log_count = 0
    prompt_token_usage = 0
    completion_token_usage = 0
    embedding_token_usage = 0

    def __init__(
        self,
        llm_model: str = "gpt-3.5-turbo",
        record_messages: bool = False,
        log_folder: str = "llm_logs",
    ):
        self.llm_model = llm_model
        self.record_messages = record_messages
        self.log_folder = log_folder
        self.client = OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY"),
        )

        # create the log folder if it doesn't exist
        if not os.path.exists(self.log_folder) and self.record_messages:
            os.makedirs(self.log_folder)

    def chat_with_gpt(
        self, messages: Union[ChatSequence, list[dict], str], model=None, **kwargs
    ) -> str:
        # if messages is a ChatSequence, convert it to a list of dicts
        if isinstance(messages, ChatSequence):
            messages = messages.raw()
        # if messages is a string, convert it to a list of dicts
        if isinstance(messages, str):
            messages = [{"role": "user", "content": messages}]

        if model is None:
            model = self.llm_model

        # save the messages to a file
        self.save_messages(messages)

        if "gpt" in model:
            try:
                response = self.client.chat.completions.create(
                    model=model, messages=messages, **kwargs
                )
            except Exception as err:
                logging.error(f"OPENAI ERROR: {err}")
                raise err

            content = response.choices[0].message.content
            self.prompt_token_usage += response.usage.prompt_tokens
            self.completion_token_usage += response.usage.completion_tokens

        else:
            raise ValueError(f"Model {model} not supported")

        self.save_messages([{"role": "assistant", "content": content}])
        return content

    def save_messages(self, messages: list[dict]):
        if not self.record_messages:
            return
        with open(
            f"{self.log_folder}/{self.log_count}.txt", "w", encoding="utf-8"
        ) as f:
            for message in messages:
                f.write(f'{message["role"]}: ')
                f.write(f'{message["content"]}\n')
        self.log_count += 1

    def get_text_embeddings_multi(self, texts: list[str]) -> list[list[float]]:
        """
        Get the text embeddings from the OpenAI API.
        """
        # assert the input is a list of strings
        assert all(isinstance(text, str) for text in texts)

        client = self.client

        response = client.embeddings.create(
            input=texts,
            model="text-embedding-3-small",
        )

        self.embedding_token_usage += response.usage.prompt_tokens

        return [r.embedding for r in response.data]

    def get_text_embeddings(self, text: str) -> list[float]:
        return self.get_text_embeddings_multi([text])[0]
