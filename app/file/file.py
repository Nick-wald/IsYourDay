from enum import Enum
from fastapi import Depends, HTTPException, status, Form, Query, BackgroundTasks, Security, APIRouter, UploadFile, Request, Body
from fastapi.responses import StreamingResponse, Response
from sqlmodel import select, col
import uuid
import os
import pathlib
import urllib.parse
import mimetypes
import re
import hashlib
import tempfile
import time
from datetime import datetime
from typing import Iterator, Tuple, Optional

from ..auth.utils import get_request_user, get_request_active_user
from ..auth.models import User
from ..models import PaginatedResponse
from ..db_manager import SessionDep
from .settings import MAX_FILE_SIZE_LIMIT_MB, STREAM_UPLOAD_LIMIT_MB
from .utils import file_path, FILE_PATH, file_path_str, parse_range_header, create_file_iterator, process_large_file_upload, process_large_file_upload_raw, process_standard_file_upload_raw
from .models import FileDB


file_manager_router = APIRouter(
    prefix="/file",
    tags=["文件管理"],
)

class FileRangeRole(str, Enum):
    """ 文件范围枚举类"""
    me = "private"
    public = "public"
    all = "all"
    global_files = "global"

@file_manager_router.get("/list/{file_range}", response_model=PaginatedResponse[FileDB], summary="获取文件列表")
async def get_files(
    session: SessionDep,
    file_range: FileRangeRole,
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(10, le=100, description="返回的记录数"),
    request_user: User | None = Security(get_request_user, scopes=["file:read"])
) -> PaginatedResponse[FileDB]:
    """获取文件列表，通过file_range参数控制返回的文件范围，global_files表示全局文件（需要管理员权限）"""
    match file_range:
        case FileRangeRole.public:
            # 只获取公开文件
            query = select(FileDB).where(FileDB.is_public == True)
        case FileRangeRole.me:
            # 获取用户自己的文件
            if not request_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="需要登录才能访问个人文件",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            query = select(FileDB).where(FileDB.uploader_id == request_user.id)
        case FileRangeRole.all:
            # 获取所有文件（公开+自己）
            if not request_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="需要登录才能访问所有文件",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            query = select(FileDB).where(
                (FileDB.is_public == True) | (FileDB.uploader_id == request_user.id)
            )
        case FileRangeRole.global_files:
            # 获取全局文件（需要管理员权限）
            if not request_user or not request_user.is_superuser:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="需要管理员权限才能访问全局文件"
                )
            query = select(FileDB)
    
    # 获取总数
    total = len(session.exec(query).all())
    
    # 获取分页数据
    files = session.exec(query.offset(skip).limit(limit)).all()
    return PaginatedResponse[FileDB].create(list(files), skip, limit, total)


@file_manager_router.get("/search", response_model=PaginatedResponse[FileDB], summary="搜索文件")
async def search_files(
    session: SessionDep,
    request_user: User | None = Depends(get_request_user),
    q: str = Query(..., description="搜索文件名关键词"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, le=100),
    public_only: bool = Query(False, description="仅搜索公开文件，未登录时仅可搜索公开文件"),
    global_search: bool = Query(False, description="是否全局搜索（包括非公开文件和其他用户文件），开启此项需要管理员权限")
) -> PaginatedResponse[FileDB]:
    """搜索文件，逻辑是先根据关键词搜索文件名，然后根据文件域限过滤结果"""
    if global_search and (not request_user or not request_user.is_superuser):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限才能进行全局搜索"
        )
    query = select(FileDB)
    if request_user and not global_search:
        # 第一次约束，用户登录时搜全部还是个人+公开
        query = query.where(
            (FileDB.uploader_id == request_user.id) | (FileDB.is_public == True)
        )
    if not request_user or public_only:
        # 第二次约束，用户未登录或选择只搜公开文件
        query = query.where(FileDB.is_public == True)
    
    query = query.where(col(FileDB.name).like(f"%{q}%"))
    
    # 获取总数
    total = len(session.exec(query).all())
    
    # 获取分页数据
    query = query.offset(skip).limit(limit)
    files = session.exec(query).all()
    
    return PaginatedResponse[FileDB].create(list(files), skip, limit, total)


@file_manager_router.get("/stats", summary="获取文件统计信息")
async def get_file_stats(
    session: SessionDep,
    request_user: User = Security(get_request_active_user, scopes=["file:read"])
):
    """获取文件统计信息"""
    # 用户上传的总文件数
    total_files = session.exec(
        select(FileDB).where(FileDB.uploader_id == request_user.id)
    ).all()
    
    # 用户公开文件数
    public_files = session.exec(
        select(FileDB).where(
            (FileDB.uploader_id == request_user.id) & (FileDB.is_public == True)
        )
    ).all()
    
    # 计算总文件大小
    total_size = sum(file.size for file in total_files)
    
    return {
        "total_files": len(total_files),
        "public_files": len(public_files),
        "private_files": len(total_files) - len(public_files),
        "total_size_bytes": total_size,
        "total_size_mb": round(total_size / (1024 * 1024), 2),
    }


@file_manager_router.get("/upload/status/{file_id}", summary="查询分片上传状态")
async def get_upload_status(
    file_id: str,
    session: SessionDep,
    request_user: User = Security(get_request_active_user, scopes=["file:read"]),
):
    """查询分片上传状态"""
    try:
        user_temp_dir = file_path(FILE_PATH.TEMP_PATH, request_user.id)
        
        if not user_temp_dir.exists():
            return {
                "file_id": file_id,
                "uploaded_chunks": [],
                "total_uploaded": 0
            }
        
        # 查找已上传的分片
        uploaded_chunks = []
        for chunk_file in user_temp_dir.glob(f"{file_id}.chunk.*"):
            try:
                chunk_index = int(chunk_file.name.split('.')[-1])
                uploaded_chunks.append(chunk_index)
            except (ValueError, IndexError):
                continue
        
        uploaded_chunks.sort()
        
        return {
            "file_id": file_id,
            "uploaded_chunks": uploaded_chunks,
            "total_uploaded": len(uploaded_chunks)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查询上传状态失败: {str(e)}"
        )


@file_manager_router.get("/{file_id}", response_model=FileDB, summary="获取单个文件信息")
async def get_file(
    file_id: uuid.UUID,
    session: SessionDep,
    request_user: User | None = Security(get_request_user, scopes=["file:read"]),
) -> FileDB:
    """获取单个文件信息"""
    file_db = session.get(FileDB, file_id)
    
    if not file_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文件不存在"
        )
    
    # 检查访问权限：公开文件或文件所有者
    if not file_db.is_public:
        if not request_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="需要登录才能访问此文件",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not request_user.is_superuser and file_db.uploader_id != request_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权访问此文件"
            )
    
    return file_db


@file_manager_router.get("/{file_id}/download", summary="下载文件（支持断点续传）")
async def download_file(
    file_id: uuid.UUID,
    request: Request,
    session: SessionDep,
    request_user: User | None = Security(get_request_user, scopes=["file:read"]),
):
    """下载文件，支持断点续传和分片传输"""
    file_db = session.get(FileDB, file_id)
    
    if not file_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文件不存在"
        )
    
    # 检查访问权限
    if not file_db.is_public:
        if not request_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="需要登录才能下载此文件",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if file_db.uploader_id != request_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权下载此文件"
            )
    
    try:
        # 构建文件路径
        _path = file_db.get_path()
        if not _path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="物理文件不存在"
            )
        
        # 获取文件大小
        file_size = _path.stat().st_size
        
        # 检测MIME类型
        mime_type, _ = mimetypes.guess_type(file_db.name)
        if mime_type is None:
            mime_type = "application/octet-stream"
        
        # 处理中文文件名编码问题
        try:
            file_db.name.encode('ascii')
            content_disposition = f"attachment; filename={file_db.name}"
        except UnicodeEncodeError:
            encoded_filename = urllib.parse.quote(file_db.name, safe='')
            ascii_fallback = "file"
            content_disposition = f"attachment; filename={ascii_fallback}; filename*=UTF-8''{encoded_filename}"
        
        # 处理Range请求（断点续传）
        range_header = request.headers.get('range')
        
        if range_header:
            try:
                start, end = parse_range_header(range_header, file_size)
                content_length = end - start + 1
                
                headers = {
                    "Content-Range": f"bytes {start}-{end}/{file_size}",
                    "Accept-Ranges": "bytes",
                    "Content-Length": str(content_length),
                    "Content-Disposition": content_disposition,
                    "Cache-Control": "public, max-age=3600",
                    "ETag": f'"{file_db.md5}"'
                }
                
                return StreamingResponse(
                    create_file_iterator(_path, start, end),
                    status_code=206,  # Partial Content
                    media_type=mime_type,
                    headers=headers
                )
                
            except ValueError as e:
                # Range请求格式错误，返回416
                raise HTTPException(
                    status_code=416,  # Range Not Satisfiable
                    detail=f"Invalid range: {str(e)}",
                    headers={"Content-Range": f"bytes */{file_size}"}
                )
        
        # 普通下载（支持分片传输）
        headers = {
            "Content-Length": str(file_size),
            "Accept-Ranges": "bytes",
            "Content-Disposition": content_disposition,
            "Cache-Control": "public, max-age=3600",
            "ETag": f'"{file_db.md5}"',
            "Last-Modified": _path.stat().st_mtime.__str__()
        }
        
        return StreamingResponse(
            create_file_iterator(_path),
            media_type=mime_type,
            headers=headers
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件下载失败: {str(e)}"
        )


@file_manager_router.head("/{file_id}/download", summary="获取文件下载信息（用于断点续传）")
async def get_download_info(
    file_id: uuid.UUID,
    session: SessionDep,
    request_user: User | None = Security(get_request_user, scopes=["file:read"]),
):
    """获取文件下载信息，支持HEAD请求用于断点续传"""
    file_db = session.get(FileDB, file_id)
    
    if not file_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文件不存在"
        )
    
    # 检查访问权限
    if not file_db.is_public:
        if not request_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="需要登录才能访问此文件",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if file_db.uploader_id != request_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权访问此文件"
            )
    
    try:
        # 构建文件路径
        _path = file_db.get_path()
        if not _path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="物理文件不存在"
            )
        
        file_size = _path.stat().st_size
        mime_type, _ = mimetypes.guess_type(file_db.name)
        if mime_type is None:
            mime_type = "application/octet-stream"
        
        # 处理文件名编码
        try:
            file_db.name.encode('ascii')
            content_disposition = f"attachment; filename={file_db.name}"
        except UnicodeEncodeError:
            encoded_filename = urllib.parse.quote(file_db.name, safe='')
            ascii_fallback = "file"
            content_disposition = f"attachment; filename={ascii_fallback}; filename*=UTF-8''{encoded_filename}"
        
        headers = {
            "Content-Length": str(file_size),
            "Accept-Ranges": "bytes",
            "Content-Type": mime_type,
            "Content-Disposition": content_disposition,
            "Cache-Control": "public, max-age=3600",
            "ETag": f'"{file_db.md5}"',
            "Last-Modified": _path.stat().st_mtime.__str__()
        }
        
        return Response(headers=headers)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取文件信息失败: {str(e)}"
        )


@file_manager_router.get("/{file_id}/stream", summary="流式下载文件（在线预览）")
async def stream_file(
    file_id: uuid.UUID,
    request: Request,
    session: SessionDep,
    request_user: User | None = Security(get_request_user, scopes=["file:read"]),
):
    """流式下载文件，适用于在线预览（如视频、音频、图片），头像，动态图片等也使用此接口"""
    file_db = session.get(FileDB, file_id)
    
    if not file_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文件不存在"
        )
    
    # 检查访问权限
    if not file_db.is_public:
        if not request_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="需要登录才能访问此文件",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if file_db.uploader_id != request_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权访问此文件"
            )
    
    try:
        # 构建文件路径
        _path = file_db.get_path()
        if not _path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="物理文件不存在"
            )
        
        file_size = _path.stat().st_size
        mime_type, _ = mimetypes.guess_type(file_db.name)
        if mime_type is None:
            mime_type = "application/octet-stream"
        
        # 处理Range请求
        range_header = request.headers.get('range')
        
        if range_header:
            try:
                start, end = parse_range_header(range_header, file_size)
                content_length = end - start + 1
                
                headers = {
                    "Content-Range": f"bytes {start}-{end}/{file_size}",
                    "Accept-Ranges": "bytes",
                    "Content-Length": str(content_length),
                    "Cache-Control": "public, max-age=3600",
                    "ETag": f'"{file_db.md5}"'
                }
                
                return StreamingResponse(
                    create_file_iterator(_path, start, end, chunk_size=64*1024),  # 64KB chunks for streaming
                    status_code=206,
                    media_type=mime_type,
                    headers=headers
                )
                
            except ValueError as e:
                raise HTTPException(
                    status_code=416,
                    detail=f"Invalid range: {str(e)}",
                    headers={"Content-Range": f"bytes */{file_size}"}
                )
        
        # 普通流式传输
        headers = {
            "Content-Length": str(file_size),
            "Accept-Ranges": "bytes",
            "Cache-Control": "public, max-age=3600",
            "ETag": f'"{file_db.md5}"'
        }
        
        return StreamingResponse(
            create_file_iterator(_path, chunk_size=64*1024),  # 64KB chunks for streaming
            media_type=mime_type,
            headers=headers
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件流式传输失败: {str(e)}"
        )


@file_manager_router.post("/upload", response_model=dict, summary="上传文件（支持大文件优化）")
async def upload_files(
    files: list[UploadFile],
    session: SessionDep,
    request_user: User = Security(get_request_active_user, scopes=["file:upload"]),
    is_public: bool = Form(False, description="是否公开文件"),
    use_streaming: bool = Form(True, description="是否使用流式处理（推荐大文件使用）"),
) -> dict:
    """上传文件，自动优化大文件处理，支持批量上传容错处理"""
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="没有选择文件上传"
        )
    
    uploaded_files = []
    failed_files = []
    skipped_files = []
    
    for file in files:
        if not file.filename:
            skipped_files.append({
                "filename": "未知文件名", 
                "reason": "文件名为空"
            })
            continue  # 跳过没有文件名的上传
            
        try:
            # 预检查文件大小（如果提供了size信息）
            if file.size and file.size > MAX_FILE_SIZE_LIMIT_MB * 1024 * 1024:
                failed_files.append({
                    "filename": file.filename,
                    "error": f"文件大小超过{MAX_FILE_SIZE_LIMIT_MB}MB限制",
                    "size_mb": round(file.size / (1024 * 1024), 2) if file.size else None
                })
                continue
            
            # 判断是否使用流式处理（文件大小超过设定值或明确要求使用流式处理）
            should_use_streaming = use_streaming or (file.size and file.size > STREAM_UPLOAD_LIMIT_MB * 1024 * 1024)
            
            if should_use_streaming:
                # 使用流式处理大文件
                file_db = await process_large_file_upload(file, request_user, is_public, session)
            else:
                # 使用传统方式处理小文件
                user_path = file_path_str(FILE_PATH.USER_PATH, request_user.id)
                file_db = await FileDB.from_upload_file(file, request_user, user_path)
                file_db.is_public = is_public
                
                # 保存到数据库 - 使用独立事务
                try:
                    session.add(file_db)
                    session.commit()
                    session.refresh(file_db)
                except Exception as db_error:
                    session.rollback()
                    # 清理已上传的文件
                    try:
                        _path = file_db.get_path()
                        if _path.exists():
                            _path.unlink()
                    except:
                        pass
                    raise db_error
            
            uploaded_files.append(file_db)
            
        except HTTPException as http_ex:
            # 记录HTTP异常但继续处理其他文件
            failed_files.append({
                "filename": file.filename,
                "error": http_ex.detail,
                "status_code": http_ex.status_code
            })
            continue
        except Exception as e:
            # 记录一般异常但继续处理其他文件
            failed_files.append({
                "filename": file.filename,
                "error": f"上传失败: {str(e)}",
                "status_code": 500
            })
            continue
    
    # 构建响应结果
    result = {
        "summary": {
            "total_files": len(files),
            "uploaded_count": len(uploaded_files),
            "failed_count": len(failed_files),
            "skipped_count": len(skipped_files)
        },
        "uploaded_files": uploaded_files,
        "failed_files": failed_files if failed_files else [],
        "skipped_files": skipped_files if skipped_files else []
    }
    
    # 如果所有文件都失败，返回错误状态
    if len(uploaded_files) == 0 and len(failed_files) > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "所有文件上传失败",
                "details": result
            }
        )
    
    return result


@file_manager_router.post("/upload/chunk", summary="分片上传文件")
async def upload_file_chunk(
    session: SessionDep,
    request_user: User = Security(get_request_active_user, scopes=["file:upload"]),
    file: UploadFile = Form(...),
    chunk_index: int = Form(..., description="分片索引（从0开始）"),
    total_chunks: int = Form(..., description="总分片数"),
    file_id: str = Form(..., description="文件唯一标识符"),
    original_filename: str = Form(..., description="原始文件名"),
    total_size: int = Form(..., description="文件总大小"),
    is_public: bool = Form(False, description="是否公开文件"),
):
    """分片上传文件，支持大文件断点上传"""
    
    # 验证分片参数
    if chunk_index < 0 or chunk_index >= total_chunks:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="分片索引无效"
        )
    
    if total_size > MAX_FILE_SIZE_LIMIT_MB * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"文件大小超过{MAX_FILE_SIZE_LIMIT_MB}MB限制"
        )
    
    try:
        # 创建临时目录存储分片
        user_temp_dir = file_path(FILE_PATH.TEMP_PATH, request_user.id)
        
        # 分片文件路径
        chunk_filename = f"{file_id}.chunk.{chunk_index}"
        chunk_path = user_temp_dir / chunk_filename
        
        # 保存分片
        chunk_content = await file.read()
        with open(chunk_path, 'wb') as f:
            f.write(chunk_content)
        
        # 检查所有分片是否都已上传
        uploaded_chunks = []
        for i in range(total_chunks):
            chunk_file = user_temp_dir / f"{file_id}.chunk.{i}"
            if chunk_file.exists():
                uploaded_chunks.append(i)
        
        response_data = {
            "chunk_index": chunk_index,
            "uploaded": True,
            "uploaded_chunks": len(uploaded_chunks),
            "total_chunks": total_chunks,
            "is_complete": len(uploaded_chunks) == total_chunks
        }
        
        # 如果所有分片都已上传，合并文件
        if len(uploaded_chunks) == total_chunks:
            # 合并分片
            md5_hash = hashlib.md5()
            merged_file_path = file_path(FILE_PATH.USER_PATH, request_user.id) / f"temp_{file_id}_{original_filename}"
            
            with open(merged_file_path, 'wb') as merged_file:
                for i in range(total_chunks):
                    chunk_file = user_temp_dir / f"{file_id}.chunk.{i}"
                    with open(chunk_file, 'rb') as chunk:
                        chunk_data = chunk.read()
                        merged_file.write(chunk_data)
                        md5_hash.update(chunk_data)
            
            # 计算MD5并重命名文件
            file_md5 = md5_hash.hexdigest()
            final_file_path = file_path(FILE_PATH.USER_PATH, request_user.id) / f"{file_md5}_{original_filename}"
            merged_file_path.rename(final_file_path)
            
            # 创建新的文件记录
            file_size = final_file_path.stat().st_size
            file_db = FileDB(
                name=original_filename,
                size=file_size,
                md5=file_md5,
                path=file_path_str(FILE_PATH.USER_PATH, request_user.id),
                uploader_id=request_user.id,
                is_public=is_public
            )
                
            session.add(file_db)
            session.commit()
            session.refresh(file_db)
            
            response_data["file_info"] = file_db
            response_data["message"] = "文件上传成功"
            
            # 清理临时分片文件
            for i in range(total_chunks):
                chunk_file = user_temp_dir / f"{file_id}.chunk.{i}"
                if chunk_file.exists():
                    chunk_file.unlink()
        
        return response_data
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"分片上传失败: {str(e)}"
        )


@file_manager_router.patch("/{file_id}", response_model=FileDB, summary="更新文件信息")
async def update_file_info(
    file_id: uuid.UUID,
    session: SessionDep,
    request_user: User = Security(get_request_active_user, scopes=["file:write"]),
    name: str | None = Form(None, description="新文件名"),
    is_public: bool | None = Form(None, description="是否公开"),
) -> FileDB:
    """更新文件信息（文件名、公开状态等）"""
    file_db = session.get(FileDB, file_id)
    
    if not file_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文件不存在"
        )
    
    # 检查权限：只有文件所有者可以修改
    if file_db.uploader_id != request_user.id:
        if not request_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权修改此文件"
            )
    
    try:
        # 更新文件名
        if name is not None:
            old_name = file_db.name
            file_db.name = name
            
            # 如果文件名改变，需要重命名物理文件
            if old_name != name:
                old_file_path = pathlib.Path(file_db.path).joinpath(f"{file_db.md5}_{old_name}")
                new_file_path = pathlib.Path(file_db.path).joinpath(f"{file_db.md5}_{name}")
                
                if old_file_path.exists():
                    old_file_path.rename(new_file_path)
        
        # 更新公开状态
        if is_public is not None:
            file_db.is_public = is_public
        
        # 更新修改时间
        file_db.updated_at = datetime.now()
        
        session.add(file_db)
        session.commit()
        session.refresh(file_db)
        
        return file_db
        
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新文件信息失败: {str(e)}"
        )


@file_manager_router.put("/{file_id}/replace", response_model=FileDB, summary="替换文件内容")
async def replace_file_content(
    file_id: uuid.UUID,
    new_file: UploadFile,
    session: SessionDep,
    request_user: User = Security(get_request_active_user, scopes=["file:write", "file:upload"]),
    use_streaming: bool = Form(True, description="是否使用流式处理"),
) -> FileDB:
    """替换文件内容，保持文件ID不变"""
    file_db = session.get(FileDB, file_id)
    
    if not file_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文件不存在"
        )
    
    # 检查权限：只有文件所有者可以替换
    if file_db.uploader_id != request_user.id:
        if not request_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权替换此文件"
            )
    
    if not new_file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="没有选择新文件"
        )
    
    try:
        # 检查新文件大小
        if new_file.size and new_file.size > MAX_FILE_SIZE_LIMIT_MB * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"新文件大小超过{MAX_FILE_SIZE_LIMIT_MB}MB限制"
            )
        
        # 备份原文件路径
        old_file_path = file_db.get_path()
        
        # 上传新文件
        user_path = file_path_str(FILE_PATH.USER_PATH, request_user.id)
        
        if use_streaming and new_file.size and new_file.size > STREAM_UPLOAD_LIMIT_MB * 1024 * 1024:
            # 使用流式处理大文件
            new_file_data = await process_large_file_upload_raw(new_file, user_path)
        else:
            # 使用传统方式处理小文件
            new_file_data = await process_standard_file_upload_raw(new_file, user_path)
        
        # 检查新文件是否与现有文件重复
        if new_file_data["md5"] == file_db.md5:
            # 如果MD5相同，说明文件内容没有变化，直接返回
            return file_db
        
        # 删除原文件
        if old_file_path.exists():
            old_file_path.unlink()
        
        # 更新文件记录
        file_db.name = new_file.filename
        file_db.size = new_file_data["size"]
        file_db.md5 = new_file_data["md5"]
        file_db.upload_time = datetime.now()
        
        session.add(file_db)
        session.commit()
        session.refresh(file_db)
        
        return file_db
        
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"替换文件内容失败: {str(e)}"
        )


@file_manager_router.delete("/batch", summary="批量删除文件")
async def delete_files_batch(
    session: SessionDep,
    request_user: User = Security(get_request_active_user, scopes=["file:delete"]),
    file_ids: list[uuid.UUID] = Body(..., description="要删除的文件ID列表"),
    force: bool = Query(False, description="强制删除（即使物理文件不存在）")
):
    """批量删除文件"""
    if not file_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="没有指定要删除的文件"
        )
    
    deleted_files = []
    failed_files = []
    
    for file_id in file_ids:
        try:
            file_db = session.get(FileDB, file_id)
            
            if not file_db:
                failed_files.append({
                    "file_id": str(file_id),
                    "error": "文件不存在"
                })
                continue
            
            # 检查权限
            if file_db.uploader_id != request_user.id:
                if not request_user.is_superuser:
                    failed_files.append({
                        "file_id": str(file_id),
                        "file_name": file_db.name,
                        "error": "无权删除此文件"
                    })
                    continue
            
            # 检查是否有其他文件使用相同的MD5
            files_with_same_md5 = session.exec(
                select(FileDB).where(FileDB.md5 == file_db.md5)
            ).all()
            
            # 删除物理文件
            if len(files_with_same_md5) <= 1:
                file_path = file_db.get_path()
                if file_path.exists():
                    file_path.unlink()
                elif not force:
                    failed_files.append({
                        "file_id": str(file_id),
                        "file_name": file_db.name,
                        "error": "物理文件不存在"
                    })
                    continue
            
            # 删除数据库记录
            session.delete(file_db)
            deleted_files.append({
                "file_id": str(file_id),
                "file_name": file_db.name
            })
            
        except Exception as e:
            failed_files.append({
                "file_id": str(file_id),
                "error": f"删除失败: {str(e)}"
            })
    
    try:
        session.commit()
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"批量删除提交失败: {str(e)}"
        )
    
    return {
        "message": f"批量删除完成，成功: {len(deleted_files)}, 失败: {len(failed_files)}",
        "deleted_files": deleted_files,
        "failed_files": failed_files
    }


@file_manager_router.post("/cleanup/orphaned", summary="清理孤立文件")
async def cleanup_orphaned_files(
    session: SessionDep,
    request_user: User = Security(get_request_active_user, scopes=["file:delete"]),
    dry_run: bool = Query(True, description="仅模拟运行，不实际删除"),
    global_cleanup: bool = Query(False, description="是否清理所有用户的孤立文件，此项需要管理员权限")
):
    """清理数据库中没有记录但物理存在的孤立文件,以及数据库中存在但物理文件不存在的记录"""
    if global_cleanup:
        if not request_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="需要管理员权限才能清理所有用户的孤立文件"
            )
        # 清理所有用户的孤立文件
        user_path = file_path(FILE_PATH.USER_PATH)
    else:
        user_path = file_path(FILE_PATH.USER_PATH, request_user.id)
    
    if not user_path.exists():
        return {
            "message": "用户文件目录不存在",
            "orphaned_files": [],
            "cleaned_count": 0
        }
    
    # 获取用户的所有文件记录
    if global_cleanup:
        user_files = session.exec(select(FileDB)).all()
    else:
        user_files = session.exec(
            select(FileDB).where(FileDB.uploader_id == request_user.id)
        ).all()
    
    cleaned_count = 0
    
    orphaned_db = []
    
    for file in user_files:
        # 检查物理文件是否存在
        _file_path = file.get_path()
        if not _file_path.exists():
            orphaned_db.append({
                    "file_id": str(file.id),
                    "file_path": str(_file_path),
                    "file_size": file.size
                })
            if not dry_run:
                # 如果物理文件不存在，但数据库记录存在，删除数据库记录
                session.delete(file)
                cleaned_count += 1
    
    session.commit()
    
    # 创建MD5到文件名的映射
    db_files = {f"{file.md5}_{file.name}" for file in user_files}
    
    # 扫描物理文件
    orphaned_files = []
    for _path in user_path.iterdir():
        if _path.is_file():
            file_name = _path.name
            if file_name not in db_files and not file_name.startswith('temp_'):
                orphaned_files.append({
                    "file_name": file_name,
                    "file_path": str(_path),
                    "size": _path.stat().st_size
                })
    
    if not dry_run:
        # 实际删除孤立文件
        for orphan in orphaned_files:
            try:
                pathlib.Path(orphan["file_path"]).unlink()
                cleaned_count += 1
            except Exception:
                pass  # 忽略删除错误
    
    return {
        "message": f"{'模拟运行' if dry_run else '实际清理'}完成，发现{len(orphaned_files)}个孤立文件",
        "orphaned_files": orphaned_files,
        "orphaned_db": orphaned_db,
        "cleaned_count": cleaned_count if not dry_run else 0
    }


@file_manager_router.post("/cleanup/temp", summary="清理临时文件")
async def cleanup_temp_files(
    session: SessionDep,
    request_user: User = Security(get_request_active_user, scopes=["file:delete"]),
    max_age_hours: int = Query(24, description="清理超过指定小时数的临时文件"),
    dry_run: bool = Query(True, description="仅模拟运行，不实际删除"),
    global_cleanup: bool = Query(False, description="是否清理所有用户的临时文件，此项需要管理员权限")
):
    """清理临时上传文件"""
    if global_cleanup:
        if not request_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="需要管理员权限才能清理所有用户的临时文件"
            )
        # 清理所有用户的临时文件
        temp_path = file_path(FILE_PATH.TEMP_PATH)
    else:
        temp_path = file_path(FILE_PATH.TEMP_PATH, request_user.id)
    
    if not temp_path.exists():
        return {
            "message": "临时文件目录不存在",
            "cleaned_files": [],
            "cleaned_count": 0
        }
    
    import time
    current_time = time.time()
    max_age_seconds = max_age_hours * 3600
    
    cleaned_files = []
    for _path in temp_path.iterdir():
        if _path.is_file():
            file_age = current_time - _path.stat().st_mtime
            if file_age > max_age_seconds:
                try:
                    file_size = _path.stat().st_size
                    if not dry_run:
                        _path.unlink()
                    cleaned_files.append({
                        "file_name": _path.name,
                        "size": file_size,
                        "age_hours": round(file_age / 3600, 2)
                    })
                except Exception:
                    pass  # 忽略删除错误
    
    return {
        "message": f"清理完成，删除了{len(cleaned_files)}个临时文件",
        "cleaned_files": cleaned_files,
        "cleaned_count": len(cleaned_files)
    }


@file_manager_router.get("/storage/usage", summary="获取存储使用情况")
async def get_storage_usage(
    session: SessionDep,
    global_usage: bool = Query(False, description="是否获取全局存储使用情况（需要管理员权限）"),
    request_user: User = Security(get_request_active_user, scopes=["file:read"]),
):
    """获取用户存储使用情况详细信息"""
    # 获取用户所有文件
    if global_usage:
        if not request_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="需要管理员权限才能获取全局存储使用情况"
            )
        user_files = session.exec(select(FileDB)).all()
    else:
        user_files = session.exec(
            select(FileDB).where(FileDB.uploader_id == request_user.id)
        ).all()
    
    # 按文件类型分组统计
    file_types = {}
    total_size = 0
    
    for file in user_files:
        # 文件类型统计
        file_ext = pathlib.Path(file.name).suffix.lower() or "无扩展名"
        if file_ext not in file_types:
            file_types[file_ext] = {"count": 0, "size": 0}
        file_types[file_ext]["count"] += 1
        file_types[file_ext]["size"] += file.size
        total_size += file.size
        
    
    # 计算物理存储使用量
    user_path = file_path(FILE_PATH.USER_PATH, request_user.id if not global_usage else None)
    physical_size = 0
    if user_path.exists():
        for _path in user_path.rglob("*"):
            if _path.is_file():
                physical_size += _path.stat().st_size
    
    return {
        "summary": {
            "total_files": len(user_files),
            "physical_size_bytes": physical_size,
            "total_size_bytes": total_size,
            "public_files": len([f for f in user_files if f.is_public]),
            "private_files": len([f for f in user_files if not f.is_public])
        },
        "file_types": {
            ext: {
                "count": stats["count"],
                "size_bytes": stats["size"],
                "percentage": round((stats["size"] / total_size) * 100, 2) if total_size > 0 else 0
            }
            for ext, stats in sorted(file_types.items(), key=lambda x: x[1]["size"], reverse=True)
        }
    }
