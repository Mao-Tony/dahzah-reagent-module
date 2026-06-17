"""
AI日志数据模型
定义AI交互日志的数据库结构
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.sql import func
from database import Base


class QmsAiLog(Base):
    """
    AI交互日志表
    记录所有AI功能的调用日志
    """
    __tablename__ = "qms_ai_log"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String(100), nullable=True, index=True, comment="用户ID")
    session_id = Column(String(100), nullable=True, index=True, comment="会话ID")
    module = Column(String(50), nullable=False, index=True, comment="模块名称")
    action = Column(String(50), nullable=False, index=True, comment="操作类型")
    prompt = Column(Text, nullable=False, comment="发送的提示词")
    response = Column(Text, nullable=True, comment="AI响应内容")
    model = Column(String(100), nullable=True, comment="使用的模型")
    tokens_used = Column(Integer, nullable=True, comment="使用的token数")
    status = Column(String(20), nullable=False, default="success", comment="状态: success/failed")
    error_message = Column(Text, nullable=True, comment="错误信息")
    request_params = Column(JSON, nullable=True, comment="请求参数")
    response_time = Column(Integer, nullable=True, comment="响应时间(毫秒)")
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="创建时间")

    def __repr__(self):
        return f"<QmsAiLog(id={self.id}, module='{self.module}', action='{self.action}', status='{self.status}')>"

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "module": self.module,
            "action": self.action,
            "prompt": self.prompt,
            "response": self.response,
            "model": self.model,
            "tokens_used": self.tokens_used,
            "status": self.status,
            "error_message": self.error_message,
            "request_params": self.request_params,
            "response_time": self.response_time,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
