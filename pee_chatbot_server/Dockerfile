FROM python:3.10.6-slim-bullseye

ENV LANG ja_JP.UTF-8
ENV LANGUAGE ja_JP:ja
ENV LC_ALL ja_JP.UTF-8
ENV TZ JST-9

ENV OPENCALM_SERVER_HOST 127.0.0.1
ENV OPENCALM_SERVER_PORT 8008

WORKDIR /work

COPY app/ /work/app
COPY pyproject.toml /work
COPY README.md /work

RUN pip install --upgrade pip
RUN pip install poetry
RUN poetry install

EXPOSE 8000
# CMD [ "poetry", "run", "python", "app/main.py" ]
# ->
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port 8000"]