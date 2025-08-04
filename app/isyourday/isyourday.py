from fastapi import APIRouter, Depends, HTTPException, status, Form, Query, BackgroundTasks, UploadFile, Security
from sqlmodel import col, select
from pydantic import BaseModel
from datetime import datetime
import uuid
from typing import Optional

from ..db_manager import SessionDep
from ..auth.utils import get_request_active_user
from ..auth.models import User
from ..models import PaginatedResponse
from .models import EventPublic, VirtualUser, VirtualUserPublic, Event

is_your_day_router = APIRouter(
    prefix="/isyourday",
    tags=["IsYourDay"],
)

@is_your_day_router.get("/users", response_model=PaginatedResponse[VirtualUser], summary="获取虚拟用户列表")
async def get_virtual_users(
    session: SessionDep,
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(default=10, le=100, description="返回的记录数"),
    request_user: User = Security(get_request_active_user, scopes=["isyourday:read"]),
) -> PaginatedResponse[VirtualUser]:
    """获取虚拟用户列表"""
    # 获取总数
    total_query = select(VirtualUser)
    total = len(session.exec(total_query).all())
    
    # 获取分页数据
    users = session.exec(
        select(VirtualUser).offset(skip).limit(limit)
    ).all()
    return PaginatedResponse[VirtualUser].create(list(users), skip, limit, total)

@is_your_day_router.get("/user/{user_id}", response_model=VirtualUser, summary="获取单个虚拟用户")
async def get_virtual_user(
    user_id: uuid.UUID,
    session: SessionDep,
    request_user: User = Security(get_request_active_user, scopes=["isyourday:read"]),
) -> VirtualUser:
    """根据ID获取单个虚拟用户"""
    user = session.get(VirtualUser, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Virtual user not found"
        )
    return user

@is_your_day_router.post("/user", summary="创建虚拟用户")
async def create_virtual_user(
    user_data: list[VirtualUserPublic],
    session: SessionDep,
    request_user: User = Security(get_request_active_user, scopes=["isyourday:write"]),
) -> list[VirtualUser]:
    """创建新的虚拟用户"""
    db_users = []
    # 检查邮箱是否已存在
    for data in user_data:
        existing_user = session.exec(
            select(VirtualUser).where(
                VirtualUser.email == data.email
            )
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已被注册"
            )
        
        # 创建新用户
        db_user = VirtualUser(**data.model_dump())
        session.add(db_user)
        db_users.append(db_user)
    session.commit()
    for db_user in db_users:
        session.refresh(db_user)
    return db_users


@is_your_day_router.get("/users/search", response_model=PaginatedResponse[VirtualUser], summary="搜索虚拟用户")
async def search_virtual_users(
    session: SessionDep,
    query: Optional[str] = Query(None, description="搜索关键词"),
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(10, le=100, description="返回的记录数"),
    request_user: User = Security(get_request_active_user, scopes=["isyourday:read"]),
) -> PaginatedResponse[VirtualUser]:
    """搜索虚拟用户"""
    if not request_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="此操作需要管理员权限"
        )
    
    if not query:
        return PaginatedResponse[VirtualUser].create([], skip, limit, 0)
    
    # 构建查询
    search_query = select(VirtualUser).where(
        col(VirtualUser.real_name).like(f"%{query}%")
    )
    
    # 获取总数
    total = len(session.exec(search_query).all())
    
    # 获取分页数据
    users = session.exec(search_query.offset(skip).limit(limit)).all()
    
    return PaginatedResponse[VirtualUser].create(list(users), skip, limit, total)


@is_your_day_router.patch("/user/{user_id}", summary="更新虚拟用户")
async def update_virtual_user(
    user_id: uuid.UUID,
    user_data: VirtualUserPublic,
    session: SessionDep,
    request_user: User = Security(get_request_active_user, scopes=["isyourday:write"]),
) -> VirtualUser:
    """更新虚拟用户信息"""
    user = session.get(VirtualUser, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 如果更新邮箱，检查是否已存在
    if user_data.email and user_data.email != user.email:
        existing_user = session.exec(
            select(VirtualUser).where(VirtualUser.email == user_data.email)
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已被注册"
            )
    
    # 更新用户数据
    update_data = user_data.model_dump(exclude_unset=True)
    update_data["updated_at"] = datetime.now()
    user.sqlmodel_update(update_data)
    
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@is_your_day_router.delete("/users/batch", summary="批量删除删除虚拟用户")
async def delete_virtual_user(
    user_id: list[uuid.UUID],
    session: SessionDep,
    request_user: User = Security(get_request_active_user, scopes=["isyourday:delete"]),
) -> dict:
    """删除虚拟用户"""
    if not request_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="此操作需要管理员权限"
        )
    for uid in user_id:
        user = session.get(VirtualUser, uid)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        session.delete(user)
    session.commit()
    return {"message": "成功删除用户"}


@is_your_day_router.get("/user/{user_id}/events", response_model=PaginatedResponse[Event], summary="获取用户事件列表")
async def get_user_events(
    user_id: uuid.UUID,
    session: SessionDep,
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(10, le=100, description="返回的记录数"),
    request_user: User = Security(get_request_active_user, scopes=["isyourday:read"]),
) -> PaginatedResponse[Event]:
    """获取指定用户的事件列表"""
    user = session.get(VirtualUser, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 构建查询
    events_query = select(Event).where(Event.user_id == user_id)
    
    # 获取总数
    total = len(session.exec(events_query).all())
    
    # 获取分页数据
    events = session.exec(events_query.offset(skip).limit(limit)).all()
    return PaginatedResponse[Event].create(list(events), skip, limit, total)


@is_your_day_router.post("/user/{user_id}/events", summary="创建用户事件")
async def create_user_event(
    user_id: uuid.UUID,
    event_data: EventPublic,
    session: SessionDep,
    request_user: User = Security(get_request_active_user, scopes=["isyourday:write"]),
) -> Event:
    """为指定用户创建事件"""
    user = session.get(VirtualUser, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    event = Event(**event_data.model_dump(), user_id=user_id)
    session.add(event)
    session.commit()
    session.refresh(event)
    return event


@is_your_day_router.delete("/user/{user_id}/events/batch", summary="批量删除用户事件")
async def delete_user_events(
    user_id: uuid.UUID,
    event_ids: list[uuid.UUID],
    session: SessionDep,
    request_user: User = Security(get_request_active_user, scopes=["isyourday:delete"]),
) -> dict:
    """批量删除指定用户的事件"""
    user = session.get(VirtualUser, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    if not request_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="此操作需要管理员权限"
        )
    
    for event_id in event_ids:
        event = session.get(Event, event_id)
        if not event or event.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"事件 {event_id} 不存在或不属于该用户"
            )
        session.delete(event)
    
    session.commit()
    return {"message": "成功删除事件"}


@is_your_day_router.patch("/user/{user_id}/event/{event_id}", response_model=Event, summary="更新用户事件详情")
async def update_user_event(
    user_id: uuid.UUID,
    event_id: uuid.UUID,
    event_data: EventPublic,
    session: SessionDep,
    request_user: User = Security(get_request_active_user, scopes=["isyourday:write"]),
) -> Event:
    """更新指定用户的事件"""
    user = session.get(VirtualUser, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    event = session.get(Event, event_id)
    if not event or event.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="事件不存在或不属于该用户"
        )
    
    update_data = event_data.model_dump(exclude_unset=True)
    event.sqlmodel_update(update_data)
    
    session.add(event)
    session.commit()
    session.refresh(event)
    return event
    