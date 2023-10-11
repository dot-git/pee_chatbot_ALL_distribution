# pee_chatbot_LLM_CALM
pee_chatbot_LLM_CALM

## 環境

### ■ ソフトウェア・ライブラリ

- Python 3.10.7
- FastAPI 0.95.0
- transformers 4.29.2
- open-calm-small（ https://huggingface.co/cyberagent/open-calm-small ）

### ■ ハードウェア

- ディスク空き容量　約3GB（pythonライブラリ約2GB、OpenCalmモデル約400MB）

## 実行

```zsh
# 事前準備
git clone https://github.com/xxx/pee_chatbot_LLM_CALM.git
cd pee_chatbot_LLM_CALM

docker network create chatbot_network
docker-compose build --no-cache
docker compose up
```
