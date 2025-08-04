# 通用分页响应模型
from typing import List, TypeVar, Generic

from pydantic import BaseModel, Field

T = TypeVar('T')

class PaginationInfo(BaseModel):
    """分页信息"""
    skip: int = Field(description="跳过的记录数")
    limit: int = Field(description="当前页记录数")
    total: int = Field(description="总记录数")
    page: int = Field(description="当前页码 (从1开始)")
    total_pages: int = Field(description="总页数")
    has_next: bool = Field(description="是否有下一页")
    has_prev: bool = Field(description="是否有上一页")

class PaginatedResponse(BaseModel, Generic[T]):
    """通用分页响应模型"""
    items: List[T] = Field(description="数据列表")
    pagination: PaginationInfo = Field(description="分页信息")
    
    @classmethod
    def create(cls, items: List[T], skip: int, limit: int, total: int):
        """创建分页响应"""
        page = (skip // limit) + 1 if limit > 0 else 1
        total_pages = ((total - 1) // limit) + 1 if limit > 0 and total > 0 else 1
        
        pagination = PaginationInfo(
            skip=skip,
            limit=limit,
            total=total,
            page=page,
            total_pages=total_pages,
            has_next=skip + limit < total,
            has_prev=skip > 0
        )
        
        return cls(items=items, pagination=pagination)
