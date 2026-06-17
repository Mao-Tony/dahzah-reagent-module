"""
文件存储工具

集成到主项目时，请使用主项目的 app/core/storage.py 实现。
此处提供简化版本用于独立测试。
"""

import os
import shutil
import uuid
from datetime import datetime
from typing import List
from fastapi import UploadFile


# 默认上传目录
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
REAGENT_LABELS_DIR = os.path.join(UPLOAD_DIR, "reagent-labels")


def ensure_dir(path: str):
    """确保目录存在"""
    os.makedirs(path, exist_ok=True)


async def save_upload_files(
    files: List[UploadFile],
    sub_dir: str = "reagent-labels"
) -> List[str]:
    """
    保存上传的文件

    Args:
        files: 上传的文件列表
        sub_dir: 子目录名称

    Returns:
        保存后的文件URL列表
    """
    upload_path = os.path.join(UPLOAD_DIR, sub_dir)
    ensure_dir(upload_path)

    saved_urls = []

    for file in files:
        # 生成唯一文件名
        ext = os.path.splitext(file.filename)[1] if file.filename else ".jpg"
        filename = f"{uuid.uuid4().hex}{ext}"
        file_path = os.path.join(upload_path, filename)

        # 保存文件
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # 生成URL（相对路径）
        saved_urls.append(f"/uploads/{sub_dir}/{filename}")

    return saved_urls


def delete_file(file_url: str) -> bool:
    """
    删除文件

    Args:
        file_url: 文件URL

    Returns:
        是否删除成功
    """
    if file_url.startswith("/"):
        # 转换为本地路径
        relative_path = file_url.lstrip("/")
        if relative_path.startswith("uploads/"):
            file_path = relative_path
        else:
            file_path = os.path.join(UPLOAD_DIR, relative_path)
    else:
        file_path = file_url

    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
    except Exception:
        pass

    return False


def get_file_path(file_url: str) -> str:
    """
    获取文件的完整路径

    Args:
        file_url: 文件URL

    Returns:
        完整文件路径
    """
    if file_url.startswith("/"):
        relative_path = file_url.lstrip("/")
        if relative_path.startswith("uploads/"):
            return relative_path
        return os.path.join(UPLOAD_DIR, relative_path)
    return file_url
