from fastapi import FastAPI
from fastapi.responses import StreamingResponse

from pydantic import BaseModel

import asyncio
from threading import Thread
from typing import AsyncIterator

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, TextIteratorStreamer
import logging

logging.basicConfig(level=logging.INFO)

# MODEL_PATH = 'cyberagent/open-calm-small'
MODEL_PATH = 'cyberagent/open-calm-small-inst'

model = AutoModelForCausalLM.from_pretrained(
    f'./model/{MODEL_PATH}'
)
tokenizer = AutoTokenizer.from_pretrained(f'./model/{MODEL_PATH}')

class opencalm_request(BaseModel):
    inputs: str
    parameters: dict | None = None
    stream: bool = True

def request2prompt_calm(request):
    print(request.inputs)
    request.inputs = request.inputs.replace('\n', '')
    request.inputs = request.inputs.replace('\"', '')
    request.inputs = request.inputs.lstrip('{').rstrip('}')
    print(request.inputs)
    return request.inputs

async def generate_stream(request) -> AsyncIterator[str]:
    prompt = request2prompt_calm(request)
    inputs = tokenizer(prompt, add_special_tokens=False, return_tensors="pt")
    streamer = TextIteratorStreamer(tokenizer)

    generation_kwargs = dict(
        inputs.to(model.device),
        streamer=streamer,
        max_new_tokens=request.parameters['max_new_tokens'],
        do_sample=request.parameters['do_sample'],
        temperature=request.parameters['temperature'],
        pad_token_id=tokenizer.pad_token_id,
        bos_token_id=tokenizer.bos_token_id,
        eos_token_id=tokenizer.eos_token_id,
        bad_words_ids=[[tokenizer.bos_token_id]],
        num_return_sequences=1,
        top_p=0.9,
        repetition_penalty=1.05,
    )

    thread = Thread(target=model.generate, kwargs=generation_kwargs)
    thread.start()

    seq = 1
    for output in streamer:
        # logging.info(f"output: {output}")
        if not output:
            continue

        output = output.replace('\n',' ')
        yield "data:{\"token\":{\"id\":" + str(seq) + ", \"text\":\"" + output + "\",\"logprob\":0.0,\"special\":false}}" + '\n'
        seq += 1
        await asyncio.sleep(0)

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "I'm LLM API"}

@app.post("/api/chat-stream/")
async def response_stream(request: opencalm_request):
    return StreamingResponse(generate_stream(request))
