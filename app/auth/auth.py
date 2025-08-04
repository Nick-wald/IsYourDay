from fastapi import APIRouter, Depends, HTTPException, status, Form, Query, BackgroundTasks, UploadFile, Security, File
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Request  # added for building activation link
from datetime import timedelta
from fastapi.templating import Jinja2Templates
from sqlmodel import col, select, desc
from uuid import UUID
from enum import Enum
import pathlib

from .models import Token, User, UserPublic, UserUpdate, ChallengeCodeDB, EmailSendHistory, EmailSendHistoryUpdate
from ..models import PaginatedResponse
from ..file.models import FileDB
from .utils import send_email, get_request_user, verify_password, hash_password, email_format_check, get_request_active_user
from .settings import ACCESS_TOKEN_EXPIRE_MINUTES
from ..file.utils import file_path_str, FILE_PATH

from ..db_manager import SessionDep

auth = APIRouter(
    prefix="/auth",
    tags=["登录鉴权"],
)

# 设置模板目录
email_templates = Jinja2Templates(directory="app/auth/email_templates")

@auth.get(
    "/users",
    summary="获取用户列表",
    response_model=PaginatedResponse[UserPublic]
    )
async def get_all_users(
    session: SessionDep,
    skip: int = 0,
    limit: int = Query(default=10, le=100),
    request_user: User = Depends(get_request_active_user)
) -> PaginatedResponse[UserPublic]:
    if not request_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="此操作需要管理员权限"
        )
    
    # 获取总数
    total_query = select(User)
    total = len(session.exec(total_query).all())
    
    # 获取分页数据
    users = session.exec(
        select(User).offset(skip).limit(limit)
    ).all()
    
    user_publics = [UserPublic.from_user(user) for user in users]
    return PaginatedResponse[UserPublic].create(user_publics, skip, limit, total)
    


@auth.get(
    "/me",
    response_model=UserPublic,
    summary="获取登录态用户信息"
    )
async def get_current_user(
    request_user: User = Security(get_request_active_user, scopes=["auth:read_basic"]),
):
    return UserPublic.from_user(request_user)

class UserSearchRole(str, Enum):
    username = "username"
    email = "email"
    user_id = "id"


@auth.get("/search", summary="搜索用户", response_model=PaginatedResponse[UserPublic])
async def search_user(
    session: SessionDep,
    request_user: User = Security(get_request_active_user, scopes=["auth:read_basic"]),
    q: str = Query(..., description="搜索关键词"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, le=100)
) -> PaginatedResponse[UserPublic]:
    if not request_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限进行全局用户检索"
        )
    
    # 获取总数
    total_query = select(User).where(col(User.username).like(f"%{q}%"))
    total = len(session.exec(total_query).all())
    
    # 获取分页数据
    query = select(User).where(col(User.username).like(f"%{q}%"))
    query = query.offset(skip).limit(limit)
    users = session.exec(query).all()
    
    user_publics = [UserPublic.from_user(user) for user in users]
    return PaginatedResponse[UserPublic].create(user_publics, skip, limit, total)


@auth.get(
    "/profile/{user_search_role}/{user_search_value}",
    response_model=UserPublic,
    summary="获取用户信息",
    )
async def get_user_by_info(
    session: SessionDep,
    user_search_role: UserSearchRole,
    user_search_value: str,
    request_user: User = Depends(get_request_active_user)
):
    match user_search_role:
        case UserSearchRole.username:
            user = session.exec(
                select(User).where(User.username == user_search_value)
            ).first()
        case UserSearchRole.email:
            user = session.exec(
                select(User).where(User.email == user_search_value)
            ).first()
        case UserSearchRole.user_id:
            user_id = UUID(user_search_value)
            user = session.get(User, user_id)
        case _:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无效的搜索方式"
            )
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在",
        )
    return UserPublic.from_user(user)


@auth.post(
    "/register",
    response_model=UserPublic,
    summary="用户注册",
    )
async def register_user(
    session: SessionDep,
    background_tasks: BackgroundTasks,
    request: Request,
    username: str = Form(..., description="用户名"),
    email: str = Form(..., description="用户邮箱", pattern=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"),
    password: str = Form(..., description="用户密码"),
    avatar: UploadFile | None = File(None, description="用户头像"),
):
    existing_user_username = session.exec(
        select(User).where(User.username == username)
    ).first()
    existing_user_email = session.exec(
        select(User).where(User.email == email)
    ).first()
    if existing_user_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户已存在",
        )
    if existing_user_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已被注册",
        )
        
    # 密码强度校验
    if any(char not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+[]{}|;:'\",.<>?/" for char in password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密码只能包含英文字母、数字和常见特殊字符"
        )
    if len(password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密码长度必须至少8个字符，一个数字，一个大写字母，一个小写字母和一个特殊字符"
        )
    if not any(char.isdigit() for char in password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密码长度必须至少8个字符，一个数字，一个大写字母，一个小写字母和一个特殊字符"
        )
    if not any(char.isupper() for char in password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密码长度必须至少8个字符，一个数字，一个大写字母，一个小写字母和一个特殊字符"
        )
    if not any(char.islower() for char in password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密码长度必须至少8个字符，一个数字，一个大写字母，一个小写字母和一个特殊字符"
        )
    if not any(char in "!@#$%^&*()-_=+[]{}|;:'\",.<>?/" for char in password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密码长度必须至少8个字符，一个数字，一个大写字母，一个小写字母和一个特殊字符"
        )
    
    db_user = User.model_validate({
        "username": username,
        "email": email,
        "password": hash_password(password),
        "is_active": False  # 新用户需激活
    })
    
    if avatar is not None:
        db_avatar = await FileDB.from_upload_file(
            avatar,
            uploader=None,  # 注册时不需要指定上传者
            path=file_path_str(FILE_PATH.AVATAR_PATH)
        )
        db_avatar.is_public = True  # 头像文件默认公开
        session.add(db_avatar)
        session.commit()
        session.refresh(db_avatar)
        db_user.avatar = db_avatar
    
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    
    # 生成激活码并发送激活邮件
    challenge = ChallengeCodeDB(user_id=db_user.id, call_from="register")
    session.add(challenge)
    session.commit()
    session.refresh(challenge)
    
    # 构建激活链接
    activate_link = request.url_for("activate_user", code=challenge.code)
    
    # 发送激活邮件
    background_tasks.add_task(
        send_email,
        None,
        [db_user.email],
        [db_user.username],
        "系统邮件",
        "账户激活邮件",
        email_templates.get_template("account_active.html.j2").render(
            {
                "username": db_user.username,
                "activate_link": activate_link
            }
        ),
        None  # 没有附件
    )
    
    return UserPublic.from_user(db_user)

@auth.post(
    "/login",
    summary="用户登录",
    )
async def login_for_access_token(
    session: SessionDep,
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Token:
    user = session.exec(
        select(User).where(User.username == form_data.username)
    ).first()
    if form_data.scopes:
        authenticate_value = f'Bearer scope="{" ".join(form_data.scopes)}"'
    else:
        authenticate_value = "Bearer"
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="不存在的用户",
            headers={"WWW-Authenticate": authenticate_value},
        )
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": authenticate_value},
        )
    
    # 检查用户是否已激活
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账户未激活，请先激活账户",
            headers={"WWW-Authenticate": authenticate_value},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = Token.create_token(
        data={
            "sub": str(user.id),
            "scopes": form_data.scopes or [],
            },
        expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")

class EmailReceiverType(str, Enum):
    user = "user"
    isyourday = "isyourday"


@auth.get(
    "/send-email/pending/{history_id}",
    summary="邮件发送接口，将挂起的请求发送"
    )
async def send_email_pending_endpoint(
    session: SessionDep,
    history_id: UUID,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    request_user: User = Security(get_request_active_user, scopes=["auth:write"])
):
    history_record = session.get(EmailSendHistory, history_id)
    if not history_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="邮件历史记录不存在"
        )
    
    if history_record.status == "success":
        return {
            "message": "该邮件已发送成功，无需重复发送",
        }
    
    if history_record.sender_id != request_user.id and not request_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限发送此邮件"
        )
    
    receiver_emails = history_record.receiver_emails.split(",")
    receiver_names = history_record.receiver_names.split(",")
    attachments: list[FileDB] = []
    if history_record.attachments:
        attachment_ids = history_record.attachments.split(",")
        for file_id in attachment_ids:
            file_db = session.get(FileDB, UUID(file_id))
            if not file_db:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"附件文件ID {file_id} 不存在"
                )
            attachments.append(file_db)
    
    background_tasks.add_task(
        send_email,
        history_id,
        receiver_emails,
        receiver_names,
        request_user.username,
        history_record.subject,
        history_record.content,
        [file.id for file in attachments],
        store_upload_files=False  # 挂起请求不需要存储文件
    )
    
    history_record.status = "sent"
    session.add(history_record)
    session.commit()
    return {
        "message": "邮件已进入发送队列",
        "email_history_id": str(history_record.id)
    }

@auth.patch(
    "/send-email/history",
    summary="更新邮件发送历史记录",
    )
async def update_email_send_history(
    session: SessionDep,
    history_id: UUID,
    update_data: EmailSendHistoryUpdate,
    request_user: User = Security(get_request_active_user, scopes=["auth:write"])
):
    history_record = session.get(EmailSendHistory, history_id)
    if not history_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="邮件发送历史记录不存在"
        )
    
    if history_record.sender_id != request_user.id and not request_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限更新此邮件发送历史记录"
        )
    
    # 更新字段
    update_dict = update_data.model_dump(exclude_unset=True)
    history_record.sqlmodel_update(update_dict)
    session.add(history_record)
    session.commit()
    session.refresh(history_record)
    
    return history_record

class EmailHistorySearchType(str, Enum):
    subject_search = "subject_search"
    content_search = "content_search"
    receiver_email_search = "receiver_email_search",
    receiver_name_search = "receiver_name_search"
    all_search = "all"

@auth.get(
    "/send-email/history/{search_type}",
    summary="获取邮件发送历史",
    response_model=PaginatedResponse[EmailSendHistory]
)
async def get_email_send_history(
    session: SessionDep,
    search_type: EmailHistorySearchType,
    q: str | None = Query(None, description="搜索关键词"),
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(10, le=100, description="返回的记录数"),
    global_search: bool = Query(False, description="是否全局搜索，此项需要管理员权限"),
    request_user: User = Security(get_request_active_user, scopes=["auth:read_basic"]),
) -> PaginatedResponse[EmailSendHistory]:
    query = select(EmailSendHistory)
    if not request_user.is_superuser and global_search:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="全局邮件历史搜索需要管理员权限"
        )
    if not global_search:
        query = query.where(EmailSendHistory.sender_id == request_user.id)
    
    match search_type:
        case EmailHistorySearchType.subject_search:
            if q:
                query = query.where(col(EmailSendHistory.subject).like(f"%{q}%"))
        case EmailHistorySearchType.content_search:
            if q:
                query = query.where(col(EmailSendHistory.content).like(f"%{q}%"))
        case EmailHistorySearchType.receiver_email_search:
            if q:
                query = query.where(col(EmailSendHistory.receiver_emails).like(f"%{q}%"))
        case EmailHistorySearchType.receiver_name_search:
            if q:
                query = query.where(col(EmailSendHistory.receiver_names).like(f"%{q}%"))
    
    # 获取总数
    total = len(session.exec(query).all())
    
    # 获取分页数据，按发送时间降序排列（从新到旧）
    history_records = session.exec(
        query.order_by(desc(EmailSendHistory.sent_at)).offset(skip).limit(limit)
    ).all()
    
    return PaginatedResponse[EmailSendHistory].create(list(history_records), skip, limit, total)

@auth.post(
    "/send-email/{receiver_type}",
    summary="邮件发送接口",
    )
async def send_email_endpoint(
    session: SessionDep,
    receiver_type: EmailReceiverType,
    receiver: list[UUID] = Form(description="接收者用户ID列表"),
    subject: str = Form("Test Email", description="邮件主题", min_length=1),
    content: str = Form("This is a test email.", description="邮件内容（支持HTML）", min_length=1),
    files: list[UploadFile] | None = None,
    files_in_store: list[UUID] | None = None,
    store_upload_files: bool = Form(False, description="是否存储上传的文件到服务器"),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    request_user: User = Security(get_request_active_user, scopes=["auth:write"]),
    send_directly: bool = Form(default=True, description="是否立即发送，False则pending")
):
    """
    files是用户上传的文件列表，files_in_store是已存储在服务器上的文件ID列表（注意需要权限）。
    """
    receiver_emails: list[str] = []
    receiver_names: list[str] = []
    attachments: list[FileDB] = []
    
    if not store_upload_files and not send_directly:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="挂起请求需要将文件储存到服务器中才可使用"
        )
    
    for user_id in receiver:
        try:
            match receiver_type:
                case EmailReceiverType.isyourday:
                    from ..isyourday.models import VirtualUser
                    user = session.exec(
                        select(VirtualUser).where(VirtualUser.id == user_id)
                    ).one()
                    username = user.real_name
                case EmailReceiverType.user:
                    user = session.exec(
                        select(User).where(User.id == user_id)
                    ).one()
                    username = user.username
                case _:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="无效的用户搜索域"
                    )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"用户ID {user_id} 不存在"
            )
        receiver_emails.append(user.email)
        receiver_names.append(username or "未知用户")
    
    if files:
        upload_path = file_path_str(FILE_PATH.TEMP_PATH) if not store_upload_files else file_path_str(FILE_PATH.USER_PATH, request_user.id)

        for file in files:
            if not file.filename:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="文件名不能为空"
                )
            file_db = await FileDB.from_upload_file(
                file,
                uploader=request_user,
                path=upload_path
            )
            attachments.append(file_db)
            
            # 如果需要存储文件到数据库
            if store_upload_files:
                session.add(file_db)
                
    if store_upload_files:
        session.commit()
        for file_db in attachments:
            # 确保文件已刷新到数据库（仅对已存储的文件）
            if file_db in session:
                session.refresh(file_db)
    
    for file_id in files_in_store or []:
        file_db = session.get(FileDB, file_id)
        if not file_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"文件ID {file_id} 不存在"
            )
        if not file_db.uploader == request_user:
            if not file_db.is_public and not request_user.is_superuser:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="没有权限访问该文件"
                )
        attachments.append(file_db)
    
    history_record = EmailSendHistory(
        receiver_type=str(receiver_type),
        receiver_emails=",".join(receiver_emails),
        receiver_names=",".join(receiver_names),
        sender_id=request_user.id,
        subject=subject,
        content=content,
        attachments=",".join([str(file.id) for file in attachments]),
        status="pending"
    )
    session.add(history_record)
    session.commit()
    session.refresh(history_record)
    
    if send_directly:
        background_tasks.add_task(
            send_email,
            history_record.id,
            receiver_emails,
            receiver_names,
            request_user.username,
            subject,
            content,
            [file.id for file in attachments],
            store_upload_files
        )
        return {
            "message": "邮件已进入发送队列",
            "email_history_id": str(history_record.id)
        }
    
    return {
        "message": "邮件已记录为挂起状态，等待发送",
        "email_history_id": str(history_record.id)
    }
    


@auth.patch(
    "/update",
    response_model=UserPublic,
    summary="更新用户信息",
    )
async def update_user_basic_info(
    session: SessionDep,
    new_user_info: UserUpdate,
    user_pk: UUID | None = None,
    request_user: User = Security(get_request_active_user, scopes=["auth:write"])
):
    user_db = request_user
    if user_pk is None:
        user_pk = request_user.id
    if request_user.id != user_pk and not request_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="修改其他用户信息需要提升权限"
        )
    else:
        user_db = session.get(User, user_pk)
    if not user_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    if new_user_info.email and not email_format_check(new_user_info.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的邮箱格式"
        )
    if new_user_info.password:
        new_user_info.password = hash_password(new_user_info.password)
    new_user_data = new_user_info.model_dump(exclude_unset=True)
    user_db.sqlmodel_update(new_user_data)
    session.add(user_db)
    session.commit()
    session.refresh(user_db)
    return UserPublic.from_user(user_db)

@auth.delete(
    "/delete/batch",
    summary="删除用户",
    )
async def delete_user(
    session: SessionDep,
    user_pk: list[UUID] = Query(..., description="用户ID列表"),
    request_user: User = Security(get_request_active_user, scopes=["auth:delete"])
):
    successful_deletes = []
    failed_users = []
    skipped_users = []
    
    for pk in user_pk:
        user_db = session.get(User, pk)
        if not user_db:
            failed_users.append({
                "id": str(pk),
                "reason": "用户不存在"
            })
            continue
        if user_db.is_superuser:
            skipped_users.append({
                "id": str(pk),
                "reason": "无法删除超级管理员用户，请降级后再试"
            })
            continue
        if user_db.id != request_user.id and not request_user.is_superuser:
            skipped_users.append({
                "id": str(pk),
                "reason": "非管理员无权删除其他用户"
            })
            continue
        # 删除用户的头像文件
        if user_db.avatar:
            avatar_path = user_db.avatar.get_path()
            if avatar_path.exists():
                avatar_path.unlink()
            session.delete(user_db.avatar)
        session.delete(user_db)
        successful_deletes.append(str(pk))
    
    session.commit()
    
    result = {
        "summary": {
            "total_users": len(user_pk),
            "successful_count": len(successful_deletes),
            "failed_count": len(failed_users),
            "skipped_count": len(skipped_users)
        },
        "deleted_users": successful_deletes,
        "failed_users": failed_users,
        "skipped_users": skipped_users
    }
    
    return result


@auth.get(
    "/activate/{code}",
    summary="激活用户账户",
    response_class=HTMLResponse
)
async def activate_user(
    code: str,
    request: Request,
    session: SessionDep
):
    """
    通过激活码激活用户账户，返回HTML激活成功页面
    """
    from datetime import datetime
    
    
    
    # 查找激活码
    challenge = session.exec(
        select(ChallengeCodeDB).where(ChallengeCodeDB.code == code, ChallengeCodeDB.call_from == "register")
    ).first()
    
    if not challenge:
        # 返回激活失败页面
        return email_templates.TemplateResponse(
            "activate_error.html.j2",
            {
                "request": request,
                "error_title": "激活链接无效",
                "error_message": "激活链接无效或已过期，请重新申请激活邮件",
                "support_email": "support@example.com"
            }
        )
    
    # 检查激活码是否已过期 (激活码永不过期，可以根据需要调整)
    if challenge.created_at < datetime.now() - timedelta(minutes=5):
        session.delete(challenge)
        session.commit()
        return email_templates.TemplateResponse(
            "activate_error.html.j2",
            {
                "request": request,
                "error_title": "激活链接已过期",
                "error_message": "激活链接已过期，请重新申请激活邮件",
                "support_email": "support@example.com"
            }
        )
    
    # 查找对应用户
    user = session.get(User, challenge.user_id)
    if not user:
        return email_templates.TemplateResponse(
            "activate_error.html.j2",
            {
                "request": request,
                "error_title": "用户不存在",
                "error_message": "关联的用户账户不存在，请联系管理员",
                "support_email": "support@example.com"
            }
        )
    
    # 检查用户是否已激活
    if user.is_active:
        # 删除已使用的激活码
        session.delete(challenge)
        session.commit()
        
        return email_templates.TemplateResponse(
            "activate_successful.html.j2",
            {
                "request": request,
                "username": user.username,
                "email": user.email,
                "activation_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "login_url": "/auth/login",
                "platform_url": "/",
                "already_activated": True
            }
        )
    
    # 激活用户并删除激活码
    user.is_active = True
    session.delete(challenge)
    session.add(user)
    session.commit()
    
    # 返回激活成功页面
    return email_templates.TemplateResponse(
        "activate_successful.html.j2",
        {
            "request": request,
            "username": user.username,
            "email": user.email,
            "activation_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "login_url": "/auth/login",
            "platform_url": "/",
            "already_activated": False
        }
    )


@auth.post(
    "/resend-activation",
    summary="重新发送激活邮件"
)
async def resend_activation_email(
    session: SessionDep,
    background_tasks: BackgroundTasks,
    request: Request,
    email: str = Form(..., description="用户邮箱")
):
    """
    重新发送激活邮件
    """
    # 查找用户
    user = session.exec(
        select(User).where(User.email == email)
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="邮箱未注册"
        )
    
    if user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户已激活，无需重复激活"
        )
    
    # 删除旧的激活码
    old_challenges = session.exec(
        select(ChallengeCodeDB).where(ChallengeCodeDB.user_id == user.id, ChallengeCodeDB.call_from == "register")
    ).all()
    for challenge in old_challenges:
        session.delete(challenge)
    
    # 生成新的激活码
    new_challenge = ChallengeCodeDB(user_id=user.id, call_from="register")
    session.add(new_challenge)
    session.commit()
    session.refresh(new_challenge)
    
    # 构建激活链接
    activate_link = f"{request.url.scheme}://{request.url.netloc}/auth/activate/{new_challenge.code}"
    
    # 发送激活邮件
    background_tasks.add_task(
        send_email,
        None,
        [user.email],
        [user.username],
        "系统邮件",
        "重新发送账户激活邮件",
        email_templates.get_template("account_active.html.j2").render(
            {
                "username": user.username,
                "activate_link": activate_link
            }
        ),
        None  # 没有附件
    )
    
    return {"message": "激活邮件已重新发送"}

@auth.post(
    "/reset-password",
    summary="发送密码重置邮件"
)
async def send_reset_password_email(
    session: SessionDep,
    background_tasks: BackgroundTasks,
    request: Request,
    email: str = Form(..., description="用户邮箱")
):
    """
    发送密码重置邮件
    """
    # 查找用户
    user = session.exec(
        select(User).where(User.email == email)
    ).first()
    
    if not user:
        # 为了安全起见，即使用户不存在也返回成功消息
        return {"message": "如果该邮箱已注册，您将收到密码重置邮件"}
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="账户未激活，请先激活账户"
        )
    
    # 删除该用户的旧密码重置码
    old_reset_codes = session.exec(
        select(ChallengeCodeDB).where(ChallengeCodeDB.user_id == user.id, ChallengeCodeDB.call_from == "reset_password")
    ).all()
    for code in old_reset_codes:
        session.delete(code)
    
    # 生成新的重置码
    reset_code = ChallengeCodeDB(user_id=user.id, call_from="reset_password")
    session.add(reset_code)
    session.commit()
    session.refresh(reset_code)
    
    # 构建重置链接
    reset_link = f"{request.url.scheme}://{request.url.netloc}/auth/reset-password/{reset_code.code}"
    
    # 发送重置密码邮件
    background_tasks.add_task(
        send_email,
        None,
        [user.email],
        [user.username],
        "系统邮件",
        "密码重置邮件",
        email_templates.get_template("password_reset.html.j2").render(
            {
                "username": user.username,
                "reset_link": reset_link
            }
        ),
        None  # 没有附件
    )
    
    return {"message": "如果该邮箱已注册，您将收到密码重置邮件"}


@auth.get(
    "/reset-password/{code}",
    summary="密码重置页面",
    response_class=HTMLResponse
)
async def reset_password_page(
    code: str,
    request: Request,
    session: SessionDep
):
    """
    显示密码重置页面
    """
    from datetime import datetime, timedelta
    
    # 查找重置码
    reset_code = session.exec(
        select(ChallengeCodeDB).where(ChallengeCodeDB.code == code, ChallengeCodeDB.call_from == "reset_password")
    ).first()
    
    if not reset_code:
        return email_templates.TemplateResponse(
            "reset_error.html.j2",
            {
                "request": request,
                "error_title": "重置链接无效",
                "error_message": "密码重置链接无效或已过期，请重新申请密码重置",
                "support_email": "support@example.com"
            }
        )
    
    # 检查重置码是否过期
    if reset_code.created_at < datetime.now() - timedelta(minutes=5):
        session.delete(reset_code)
        session.commit()
        return email_templates.TemplateResponse(
            "reset_error.html.j2",
            {
                "request": request,
                "error_title": "重置链接已过期",
                "error_message": "密码重置链接已过期，请重新申请密码重置",
                "support_email": "support@example.com"
            }
        )
    
    # 查找对应用户
    user = session.get(User, reset_code.user_id)
    if not user:
        return email_templates.TemplateResponse(
            "reset_error.html.j2",
            {
                "request": request,
                "error_title": "用户不存在",
                "error_message": "关联的用户账户不存在，请联系管理员",
                "support_email": "support@example.com"
            }
        )
    
    # 返回密码重置页面
    return email_templates.TemplateResponse(
        "password_reset_form.html.j2",
        {
            "request": request,
            "reset_code": code,
            "username": user.username,
            "email": user.email
        }
    )


@auth.post(
    "/reset-password/{code}",
    summary="执行密码重置"
)
async def reset_password_submit(
    code: str,
    session: SessionDep,
    new_password: str = Form(..., description="新密码"),
    confirm_password: str = Form(..., description="确认新密码")
):
    """
    执行密码重置
    """
    from datetime import datetime, timedelta
    
    if new_password != confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="两次输入的密码不一致"
        )
    
    # 密码强度校验（复用注册时的逻辑）
    if len(new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密码长度必须至少8个字符"
        )
    if not any(char.isdigit() for char in new_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密码必须包含至少一个数字"
        )
    if not any(char.isupper() for char in new_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密码必须包含至少一个大写字母"
        )
    if not any(char.islower() for char in new_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密码必须包含至少一个小写字母"
        )
    if not any(char in "!@#$%^&*()-_=+[]{}|;:'\",.<>?/" for char in new_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密码必须包含至少一个特殊字符"
        )
    
    # 查找重置码
    reset_code = session.exec(
        select(ChallengeCodeDB).where(ChallengeCodeDB.code == code, ChallengeCodeDB.call_from == "reset_password")
    ).first()
    
    if not reset_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="重置链接无效或已过期"
        )
    
    # 检查重置码是否过期（24小时）
    if reset_code.created_at < datetime.now() - timedelta(hours=24):
        session.delete(reset_code)
        session.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="重置链接已过期，请重新申请密码重置"
        )
    
    # 查找对应用户
    user = session.get(User, reset_code.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 更新用户密码
    user.password = hash_password(new_password)
    session.add(user)
    
    # 删除使用过的重置码
    session.delete(reset_code)
    session.commit()
    
    return {"message": "密码重置成功，请使用新密码登录"}
