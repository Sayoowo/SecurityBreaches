import kagglehub
import kagglehub, shutil, os

path = kagglehub.dataset_download("muhammadahmerkhan/ai-agent-security-and-real-world-incidents-2024-26")

shutil.copytree(path, "dataset", dirs_exist_ok=True)
print("Copied to:", os.path.abspath("dataset"))
print("Files:", os.listdir("dataset"))