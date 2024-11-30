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
    def __init__(
        self,
        llm_model: str = "gpt-3.5-turbo",
        api_key: str = None,
        log_folder: str = None,
    ):
        if "gpt" in llm_model:
            self.llm_handler = GPTHandler(llm_model, api_key, log_folder)
        elif "gemini" in llm_model:
            self.llm_handler = GeminiHandler(llm_model, api_key, log_folder)
        else:
            raise ValueError("Invalid LLM model")
        
    def chat_with_gpt(self, messages: Union[ChatSequence, list[dict], str], **kwargs) -> str:
        return self.llm_handler.chat(messages, **kwargs)
    

class BaseLLMHandler:
    log_count = 0
    prompt_token_usage = 0
    completion_token_usage = 0
    embedding_token_usage = 0

    def __init__(
        self,
        llm_model: str = "gpt-3.5-turbo",
        api_key: str = None,
        log_folder: str = None,
    ):
        self.llm_model = llm_model
        self.log_folder = log_folder

        # create the log folder if it doesn't exist
        if log_folder:
            if not os.path.exists(self.log_folder):
                os.makedirs(self.log_folder)

    def chat(
        self, messages: Union[ChatSequence, list[dict], str], **kwargs
    ) -> str:
        # if messages is a ChatSequence, convert it to a list of dicts
        if isinstance(messages, ChatSequence):
            messages = messages.raw()
        # if messages is a string, convert it to a list of dicts
        if isinstance(messages, str):
            messages = [{"role": "user", "content": messages}]

        # save the messages to a file
        self.save_messages(messages)

        # connect to APIs
        content = self.connect_to_api(messages, **kwargs)

        self.save_messages([{"role": "assistant", "content": content}])
        return content
    
    def connect_to_api(self, messages: list[dict], **kwargs):
        raise NotImplementedError

    def save_messages(self, messages: list[dict]):
        if not self.log_folder:
            return
        with open(
            f"{self.log_folder}/{self.log_count}.txt", "w", encoding="utf-8"
        ) as f:
            for message in messages:
                f.write(f'{message["role"]}: ')
                f.write(f'{message["content"]}\n')
        self.log_count += 1


class GPTHandler(BaseLLMHandler):
    def __init__(
            self, 
            llm_model: str = "gpt-3.5-turbo", 
            api_key: str = None, 
            log_folder: str = None
            ):
        super().__init__(llm_model, api_key, log_folder)
        if api_key:
            self.client = OpenAI(api_key=api_key)
        else:
            self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    def connect_to_api(self, messages: list[dict], **kwargs):
        try:
            response = self.client.chat.completions.create(
                model=self.llm_model, messages=messages, **kwargs
            )
        except Exception as err:
            logging.error(f"OPENAI ERROR: {err}")
            raise err

        content = response.choices[0].message.content
        self.prompt_token_usage += response.usage.prompt_tokens
        self.completion_token_usage += response.usage.completion_tokens
        return content
    

class GeminiHandler(BaseLLMHandler):
    def __init__(
            self, 
            llm_model: str = "gemini-1.5-flash", 
            api_key: str = None, 
            log_folder: str = None
            ):
        super().__init__(llm_model, api_key, log_folder)
        if api_key:
            self.client = OpenAI(api_key=api_key, base_url="https://generativelanguage.googleapis.com/v1beta/")
        else:
            self.client = OpenAI(api_key=os.environ.get("GEMINI_API_KEY"), base_url="https://generativelanguage.googleapis.com/v1beta/")

    def connect_to_api(self, messages: list[dict], **kwargs):
        try:
            response = self.client.chat.completions.create(
                model=self.llm_model, messages=messages, **kwargs
            )
        except Exception as err:
            logging.error(f"GOOGLE ERROR: {err}")
            raise err
        content = response.choices[0].message.content
        return content


# Example usage
if __name__ == "__main__":
    llm_handler = LLMHandler(llm_model="gemini-1.5-flash")
    messages = ChatSequence()
    messages.append(Message("user", "Hello!"))

    response = llm_handler.chat_with_gpt(messages)
    print(response)
