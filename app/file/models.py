from sqlmodel import SQLModel, Field, Relationship
from fastapi import UploadFile
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional
import pathlib
import hashlib
from sqlmodel import Session

from .settings import FILE_PATH

if TYPE_CHECKING:
    from ..auth.models import User

class FileDB(SQLModel, table=True):
    """File model for storing file metadata."""
    
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        description="Unique identifier for the file"
    )
    name: str = Field(nullable=False, description="Name of the file")
    md5: str = Field(
        index=True,
        nullable=False,
        description="MD5 hash of the file for integrity check"
    )
    is_public: bool = Field(
        default=False,
        description="Is the file publicly accessible?"
    )
    path: str = Field(
        nullable=False,
        description="Path to the file on the server"
    )
    size: int = Field(
        default=0,
        description="Size of the file in bytes"
    )
    uploader_id: uuid.UUID | None = Field(
        foreign_key="user.id",
        description="ID of the user who uploaded the file"
    )
    uploader: Optional["User"] = Relationship(
        back_populates="files",
        sa_relationship_kwargs={"foreign_keys": "[FileDB.uploader_id]"}
    )
    avatar_users: list["User"] = Relationship(
        back_populates="avatar",
        sa_relationship_kwargs={"foreign_keys": "[User.avatar_id]"}
    )
    upload_time: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp when the file was uploaded"
    )
    
    def check_md5(self, res: bytes) -> bool:
        """Check if the MD5 hash of the given bytes matches the stored MD5."""
        return hashlib.md5(res).hexdigest() == self.md5
    
    @classmethod
    async def from_upload_file(cls, upload_file: UploadFile, uploader: Optional["User"] = None, path = "./media") -> "FileDB":
        """Create a FileDB instance from an UploadFile."""
        # 读取文件内容
        file_content = await upload_file.read()
        
        # 计算MD5
        file_md5 = hashlib.md5(file_content).hexdigest()
        
        _inst = cls(
            name=upload_file.filename or "unknown_file",
            md5=file_md5,
            size=len(file_content),
            uploader_id=uploader.id if uploader else None,
            path=path
        )
        
        # 写入文件
        await _inst.write(file_content)
        return _inst
    
    def get_path(self) -> pathlib.Path:
        """Get the full path to the file."""
        return pathlib.Path(self.path).joinpath(f"{self.md5}_{self.name}").resolve()
    
    async def write(self, res: bytes) -> "FileDB":
        """Write the file to the specified path."""
        path = pathlib.Path(self.path)
        path = path.resolve()  # 解析路径
        # 创建目录（包括父目录），如果不存在的话
        path.mkdir(parents=True, exist_ok=True)
        with open(path.joinpath(self.md5 + "_" + self.name), "wb") as f:
            f.write(res)
        return self
    
    async def read(self) -> bytes:
        """Read the file from the specified path."""
        path = pathlib.Path(self.path)
        path = path.resolve()  # 解析路径
        file_path = path.joinpath(self.md5 + "_" + self.name)
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        with open(file_path, "rb") as f:
            return f.read()
    
    async def delete(self, session: Session) -> None:
        """Delete the file from the specified path."""
        path = pathlib.Path(self.path)
        path = path.resolve()  # 解析路径
        if not path.exists():
            return
        file_path = path.joinpath(self.md5 + "_" + self.name)
        if file_path.exists():
            file_path.unlink()
            session.delete(self)
            session.commit()
        else:
            raise FileNotFoundError(f"文件不存在: {file_path}")