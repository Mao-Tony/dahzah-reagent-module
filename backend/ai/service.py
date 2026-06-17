"""
AI日志服务
提供AI交互日志的创建和管理功能
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc

from ai.models import QmsAiLog


class AiLogService:
    """AI日志服务类"""

    def __init__(self, db: Session):
        self.db = db

    def create_log(
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
    ) -> QmsAiLog:
        """
        创建AI日志记录

        Args:
            module: 模块名称
            action: 操作类型
            prompt: 发送的提示词
            user_id: 用户ID
            session_id: 会话ID
            response: AI响应内容
            model: 使用的模型
            tokens_used: 使用的token数
            status: 状态
            error_message: 错误信息
            request_params: 请求参数
            response_time: 响应时间(毫秒)

        Returns:
            QmsAiLog: 创建的日志记录
        """
        log = QmsAiLog(
            user_id=user_id,
            session_id=session_id,
            module=module,
            action=action,
            prompt=prompt,
            response=response,
            model=model,
            tokens_used=tokens_used,
            status=status,
            error_message=error_message,
            request_params=request_params,
            response_time=response_time
        )

        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)

        return log

    def get_logs(
        self,
        page: int = 1,
        page_size: int = 20,
        module: Optional[str] = None,
        action: Optional[str] = None,
        status: Optional[str] = None,
        user_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> tuple[List[QmsAiLog], int]:
        """
        获取AI日志列表

        Args:
            page: 页码
            page_size: 每页数量
            module: 模块名称
            action: 操作类型
            status: 状态
            user_id: 用户ID
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            tuple: (日志列表, 总数)
        """
        query = self.db.query(QmsAiLog)

        if module:
            query = query.filter(QmsAiLog.module == module)
        if action:
            query = query.filter(QmsAiLog.action == action)
        if status:
            query = query.filter(QmsAiLog.status == status)
        if user_id:
            query = query.filter(QmsAiLog.user_id == user_id)
        if start_date:
            query = query.filter(QmsAiLog.created_at >= start_date)
        if end_date:
            query = query.filter(QmsAiLog.created_at <= end_date)

        total = query.count()

        logs = query.order_by(desc(QmsAiLog.created_at)) \
            .offset((page - 1) * page_size) \
            .limit(page_size) \
            .all()

        return logs, total

    def get_log_by_id(self, log_id: int) -> Optional[QmsAiLog]:
        """
        根据ID获取日志

        Args:
            log_id: 日志ID

        Returns:
            QmsAiLog or None
        """
        return self.db.query(QmsAiLog).filter(QmsAiLog.id == log_id).first()

    def get_stats(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        获取AI使用统计

        Args:
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            Dict: 统计数据
        """
        from sqlalchemy import func

        query = self.db.query(QmsAiLog)

        if start_date:
            query = query.filter(QmsAiLog.created_at >= start_date)
        if end_date:
            query = query.filter(QmsAiLog.created_at <= end_date)

        total_count = query.count()
        success_count = query.filter(QmsAiLog.status == "success").count()
        failed_count = query.filter(QmsAiLog.status == "failed").count()
        total_tokens = query.with_entities(
            func.coalesce(func.sum(QmsAiLog.tokens_used), 0)
        ).scalar()

        return {
            "total_count": total_count,
            "success_count": success_count,
            "failed_count": failed_count,
            "total_tokens": total_tokens,
            "success_rate": round(success_count / total_count * 100, 2) if total_count > 0 else 0
        }

    def delete_log(self, log_id: int) -> bool:
        """
        删除日志

        Args:
            log_id: 日志ID

        Returns:
            bool: 是否成功
        """
        log = self.get_log_by_id(log_id)
        if log:
            self.db.delete(log)
            self.db.commit()
            return True
        return False

    def cleanup_old_logs(self, days: int = 30) -> int:
        """
        清理旧日志

        Args:
            days: 保留天数

        Returns:
            int: 删除的数量
        """
        from datetime import timedelta

        cutoff_date = datetime.now() - timedelta(days=days)

        deleted_count = self.db.query(QmsAiLog).filter(
            QmsAiLog.created_at < cutoff_date
        ).delete()

        self.db.commit()

        return deleted_count
