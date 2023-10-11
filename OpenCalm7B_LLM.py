from langchain.llms.base import LLM
from langchain.callbacks.manager import CallbackManagerForLLMRun

from functools import partial
from typing import Any, Iterator, List, Mapping, Optional
from text_generation.types import StreamResponse, Parameters, Request
from text_generation.errors import parse_error
from pydantic import ValidationError

import requests
import json
import os


class OpenCalm7B_LLM(LLM):
    @property
    def _llm_type(self) -> str:
        return "OpenCalm7B"

    def generate_stream(
        self,
        prompt: str,
        do_sample: bool = False,
        max_new_tokens: int = 128,
        temperature: Optional[float] = None,
    ) -> Iterator[StreamResponse]:
        parameters = Parameters(
            max_new_tokens=max_new_tokens,
            do_sample=do_sample,
            temperature=temperature,
        )
        prompt = prompt.replace("\n", "")
        prompt = prompt.replace('"', "")
        request = Request(inputs=prompt, stream=True, parameters=parameters)

        print(request.dict())

        hostname = os.getenv("OPENCALM_SERVER_HOST", default="http://127.0.0.1:8008")
        # port = os.getenv("OPENCALM_SERVER_PORT", default="8008")

        resp = requests.post(
            f"{hostname}/api/chat-stream/",
            json=request.dict(),
            timeout=120,
            stream=True,
        )

        if resp.status_code != 200:
            raise parse_error(resp.status_code, resp.json())

        for byte_payload in resp.iter_lines():
            if byte_payload == b"\n":
                continue

            payload = byte_payload.decode("utf-8")

            if payload.startswith("data:"):
                json_payload = json.loads(payload.lstrip("data:").rstrip("/n"))
                try:
                    response = StreamResponse(**json_payload)
                    yield response
                except ValidationError:
                    raise parse_error(resp.status_code, json_payload)

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
    ) -> str:
        if stop is not None:
            raise ValueError("stop kwargs are not permitted.")

        text_callback = None
        if run_manager:
            text_callback = partial(run_manager.on_llm_new_token, verbose=self.verbose)

        params = {
            "max_new_tokens": 128,
            "do_sample": True,
            "temperature": 0.1,
        }

        text = ""
        for res in self.generate_stream(prompt, **params):
            token = res.token

            if not token.special:
                if text_callback:
                    text_callback(token.text)
                text += token.text

        return text
