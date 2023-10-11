import json
import time
import uuid
from typing import List

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import logging

from pydantic import BaseModel

from app.models.OpenCalm7B_chat import OpenCalm7B_Chat

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="LangChain API",
)

class Message(BaseModel):
    role: str
    content: str

class CompletionRequest(BaseModel):
    model: str
    messages: List[Message]
    max_tokens: int
    temperature: float
    stream: bool

async def streaming_response(json_data, chat_generator):
    json_without_choices = json_data.copy()
    json_without_choices["choices"] = [{
        "text": '',
        "index": 0,
        "logprobs": None,
        "finish_reason": 'length',
        "delta": {"content": ''}
    }]

    # logging.info(f"Sending initial JSON: {json_without_choices}")
    yield f"data: {json.dumps(json_without_choices)}\n\n"  # NOTE: EventSource

    def is_only_spaces(s):
        return all(char == ' ' for char in s)

    text = ""
    get_flag = False
    for chunk in chat_generator:
        # logging.info(f"chunk: {chunk}")
        if "# 出力" in chunk:
            get_flag = True
            continue
        if is_only_spaces(chunk):
            continue
        if chunk == "- ":
            continue
        if get_flag:
            new_chunk = chunk.replace("<|endoftext|>", "")
            text += new_chunk
            json_data["choices"][0]["delta"] = {"content": new_chunk}
            # logging.info(f"Sending chunk: {json.dumps(json_data)}")
            yield f"data: {json.dumps(json_data, ensure_ascii=False)}\n\n"  # NOTE: EventSource
        if '<|endoftext|>' in chunk:
            break

    if text == "":
        text = "Sorry, I couldn't understand your message."
        json_data["choices"][0]["text"] = text
        yield f"data: {json.dumps(json_data, ensure_ascii=False)}\n\n"  # NOTE: EventSource
    logging.info(f"reply: {text}:ENDTEXT")
    yield f"data: [DONE]\n\n"  # NOTE: EventSource


@app.get("/v1/models")
async def models():
    return {
        "data": [
            {
                "id": "open-calm-7b",
                "object": "model",
                "owned_by": "organization-owner"
            },
        ],
        "object": "list",
    }


@app.post("/v1/chat/completions")
async def chat_completions(completion_request: CompletionRequest):
    logging.info(f"Received request: {completion_request}")

    history_messages = completion_request.messages[:-1]
    user_message = completion_request.messages[-1]

    if completion_request.model == "open-calm-7b":
        chat = OpenCalm7B_Chat(history_messages)
    else:
        raise ValueError(f"Unknown model: {completion_request.model}")

    json_data = {
        "id": str(uuid.uuid4()),
        "object": "text_completion",
        "created": int(time.time()),
        "model": completion_request.model,
        "choices": [
            {
                "text": "",
                "index": 0,
                "logprobs": None,
                "finish_reason": "length"
            }
        ]
    }

    if completion_request.stream:
        return StreamingResponse(
            streaming_response(json_data, chat.generator(user_message.content)),
            media_type="text/event-stream"
        )
    else:
        return json_data
