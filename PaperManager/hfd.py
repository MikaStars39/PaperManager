from huggingface_hub import HfApi
import os

def upload_to_hf(folder_path: str, repo_id: str, repo_type: str, hf_token: str = None):
    if hf_token is None:
        hf_token = os.getenv("HF_TOKEN")
    api = HfApi(token=hf_token)
    api.upload_folder(
        folder_path=folder_path,
        repo_id=repo_id,
        repo_type=repo_type,
    )