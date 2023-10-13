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

## Google Cloud Platform（GCP）デプロイ

- [PROJECT_NAME]
  - `pee-chatbot-ALL-distribution`
- [PROJECT_ID]
  - `pee-chatbot-all-distribution`

Google Cloud Console で手動で API を有効にする:

    Google Cloud Console にログインします。
    左上のメニューボタンをクリックし、APIs & Services > Dashboard を選択します。
    + ENABLE APIS AND SERVICES ボタンをクリックします。
    xxx API を検索し、選択します。
    ENABLE ボタンをクリックします。

- Cloud Build API
- Artifact Registry API
- Cloud Run API
- Compute Engine API
- VPC ネットワーク用

### Google Cloud SDK をインストールする

```zsh
# 初期化
gcloud init
# Google Cloud にログインする
gcloud auth login
gcloud auth list
# プロジェクト一覧を確認する
gcloud projects list
# 使いたいプロジェクトをセットする
gcloud config set project PROJECT_ID

# プロジェクトを作成する（UIから作成済みの場合は不要）
# gcloud projects create [PROJECT_ID] --name=[PROJECT_NAME]
gcloud projects create pee-chatbot-all-distribution --name="pee-chatbot-ALL-distribution"
# 現在の作業プロジェクトとして設定
# gcloud config set project [PROJECT_ID]
gcloud config set project pee-chatbot-all-distribution
# プロジェクト一覧を確認する
gcloud projects list
```

### Artifact Registry サービスでリポジトリを作成する

```zsh
gcloud artifacts repositories create pee-chatbot-repo --repository-format=docker --location=asia-northeast1
# Create request issued for: [pee-chatbot-repo]
# Waiting for operation [projects/pee-chatbot-all-distribution/locations/asia-nor
# theast1/operations/137a2403-e358-4ff0-a8cf-a8eeb9d37b64] to complete...done.
# Created repository [pee-chatbot-repo].
```

### LLM のイメージはローカルでビルドしてリポジトリにプッシュする

```zsh
# 作業するディレクトリに移動する
cd pee_chatbot_ALL_distribution/pee_chatbot_LLM_CALM

# gcloud builds submit --tag asia-northeast1-docker.pkg.dev/pee-chatbot-all-distribution/pee-chatbot-repo/pee-chatbot-llm --timeout=20m
# gcloud builds submit --tag asia-northeast1-docker.pkg.dev/pee-chatbot-all-distribution/pee-chatbot-repo/pee-chatbot-server --timeout=30m

# -> Arm ワークロード向けのマルチアーキテクチャ イメージのビルドを行うため、ローカルでイメージをビルドする

# ローカルでイメージをビルドする
docker build -t pee-chatbot-llm .
# M1,2 Mac ユーザの場合
# Arm ワークロード向けのマルチアーキテクチャ イメージのビルド（30分から1時間程度かかる）
# https://cloud.google.com/kubernetes-engine/docs/how-to/build-multi-arch-for-arm?hl=ja
docker build --platform linux/amd64 -t pee-chatbot-llm .

# Cloud Run にデプロイする前に、一度ローカルで起動して動作確認を行います。
# ローカルで起動するには、次のコマンドを実行します。
docker run -p 8008:8008 pee-chatbot-llm

# コマンドでタグをつける
# このコマンドは2つの引数を必要とし、1つ目はソースイメージ名で、2つ目はターゲットイメージ名です。
# ソースイメージは既存のDockerイメージを指し、ターゲットイメージは新しいタグ名を指します。
# また、タグ名はオプションであり、指定されていない場合はlatestがデフォルトとして使用されます。
# docker tag SOURCE_IMAGE[:TAG] TARGET_IMAGE[:TAG]
# 例えば、ソースイメージ名がpee-chatbot-llmで、ターゲットイメージ名がasia-northeast1-docker.pkg.dev/course-llm/pee-chatbot-repo/pee-chatbot-llmである場合、次のようにコマンドを実行します：
# このコマンドは、pee-chatbot-llmという名前の既存のDockerイメージに新しいタグasia-northeast1-docker.pkg.dev/course-llm/pee-chatbot-repo/pee-chatbot-llmを作成します。
docker tag pee-chatbot-llm asia-northeast1-docker.pkg.dev/pee-chatbot-all-distribution/pee-chatbot-repo/pee-chatbot-llm

# Docker クライアントの認証を Google Cloud asia-northeast1-docker.pkg.dev レジストリに対して構成する
# プロンプトに Y と入力することで、指定された設定が Docker の設定ファイルに書き込まれ、それによりDocker は指定されたレジストリに対して認証を行うように構成されます。
gcloud auth configure-docker asia-northeast1-docker.pkg.dev

# ローカルのDockerイメージをリモートのイメージリポジトリにプッシュする
# asia-northeast1-docker.pkg.dev/course-llm/pee-chatbot-repo/pee-chatbot-llmというタグが付けられたローカルのDockerイメージをasia-northeast1-docker.pkg.devというリモートのリポジトリにプッシュするには、次のコマンドを実行します。
docker push asia-northeast1-docker.pkg.dev/pee-chatbot-all-distribution/pee-chatbot-repo/pee-chatbot-llm
```

### Cloud Build で API サーバの docker イメージをビルドして、リポジトリにプッシュ

```zsh
# 作業するディレクトリに移動する
cd pee_chatbot_ALL_distribution/pee_chatbot_server

# コマンドでビルド＆プッシュする
# Google Cloud Build を使用してソースコードをビルドし、ビルドされたイメージを Artifact Registry にプッシュする
# ソースコードをビルドし、ビルドされた Docker イメージを asia-northeast1-docker.pkg.dev/pee-chatbot-all-distribution/pee-chatbot-repo/pee-chatbot-server というタグでリモートのリポジトリにプッシュするには、次のコマンドを実行します。
# gcloud builds submit --tag asia-northeast1-docker.pkg.dev/pee-chatbot-all-distribution/pee-chatbot-repo/pee-chatbot-server

# -> Arm ワークロード向けのマルチアーキテクチャ イメージのビルドを行うため、ローカルでイメージをビルドする

# ローカルでイメージをビルドする
docker build -t pee-chatbot-server .
# M1,2 Mac ユーザの場合
docker build --platform linux/amd64 -t pee-chatbot-server .

# Cloud Run にデプロイする前に、一度ローカルで起動して動作確認を行います。
# ローカルで起動するには、次のコマンドを実行します。
docker run -p 8000:8000 pee-chatbot-server

# コマンドでタグをつける
docker tag pee-chatbot-server asia-northeast1-docker.pkg.dev/pee-chatbot-all-distribution/pee-chatbot-repo/pee-chatbot-server

# Docker クライアントの認証を Google Cloud asia-northeast1-docker.pkg.dev レジストリに対して構成する
gcloud auth configure-docker asia-northeast1-docker.pkg.dev

# ローカルのDockerイメージをリモートのイメージリポジトリにプッシュする
docker push asia-northeast1-docker.pkg.dev/pee-chatbot-all-distribution/pee-chatbot-repo/pee-chatbot-server
```

### Cloud Build で UI の docker イメージをビルドして、リポジトリにプッシュ

```zsh
# 作業するディレクトリに移動する
cd pee_chatbot_ALL_distribution/pee_chatbot_UI

# gcloud builds submit --tag asia-northeast1-docker.pkg.dev/pee-chatbot-all-distribution/pee-chatbot-repo/pee-chatbot-ui

# -> Arm ワークロード向けのマルチアーキテクチャ イメージのビルドを行うため、ローカルでイメージをビルドする

# ローカルでイメージをビルドする
docker build -t pee-chatbot-ui .
# M1,2 Mac ユーザの場合
docker build --platform linux/amd64 -t pee-chatbot-ui .

# Cloud Run にデプロイする前に、一度ローカルで起動して動作確認を行います。
# ローカルで起動するには、次のコマンドを実行します。
docker run -p 3000:3000 pee-chatbot-ui

# コマンドでタグをつける
docker tag pee-chatbot-ui asia-northeast1-docker.pkg.dev/pee-chatbot-all-distribution/pee-chatbot-repo/pee-chatbot-ui

# Docker クライアントの認証を Google Cloud asia-northeast1-docker.pkg.dev レジストリに対して構成する
gcloud auth configure-docker asia-northeast1-docker.pkg.dev

# ローカルのDockerイメージをリモートのイメージリポジトリにプッシュする
docker push asia-northeast1-docker.pkg.dev/pee-chatbot-all-distribution/pee-chatbot-repo/pee-chatbot-ui
```

### LLM を内部から呼び出せる形でデプロイする

```zsh
# Google Cloud Runにサービスをデプロイする
    # --region asia-northeast1: サービスをasia-northeast1リージョンにデプロイします。
    # --allow-unauthenticated: 認証なしでサービスにアクセスできるようにします。
    # --image asia-northeast1-docker.pkg.dev/pee-chatbot-all-distribution/pee-chatbot-repo/pee-chatbot-llm: デプロイするDockerイメージのパスを指定します。
    # --port 8008: サービスがリッスンするポートを8008に設定します。
    # --memory 3Gi: サービスのメモリ制限を3ギビバイトに設定します。
    # --ingress internal-and-cloud-load-balancing: イングレスの設定をinternal-and-cloud-load-balancingに設定します。
      # --ingress internal-and-cloud-load-balancing を指定し、内部または Cloud Load Balancing のみからのアクセスを許可します。
      # これを指定しないと、外部ネットワークから Cloud Load Balancing を通さずにアクセスできてしまいます。
      # その他の認証をかけない場合は --allow-unauthenticated も付与します。
gcloud run deploy pee-chatbot-llm-service --region asia-northeast1 --allow-unauthenticated --image asia-northeast1-docker.pkg.dev/pee-chatbot-all-distribution/pee-chatbot-repo/pee-chatbot-llm --port 8008 --memory 3Gi --ingress internal-and-cloud-load-balancing

# エラーが出たので、色々と設定項目を外して、極力単純な方法でデプロイしてみる
# gcloud run deploy pee-chatbot-llm-service --region asia-northeast1 --image asia-northeast1-docker.pkg.dev/pee-chatbot-all-distribution/pee-chatbot-repo/pee-chatbot-llm --port 8008 --memory 3Gi
```

pee-chatbot-inner
pee-chatbot-alb
pee-chatbot-alb-backend
pee-chatbot-endpoint-group

10.146.0.2:80

### チャットボットの API サーバをデプロイする

```zsh
gcloud run deploy pee-chatbot-api-service --region asia-northeast1 --allow-unauthenticated --image asia-northeast1-docker.pkg.dev/pee-chatbot-all-distribution/pee-chatbot-repo/pee-chatbot-server --port 8000 --set-env-vars="OPENCALM_SERVER_HOST=https://10.146.0.2"
```

https://pee-chatbot-api-service-l2f226knga-an.a.run.app

```zsh
curl -X POST "https://pee-chatbot-api-service-l2f226knga-an.a.run.app/v1/chat/completions" -H "accept: text/event-stream" -H "Content-Type: application/json" --data '{"model": "open-calm-7b", "messages": [{"role": "system", "content": "あなたは日本の専門家です。"}, {"role": "user", "content": "以下は、タスクを説明する指示と、文脈のある入力の組み合わせです。\n要求を適切に満たす応答を書きなさい。\n\n# 指示\n大阪城について教えてください。\n\n# 出力"}], "max_tokens": 128, "temperature": 0.1, "stream": true}'
```

```json
{
  "model": "open-calm-7b",
  "messages": [
    {
      "role": "system",
      "content": "あなたは日本の専門家です。"
    },
    {
      "role": "user",
      "content": "以下は、タスクを説明する指示と、文脈のある入力の組み合わせです。\n要求を適切に満たす応答を書きなさい。\n\n# 指示\n大阪城について教えてください。\n\n# 出力"
    }
  ],
  "max_tokens": 128,
  "temperature": 0.1,
  "stream": true
}
```

### チャットボットの UI をデプロイ

```zsh
gcloud run deploy pee-chatbot-ui-service --region asia-northeast1 --allow-unauthenticated --image asia-northeast1-docker.pkg.dev/pee-chatbot-all-distribution/pee-chatbot-repo/pee-chatbot-ui --port 3000 --set-env-vars="OPENAI_API_HOST=https://pee-chatbot-api-service-l2f226knga-an.a.run.app"
```

## 参考資料

- ビルドするマシンと実行するマシンの CPU アーキテクチャが異なっていると起動に失敗する
  - <a href="https://zenn.dev/yutan/articles/bc0ef89b15d2ba" title="CloudRunのデプロイに失敗した時のメモ（failed to load /bin/sh: exec format error）" target="_blank">CloudRun のデプロイに失敗した時のメモ（failed to load /bin/sh: exec format error）</a>
  - <a href="https://zenn.dev/msksgm/scraps/d667e2b2eecf4e" title="GCP 初心者の M1 Mac ユーザーが Cloud Run にデプロイするときにドツボにはまったこと" target="_blank">GCP 初心者の M1 Mac ユーザーが Cloud Run にデプロイするときにドツボにはまったこと</a>
  - <a href="https://cloud.google.com/kubernetes-engine/docs/how-to/build-multi-arch-for-arm?hl=ja" title="Arm ワークロード向けのマルチアーキテクチャ イメージのビルド  |  Google Kubernetes Engine（GKE）  |  Google Cloud" target="_blank">Arm ワークロード向けのマルチアーキテクチャ イメージのビルド  |  Google Kubernetes Engine（GKE）  |  Google Cloud</a>
- <a href="https://cloud.google.com/sdk/docs/install-sdk?hl=ja" title="クイックスタート: Google Cloud CLI をインストールする  |  Google Cloud CLI のドキュメント" target="_blank">クイックスタート: Google Cloud CLI をインストールする  |  Google Cloud CLI のドキュメント</a>
- <a href="https://zenn.dev/kazumax4395/articles/66ec5c259c950c#cloud-armor" title="【GCP/Next.js】Cloud Runを使用したインフラ構築" target="_blank">【GCP/Next.js】Cloud Run を使用したインフラ構築</a>
- <a href="https://cloud.google.com/load-balancing/docs/l7-internal/setting-up-l7-internal-serverless?hl=ja" title="Cloud Run を使用してリージョン内部アプリケーション ロードバランサを設定します。  |  負荷分散  |  Google Cloud" target="_blank">Cloud Run を使用してリージョン内部アプリケーション ロードバランサを設定します。  |  負荷分散  |  Google Cloud</a>
- <a href="https://cloud.google.com/load-balancing/docs/https/setting-up-reg-ext-https-serverless?hl=ja" title="Cloud Run を使用してリージョン外部アプリケーション ロードバランサを設定します。  |  負荷分散  |  Google Cloud" target="_blank">Cloud Run を使用してリージョン外部アプリケーション ロードバランサを設定します。  |  負荷分散  |  Google Cloud</a>
- <a href="https://qiita.com/nekoshita_yuki/items/95d2d6a889629a557c54#%E3%82%B5%E3%83%BC%E3%83%90%E3%83%BC%E3%83%AC%E3%82%B9vpc%E3%82%A2%E3%82%AF%E3%82%BB%E3%82%B9%E3%81%A3%E3%81%A6" title="Google Cloud Run の個人的なQ&A（2021年2月現在） - Qiita" target="_blank">Google Cloud Run の個人的な Q&A（2021 年 2 月現在） - Qiita</a>
