"""
平台模块 - 包含数据库和AI服务

集成到主项目时，这些导入会被主项目的实际模块替代。
"""

from app.platform.database import get_db_session

__all__ = ["get_db_session"]
