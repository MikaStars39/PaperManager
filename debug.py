from huggingface_hub import HfApi
import os

api = HfApi(token=os.getenv("HF_TOKEN"))
api.upload_folder(
    folder_path="data",
    repo_id="MikaStars39/MikaDailyPaper",
    repo_type="dataset",
)
