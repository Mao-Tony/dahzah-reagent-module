"""
AI日志服务

集成到主项目时，请使用主项目的 app/platform/ai/service.py 实现。
此处提供简化版本用于独立测试。
"""

from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

# 尝试导入主项目的AI日志服务，如果不存在则使用模块内的实现
try:
    from app.platform.ai.models import QmsAiLog
except ImportError:
    # 回退到模块内的实现
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
    try:
        from ai.models import QmsAiLog
    except ImportError:
        # 定义一个简单的日志模型（如果都不可用）
        class QmsAiLog:
            pass


class AiLogService:
    """AI日志服务类

    集成到主项目时，请使用主项目的完整实现。
    此处提供简化版本用于独立测试。
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_log(
        self,
        module: str,
        action: str,
        prompt: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        response: Optional[str] = None,
        model: Optional[str] = None,
        tokens_used: Optional[int] = None,
        status: str = "success",
        error_message: Optional[str] = None,
        request_params: Optional[Dict[str, Any]] = None,
        response_time: Optional[float] = None
    ):
        """
        创建AI日志记录

        集成到主项目时使用主项目的完整实现。
        """
        # 尝试使用主项目的日志服务
        try:
            from ai.service import AiLogService as ModuleAiLogService
            service = ModuleAiLogService(self.session)
            return await service.create_log(
                module=module,
                action=action,
                prompt=prompt,
                user_id=user_id,
                session_id=session_id,
                response=response,
                model=model,
                tokens_used=tokens_used,
                status=status,
                error_message=error_message,
                request_params=request_params,
                response_time=response_time
            )
        except (ImportError, Exception):
            # 独立模式 - 简化实现
            print(f"[AI Log] {module}/{action}: {status}")
            return None
