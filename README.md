# pee_chatbot_ALL_distribution

最終納品用ファイル

## 環境

- Python 3.10.6
- npm 18.17.0（npm 9.6.7）

## 実行

```zsh
# 事前準備
git clone https://github.com/xxx/pee_chatbot_ALL_distribution.git
cd pee_chatbot_ALL_distribution/pee_chatbot_UI

chmod +x ./docker-entrypoint.sh

docker network ls
docker network rm [NETWORK_NAME]

docker network create chatbot_network
docker compose build --no-cache
docker compose up
```

## 動作確認

http://localhost:3000/
