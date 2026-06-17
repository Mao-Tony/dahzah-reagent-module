"""
MiniMax VL 视觉识别工具

集成到主项目时，请使用主项目的 app/platform/ai/minimax_util.py 实现。
此处提供简化版本用于独立测试。
"""

import base64
import httpx
from typing import Optional, List, Dict, Any
import json


class VisionResult:
    """视觉识别结果"""

    def __init__(self, content: str, usage: Optional[Dict] = None):
        self.content = content
        self.usage = usage or {}


def encode_image_to_base64(image_path: str) -> str:
    """将图片文件编码为base64字符串"""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def get_vision_util(
    api_key: str,
    base_url: str = "https://api.minimax.chat",
    model: str = "MiniMax-VL-01"
):
    """
    获取视觉识别工具实例

    Args:
        api_key: MiniMax API密钥
        base_url: API基础URL
        model: 模型名称

    Returns:
        VisionUtil 实例
    """
    return VisionUtil(api_key, base_url, model)


class VisionUtil:
    """MiniMax VL 视觉识别工具

    集成到主项目时，请使用主项目的完整实现。
    """

    def __init__(self, api_key: str, base_url: str, model: str):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model

    async def recognize(
        self,
        image_urls: List[str],
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> VisionResult:
        """
        识别图片内容

        Args:
            image_urls: 图片URL列表
            prompt: 识别提示词
            temperature: 温度参数
            max_tokens: 最大token数

        Returns:
            VisionResult: 识别结果
        """
        # 读取本地图片文件
        images_content = []
        for url in image_urls:
            if url.startswith("http"):
                # 如果是URL，先下载
                try:
                    async with httpx.AsyncClient(timeout=30.0) as client:
                        response = await client.get(url)
                        if response.status_code == 200:
                            images_content.append(base64.b64encode(response.content).decode("utf-8"))
                except Exception:
                    pass
            else:
                # 本地文件路径
                try:
                    path = url.replace("file://", "")
                    images_content.append(encode_image_to_base64(path))
                except Exception:
                    pass

        if not images_content:
            return VisionResult(content="无法读取图片内容")

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/v1/text/chatfish_pro",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": prompt}
                                ] + [
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": f"data:image/jpeg;base64,{img}"
                                        }
                                    }
                                    for img in images_content
                                ]
                            }
                        ],
                        "temperature": temperature,
                        "max_tokens": max_tokens
                    }
                )

                if response.status_code == 200:
                    result = response.json()
                    content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                    usage = result.get("usage", {})
                    return VisionResult(content=content, usage=usage)
                else:
                    return VisionResult(content=f"API错误: {response.status_code}")

        except Exception as e:
            return VisionResult(content=f"识别失败: {str(e)}")
