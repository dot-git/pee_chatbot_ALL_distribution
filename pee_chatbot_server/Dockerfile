FROM python:3.10.6-slim-bullseye

ENV LANG ja_JP.UTF-8
ENV LANGUAGE ja_JP:ja
ENV LC_ALL ja_JP.UTF-8
ENV TZ JST-9

RUN pip install --upgrade pip
RUN pip install poetry

WORKDIR /work

COPY app/ /work/app
COPY pyproject.toml /work/pyproject.toml

RUN poetry config virtualenvs.create false
RUN poetry install

EXPOSE 8000
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port 8000"]