import os
import uuid
from fastapi import UploadFile

def save_temp_file(file: UploadFile, dir_path: str = "tmp") -> str:
    os.makedirs(dir_path, exist_ok=True)
    extension = file.filename.split('.')[-1]
    temp_filename = f"{uuid.uuid4()}.{extension}"
    temp_path = os.path.join(dir_path, temp_filename)

    with open(temp_path, "wb") as f:
        f.write(file.file.read())

    return temp_path