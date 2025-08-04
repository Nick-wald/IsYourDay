from uuid import UUID
import uuid
from fastapi import UploadFile
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
import jwt
from jwt import InvalidTokenError
from sqlmodel import select
import urllib.parse
import pathlib

import smtplib
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.utils import formataddr, formatdate
from email import encoders
import encodings.idna

from .settings import EMAIL_SENDER_ACCOUNT, EMAIL_SENDER_PASSWORD, EMAIL_SENDER_SMTP, EMAIL_SENDER_PORT, OAUTH2_SCOPE, SECRET_KEY, ALGORITHM
from .models import EmailSendHistory, TokenData, User
from ..file.models import FileDB
from ..db_manager import Session, engine, SessionDep

async def send_email(
    history_id: UUID | None,
    receiver_emails: list[str],
    receiver_name: list[str],
    sender_name: str = "Unified Auth System",
    subject: str = "Test Email",
    content: str = "This is a test email.",
    attachment_ids: list[UUID] | None = None,
    store_upload_files: bool = False
):
    with Session(engine) as session:
        history_record = session.get(EmailSendHistory, history_id) if history_id else None
        if history_id and not history_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="邮件历史记录不存在"
            )
        if len(receiver_emails) != len(receiver_name):
            if history_record:
                history_record.status = "failed"
                history_record.reason = "收件人和收件人名称数量不匹配"
                session.add(history_record)
                session.commit()
                session.refresh(history_record)
                return
        message = MIMEMultipart()
        message.attach(MIMEText(content, "html", "utf-8"))
        if attachment_ids:
            for file_id in attachment_ids:
                try:
                    # 从数据库获取文件对象
                    file = session.get(FileDB, file_id)
                    if not file:
                        if history_record:
                            history_record.status = "failed"
                            history_record.reason = f"附件文件不存在: {file_id}"
                            session.add(history_record)
                            session.commit()
                            session.refresh(history_record)
                            return
                        continue
                    
                    part = MIMEBase("application", "octet-stream")
                    file_content = await file.read()
                    part.set_payload(file_content)
                    # 对附件进行Base64编码
                    encoders.encode_base64(part)
                    # 确保文件名编码正确，支持中文文件名
                    encoded_filename = urllib.parse.quote(file.name, safe='')
                    part.add_header(
                        "Content-Disposition",
                        f"attachment; filename*=utf-8''{encoded_filename}",
                    )
                    message.attach(part)
                    # 如果不需要存储文件，则在发送后删除临时文件
                    if not store_upload_files:
                        try:
                            file_path = file.get_path()
                            if file_path.exists():
                                file_path.unlink()
                        except Exception:
                            pass  # 忽略删除临时文件的错误
                except Exception as e:
                    # 清理临时文件
                    if not store_upload_files and attachment_ids:
                        for cleanup_file_id in attachment_ids:
                            try:
                                cleanup_file = session.get(FileDB, cleanup_file_id)
                                if cleanup_file:
                                    file_path = cleanup_file.get_path()
                                    if file_path.exists():
                                        file_path.unlink()
                            except Exception:
                                pass
                    if history_record:
                        history_record.status = "failed"
                        history_record.reason = f"附件处理失败: {file_id} - {str(e)}"
                        session.add(history_record)
                        session.commit()
                        session.refresh(history_record)
                        return
        
        # 使用formataddr确保From字段格式正确
        message["From"] = formataddr((sender_name, EMAIL_SENDER_ACCOUNT))
        # 为To字段也使用正确的格式
        to_addresses = [formataddr((name, email)) for name, email in zip(receiver_name, receiver_emails)]
        message["To"] = ", ".join(to_addresses)
        message["Subject"] = Header(subject, "utf-8").encode()
        
        # 添加邮件头以提高送达率和专业性
        message["Reply-To"] = EMAIL_SENDER_ACCOUNT
        message["Return-Path"] = EMAIL_SENDER_ACCOUNT
        message["Message-ID"] = f"<{uuid.uuid4()}@{EMAIL_SENDER_ACCOUNT.split('@')[1]}>"
        message["Date"] = formatdate(localtime=True)
        message["MIME-Version"] = "1.0"
        
        try:
            with smtplib.SMTP_SSL(EMAIL_SENDER_SMTP, EMAIL_SENDER_PORT) as server:
                server.login(EMAIL_SENDER_ACCOUNT, EMAIL_SENDER_PASSWORD)
                server.sendmail(
                    from_addr=EMAIL_SENDER_ACCOUNT,
                    to_addrs=receiver_emails,
                    msg=message.as_string()
                )
                if history_record:
                    history_record.status = "success"
                    session.add(history_record)
                    session.commit()
                    session.refresh(history_record)
        except smtplib.SMTPException as e:
            if history_record:
                history_record.status = "failed"
                history_record.reason = f"邮件发送失败: {str(e)}"
                session.add(history_record)
                session.commit()
                session.refresh(history_record)
                return


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", scopes=OAUTH2_SCOPE, auto_error=False)


async def get_request_user(session: SessionDep, security_scopes: SecurityScopes, token: str = Depends(oauth2_scheme)) -> User | None:
    """ 获取当前登陆态用户 """
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
    if not token:
        return None
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="令牌无效或已过期",
        headers={"WWW-Authenticate": authenticate_value},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_scopes = payload.get("scopes", [])
        try:
            user_uuid = UUID(user_id)
        except ValueError:
            # 如果UUID转换失败，抛出认证异常
            raise credentials_exception
        token_data = TokenData(scopes=token_scopes, user_id=user_uuid)
    except InvalidTokenError:
        raise credentials_exception
    user = session.get(User, token_data.user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在或已注销",
            headers={"WWW-Authenticate": authenticate_value},
        )
    missing_scopes = set(security_scopes.scopes) - set(token_data.scopes)
    if len(missing_scopes) != 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"权限不足，此操作需要token额外具有下面权限: {', '.join(missing_scopes)}",
            headers={"WWW-Authenticate": authenticate_value},
        )
    return user


async def get_request_active_user(session: SessionDep, security_scopes: SecurityScopes, token: str = Depends(oauth2_scheme)) -> User:
    """ 获取当前登陆态的活跃用户 """
    user = await get_request_user(session, security_scopes, token)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户未登录或令牌无效",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用，此操作需要用户处于活跃状态",
        )
    return user


def hash_password(password: str):
    """Hash the password using bcrypt."""
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify the provided password against the stored hash."""
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.verify(plain_password, hashed_password)
    

def email_format_check(email: str) -> bool:
    """Check if the email format is valid, true is OK"""
    import re
    email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(email_regex, email) is not None


def random_code_generator(length: int = 6) -> str:
    """Generate a random challenge code of specified length."""
    import random
    import string
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))
