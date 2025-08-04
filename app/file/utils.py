"""
文件存储初始化脚本
在应用启动时创建必要的目录结构
"""
import hashlib
import pathlib
import re
import tempfile
from typing import Iterator, Optional, Tuple
from fastapi import HTTPException, UploadFile, status
from sqlmodel import select
import typer
from rich import print
from rich.console import Console
from rich.table import Table

from app.auth.models import User
from app.db_manager import SessionDep
from app.file.models import FileDB

from .settings import FILE_PATH, MAX_FILE_SIZE_LIMIT_MB

console = Console()

def init_file_storage():
    table = Table("Type", "Path", "Status")
    
    for item in FILE_PATH:
        dir_path = pathlib.Path(item.value)
        dir_path.mkdir(parents=True, exist_ok=True)
        table.add_row(f"[bold green]{item.name}[/bold green]", f"[bold green]{str(dir_path.resolve())}[/bold green]", "[bold green]OK![/bold green]")

    print("[bold yellow]File Storage Paths Checking...[/bold yellow]")
    console.print(table)


def file_path(parent_path: str, path = None, resolve: bool = False) -> pathlib.Path:
    """ generate file storage path"""
    if parent_path not in FILE_PATH:
        raise ValueError(f"无效的文件存储路径: {parent_path}")
    _path = pathlib.Path(parent_path)
    if path:
        _path = _path.joinpath(str(path))
    _path.mkdir(parents=True, exist_ok=True)
    return _path.resolve() if resolve else _path


def file_path_str(parent_path: str, path = None, resolve: bool = False) -> str:
    """ generate file storage path as string"""
    _path = file_path(parent_path, path, resolve)
    return str(_path)



def parse_range_header(range_header: str, file_size: int) -> Tuple[int, int]:
    """解析HTTP Range请求头"""
    range_match = re.match(r'bytes=(\d+)-(\d*)', range_header)
    if not range_match:
        raise ValueError("Invalid range header format")
    
    start = int(range_match.group(1))
    end_str = range_match.group(2)
    
    if end_str:
        end = int(end_str)
    else:
        end = file_size - 1
    
    # 验证范围
    if start >= file_size or end >= file_size or start > end:
        raise ValueError(f"Range out of bounds: {start}-{end} for file size {file_size}")
    
    return start, end


def create_file_iterator(file_path: pathlib.Path, start: int = 0, end: Optional[int] = None, chunk_size: int = 1024 * 1024) -> Iterator[bytes]:
    """创建文件内容迭代器，支持Range请求"""
    with open(file_path, 'rb') as f:
        f.seek(start)
        
        if end is None:
            # 读取到文件末尾
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                yield chunk
        else:
            # 读取指定范围
            remaining = end - start + 1
            while remaining > 0:
                chunk_size_to_read = min(chunk_size, remaining)
                chunk = f.read(chunk_size_to_read)
                if not chunk:
                    break
                yield chunk
                remaining -= len(chunk)


async def process_large_file_upload(file: UploadFile, request_user: User, is_public: bool, session: SessionDep) -> FileDB:
    """处理大文件上传的内部函数"""
    # 创建用户目录
    user_path = file_path_str(FILE_PATH.USER_PATH, request_user.id)
    
    temp_file_path = None
    md5_hash = hashlib.md5()
    total_size = 0
    chunk_size = 1024 * 1024  # 1MB chunks
    
    try:
        # 创建临时文件
        with tempfile.NamedTemporaryFile(delete=False, dir=user_path) as temp_file:
            temp_file_path = temp_file.name
            
            # 流式读取和写入
            while True:
                chunk = await file.read(chunk_size)
                if not chunk:
                    break
                
                # 检查总大小限制
                total_size += len(chunk)
                if total_size > MAX_FILE_SIZE_LIMIT_MB * 1024 * 1024:
                    temp_file.close()
                    pathlib.Path(temp_file_path).unlink()
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=f"文件大小超过{MAX_FILE_SIZE_LIMIT_MB}MB限制"
                    )
                
                temp_file.write(chunk)
                md5_hash.update(chunk)
        
        # 计算MD5
        file_md5 = md5_hash.hexdigest()
        
        # 检查是否已存在相同MD5的文件
        existing_file = session.exec(
            select(FileDB).where(FileDB.md5 == file_md5)
        ).first()
        
        if existing_file:
            # 删除临时文件，返回现有记录
            pathlib.Path(temp_file_path).unlink()
            return existing_file
        
        # 重命名到最终位置
        final_file_path = pathlib.Path(user_path) / f"{file_md5}_{file.filename or 'unknown_file'}"
        pathlib.Path(temp_file_path).rename(final_file_path)
        
        # 创建数据库记录
        file_db = FileDB(
            name=file.filename or "unknown_file",
            size=total_size,
            md5=file_md5,
            path=user_path,
            uploader_id=request_user.id,
            is_public=is_public
        )
        
        session.add(file_db)
        session.commit()
        session.refresh(file_db)
        
        return file_db
        
    except Exception as e:
        # 清理临时文件
        if temp_file_path and pathlib.Path(temp_file_path).exists():
            pathlib.Path(temp_file_path).unlink()
        raise e


async def process_large_file_upload_raw(file: UploadFile, user_path: str) -> dict:
    """处理大文件上传，返回文件信息字典"""
    pathlib.Path(user_path).mkdir(parents=True, exist_ok=True)
    
    temp_file_path = None
    md5_hash = hashlib.md5()
    total_size = 0
    chunk_size = 1024 * 1024  # 1MB chunks
    
    try:
        # 创建临时文件
        with tempfile.NamedTemporaryFile(delete=False, dir=user_path) as temp_file:
            temp_file_path = temp_file.name
            
            # 流式读取和写入
            while True:
                chunk = await file.read(chunk_size)
                if not chunk:
                    break
                
                total_size += len(chunk)
                if total_size > MAX_FILE_SIZE_LIMIT_MB * 1024 * 1024:
                    temp_file.close()
                    pathlib.Path(temp_file_path).unlink()
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=f"文件大小超过{MAX_FILE_SIZE_LIMIT_MB}MB限制"
                    )
                
                temp_file.write(chunk)
                md5_hash.update(chunk)
        
        file_md5 = md5_hash.hexdigest()
        
        # 重命名到最终位置
        final_file_path = pathlib.Path(user_path) / f"{file_md5}_{file.filename or 'unknown_file'}"
        pathlib.Path(temp_file_path).rename(final_file_path)
        
        return {
            "md5": file_md5,
            "size": total_size,
            "path": str(final_file_path)
        }
        
    except Exception as e:
        if temp_file_path and pathlib.Path(temp_file_path).exists():
            pathlib.Path(temp_file_path).unlink()
        raise e


async def process_standard_file_upload_raw(file: UploadFile, user_path: str) -> dict:
    """处理标准文件上传，返回文件信息字典"""
    pathlib.Path(user_path).mkdir(parents=True, exist_ok=True)
    
    # 读取文件内容
    content = await file.read()
    
    # 检查文件大小
    if len(content) > MAX_FILE_SIZE_LIMIT_MB * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"文件大小超过{MAX_FILE_SIZE_LIMIT_MB}MB限制"
        )
    
    # 计算MD5
    file_md5 = hashlib.md5(content).hexdigest()
    
    # 保存文件
    file_path = pathlib.Path(user_path) / f"{file_md5}_{file.filename or 'unknown_file'}"
    with open(file_path, 'wb') as f:
        f.write(content)
    
    return {
        "md5": file_md5,
        "size": len(content),
        "path": str(file_path)
    }


if __name__ == "__main__":
    init_file_storage()
