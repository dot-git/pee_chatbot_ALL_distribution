FROM ubuntu:20.04
# FROM nvidia/cuda:11.8.0-devel-ubuntu20.04

USER root

RUN apt-get update && \
    apt-get install -y locales && \
    rm -rf /var/lib/apt/lists/* && \
    locale-gen ja_JP.UTF-8

ENV LC_ALL ja_JP.UTF-8
ENV LANG ja_JP.UTF-8
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ Asia/Tokyo 
ENV PY_VER 3.10.7

RUN apt update && apt install -y \
    wget \
    build-essential \
    libbz2-dev \
    libdb-dev \
    libreadline-dev \
    libffi-dev libgdbm-dev liblzma-dev \
    libncursesw5-dev \
    libsqlite3-dev \
    libssl-dev \
    zlib1g-dev \
    uuid-dev \
    tk-dev \
    git \
    curl \
    vim \
    tree \
    zip \
    tmux \
    file \
    libmecab-dev \
    sudo \
    glibc-source

RUN wget --no-check-certificate https://www.python.org/ftp/python/${PY_VER}/Python-${PY_VER}.tar.xz \
    && tar xJf Python-${PY_VER}.tar.xz \
    && cd Python-${PY_VER} \
    && ./configure --enable-optimizations\
    && make \
    && make install

# packages install
RUN mkdir /app
WORKDIR /app
COPY . /app/

RUN pip3 install --upgrade pip
RUN pip3 install --no-cache-dir -r ./requirements.txt

EXPOSE 8008

COPY init/init_script.sh /init/init_script.sh
RUN chmod +x /init/init_script.sh
ENTRYPOINT ["/init/init_script.sh"]
