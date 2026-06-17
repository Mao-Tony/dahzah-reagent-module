"""
AI配置API接口
提供AI配置的获取和更新功能
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

router = APIRouter(prefix="/api/v1/ai-config", tags=["AI配置"])


def get_db():
    """数据库会话依赖"""
    from database import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class AIConfigUpdate(BaseModel):
    """AI配置更新模型"""
    enabled: Optional[bool] = None
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    prompt_template: Optional[str] = None
    image_analysis_prompt: Optional[str] = None
    label_recognition_prompt: Optional[str] = None


class AIConfigResponse(BaseModel):
    """AI配置响应模型"""
    enabled: bool = False
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model: str = "MiniMax/VL-01"
    max_tokens: int = 2048
    temperature: float = 0.7
    prompt_template: Optional[str] = None
    image_analysis_prompt: Optional[str] = None
    label_recognition_prompt: Optional[str] = None
    updated_at: Optional[datetime] = None


@router.get("/", response_model=AIConfigResponse)
async def get_ai_config(db: Session = Depends(get_db)):
    """
    获取当前AI配置
    """
    from ai_config import ai_config
    ai_config.init(db)

    config = ai_config.get_all()
    return AIConfigResponse(
        enabled=config.get("enabled", False),
        api_key=config.get("api_key"),
        base_url=config.get("base_url"),
        model=config.get("model", "MiniMax/VL-01"),
        max_tokens=config.get("max_tokens", 2048),
        temperature=config.get("temperature", 0.7),
        prompt_template=config.get("prompt_template"),
        image_analysis_prompt=config.get("image_analysis_prompt"),
        label_recognition_prompt=config.get("label_recognition_prompt"),
        updated_at=config.get("updated_at")
    )


@router.post("/", response_model=AIConfigResponse)
async def update_ai_config(
    config_update: AIConfigUpdate,
    db: Session = Depends(get_db)
):
    """
    更新AI配置
    """
    from ai_config import ai_config
    ai_config.init(db)

    update_data = config_update.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(status_code=400, detail="没有提供需要更新的配置项")

    ai_config.update(update_data)
    ai_config.set("updated_at", datetime.now())
    ai_config.save_config()

    return AIConfigResponse(
        enabled=ai_config.is_enabled(),
        api_key=ai_config.get_api_key(),
        base_url=ai_config.get_base_url(),
        model=ai_config.get_model(),
        max_tokens=ai_config.get_max_tokens(),
        temperature=ai_config.get_temperature(),
        prompt_template=ai_config.get("prompt_template"),
        image_analysis_prompt=ai_config.get("image_analysis_prompt"),
        label_recognition_prompt=ai_config.get("label_recognition_prompt"),
        updated_at=ai_config.get("updated_at")
    )


@router.get("/status")
async def get_ai_status(db: Session = Depends(get_db)):
    """
    获取AI服务状态
    """
    from ai_config import ai_config
    ai_config.init(db)

    enabled = ai_config.is_enabled()
    has_api_key = bool(ai_config.get_api_key())
    has_base_url = bool(ai_config.get_base_url())

    return {
        "enabled": enabled,
        "configured": enabled and has_api_key and has_base_url,
        "message": "AI功能已配置" if (enabled and has_api_key and has_base_url) else "AI功能未完整配置"
    }


@router.post("/test")
async def test_ai_connection(
    config_test: AIConfigUpdate,
    db: Session = Depends(get_db)
):
    """
    测试AI连接
    """
    api_key = config_test.api_key
    base_url = config_test.base_url

    if not api_key or not base_url:
        raise HTTPException(status_code=400, detail="API密钥和基础URL都是必需的")

    try:
        import httpx
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{base_url.rstrip('/')}/v1/text/chatfish_pro",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": config_test.model or "MiniMax/VL-01",
                    "messages": [{"role": "user", "content": "Hello"}],
                    "max_tokens": 10
                }
            )

            if response.status_code == 200:
                return {"success": True, "message": "连接测试成功"}
            else:
                return {"success": False, "message": f"连接失败: {response.status_code}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"连接测试失败: {str(e)}")
