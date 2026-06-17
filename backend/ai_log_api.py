"""
AI日志API接口
提供AI交互日志的查询、创建和管理功能
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

router = APIRouter(prefix="/api/v1/ai-logs", tags=["AI日志"])


def get_db():
    """数据库会话依赖"""
    from database import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class AiLogCreate(BaseModel):
    """创建AI日志"""
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    module: str
    action: str
    prompt: str
    response: Optional[str] = None
    model: Optional[str] = None
    tokens_used: Optional[int] = None
    status: str = "success"
    error_message: Optional[str] = None
    request_params: Optional[dict] = None
    response_time: Optional[float] = None


class AiLogResponse(BaseModel):
    """AI日志响应"""
    id: int
    user_id: Optional[str]
    session_id: Optional[str]
    module: str
    action: str
    prompt: str
    response: Optional[str]
    model: Optional[str]
    tokens_used: Optional[int]
    status: str
    error_message: Optional[str]
    request_params: Optional[dict]
    response_time: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True


class AiLogListResponse(BaseModel):
    """AI日志列表响应"""
    items: List[AiLogResponse]
    total: int
    page: int
    page_size: int


@router.get("/", response_model=AiLogListResponse)
async def list_ai_logs(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    module: Optional[str] = Query(None, description="模块名称"),
    action: Optional[str] = Query(None, description="操作类型"),
    status: Optional[str] = Query(None, description="状态"),
    start_date: Optional[datetime] = Query(None, description="开始日期"),
    end_date: Optional[datetime] = Query(None, description="结束日期"),
    db: Session = Depends(get_db)
):
    """
    获取AI日志列表
    """
    from ai.models import QmsAiLog
    from sqlalchemy import func, desc

    query = db.query(QmsAiLog)

    if module:
        query = query.filter(QmsAiLog.module == module)
    if action:
        query = query.filter(QmsAiLog.action == action)
    if status:
        query = query.filter(QmsAiLog.status == status)
    if start_date:
        query = query.filter(QmsAiLog.created_at >= start_date)
    if end_date:
        query = query.filter(QmsAiLog.created_at <= end_date)

    total = query.count()

    logs = query.order_by(desc(QmsAiLog.created_at)) \
        .offset((page - 1) * page_size) \
        .limit(page_size) \
        .all()

    items = []
    for log in logs:
        items.append(AiLogResponse(
            id=log.id,
            user_id=log.user_id,
            session_id=log.session_id,
            module=log.module,
            action=log.action,
            prompt=log.prompt,
            response=log.response,
            model=log.model,
            tokens_used=log.tokens_used,
            status=log.status,
            error_message=log.error_message,
            request_params=log.request_params,
            response_time=log.response_time,
            created_at=log.created_at
        ))

    return AiLogListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{log_id}", response_model=AiLogResponse)
async def get_ai_log(log_id: int, db: Session = Depends(get_db)):
    """
    获取单个AI日志详情
    """
    from ai.models import QmsAiLog

    log = db.query(QmsAiLog).filter(QmsAiLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="日志记录不存在")

    return AiLogResponse(
        id=log.id,
        user_id=log.user_id,
        session_id=log.session_id,
        module=log.module,
        action=log.action,
        prompt=log.prompt,
        response=log.response,
        model=log.model,
        tokens_used=log.tokens_used,
        status=log.status,
        error_message=log.error_message,
        request_params=log.request_params,
        response_time=log.response_time,
        created_at=log.created_at
    )


@router.post("/", response_model=AiLogResponse)
async def create_ai_log(log_data: AiLogCreate, db: Session = Depends(get_db)):
    """
    创建AI日志记录
    """
    from ai.models import QmsAiLog

    new_log = QmsAiLog(
        user_id=log_data.user_id,
        session_id=log_data.session_id,
        module=log_data.module,
        action=log_data.action,
        prompt=log_data.prompt,
        response=log_data.response,
        model=log_data.model,
        tokens_used=log_data.tokens_used,
        status=log_data.status,
        error_message=log_data.error_message,
        request_params=log_data.request_params,
        response_time=log_data.response_time
    )

    db.add(new_log)
    db.commit()
    db.refresh(new_log)

    return AiLogResponse(
        id=new_log.id,
        user_id=new_log.user_id,
        session_id=new_log.session_id,
        module=new_log.module,
        action=new_log.action,
        prompt=new_log.prompt,
        response=new_log.response,
        model=new_log.model,
        tokens_used=new_log.tokens_used,
        status=new_log.status,
        error_message=new_log.error_message,
        request_params=new_log.request_params,
        response_time=new_log.response_time,
        created_at=new_log.created_at
    )


@router.get("/stats/summary")
async def get_ai_stats_summary(
    start_date: Optional[datetime] = Query(None, description="开始日期"),
    end_date: Optional[datetime] = Query(None, description="结束日期"),
    db: Session = Depends(get_db)
):
    """
    获取AI使用统计摘要
    """
    from ai.models import QmsAiLog
    from sqlalchemy import func

    query = db.query(QmsAiLog)

    if start_date:
        query = query.filter(QmsAiLog.created_at >= start_date)
    if end_date:
        query = query.filter(QmsAiLog.created_at <= end_date)

    total_count = query.count()
    success_count = query.filter(QmsAiLog.status == "success").count()
    failed_count = query.filter(QmsAiLog.status == "failed").count()
    total_tokens = query.with_entities(func.coalesce(func.sum(QmsAiLog.tokens_used), 0)).scalar()

    return {
        "total_count": total_count,
        "success_count": success_count,
        "failed_count": failed_count,
        "total_tokens": total_tokens,
        "success_rate": round(success_count / total_count * 100, 2) if total_count > 0 else 0
    }


@router.delete("/{log_id}")
async def delete_ai_log(log_id: int, db: Session = Depends(get_db)):
    """
    删除AI日志记录
    """
    from ai.models import QmsAiLog

    log = db.query(QmsAiLog).filter(QmsAiLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="日志记录不存在")

    db.delete(log)
    db.commit()

    return {"message": "删除成功"}


@router.delete("/cleanup")
async def cleanup_old_logs(
    days: int = Query(30, ge=1, le=365, description="保留天数"),
    db: Session = Depends(get_db)
):
    """
    清理旧日志
    """
    from ai.models import QmsAiLog
    from datetime import timedelta

    cutoff_date = datetime.now() - timedelta(days=days)

    deleted_count = db.query(QmsAiLog).filter(
        QmsAiLog.created_at < cutoff_date
    ).delete()

    db.commit()

    return {"message": f"已删除 {deleted_count} 条旧日志"}
