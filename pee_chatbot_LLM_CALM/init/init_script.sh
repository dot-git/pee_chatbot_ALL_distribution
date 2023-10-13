#!/bin/bash
#!/bin/sh
if [ "$DOWNLOAD_MODEL" = "true" ]; then
  python3 -c 'from huggingface_hub import snapshot_download; model = "cyberagent/open-calm-small"; download_path = snapshot_download(repo_id=f"{model}", revision="main", local_dir=f"./model/{model}", local_dir_use_symlinks=False)'
fi
exec uvicorn main:app --reload --host 0.0.0.0 --port 8008
