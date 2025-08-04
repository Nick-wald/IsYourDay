import sys
from pathlib import Path

import requests
import json
import uuid
import os

from sqlmodel import select

# 确保项目根目录在Python路径中
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from datetime import timedelta
from app.auth.models import Token
from app.auth.models import User
from app.file.models import FileDB
from app.auth.settings import ACCESS_TOKEN_EXPIRE_MINUTES
from app.db_manager import Session, engine
from .celery_app import celery_app

# ====================== 配置参数（需根据实际情况修改） ======================
WORKFLOW_URL = os.getenv("WORKFLOW_URL", "http://example.com")  # Workflow 接口地址
API_KEY = os.getenv("API_KEY", "default_key")  # 认证用的 API Key
USER_ID = os.getenv("USER_ID", "default_user_id")  # 示例用户标识

# 输入变量
INPUTS = {
    "token": "",
    "ip": "http://192.168.42.138:8000",
    "mode": 0,
    "select_mode": 0,
    "sender": "系统自动发送邮件",
    "only_text": 0
}

def get_refresh_token():
    """
    获取刷新令牌的函数
    这里可以根据实际情况实现获取刷新令牌的逻辑
    """
    try:
        with Session(engine) as session:
            user = session.exec(
                select(User).where(User.id == uuid.UUID("7522b2ee-6815-46f1-846c-b08371d94db5"))
            ).first()
            
            if not user:
                raise ValueError("未找到管理员用户")
                
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = Token.create_token(
                data={
                    "sub": str(user.id),
                    "scopes": [
                            "isyourday:read",
                            "auth:write"
                        ],
                    },
                expires_delta=access_token_expires
            )
            return access_token
    except Exception as e:
        print(f"获取刷新令牌失败: {e}")
        return None

def send_workflow_request(mode: int = 0) -> str:
    """发送工作流请求"""
    try:
        # 获取token
        token = get_refresh_token()
        if not token:
            raise ValueError("无法获取认证令牌")
            return "无法获取认证令牌"
            
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        
        # 创建输入数据副本并设置token
        inputs = INPUTS.copy()
        inputs["token"] = token
        inputs["mode"] = mode

        payload = {
            "inputs": inputs,
            "response_mode": "streaming",
            "user": USER_ID
        }

        # 发送请求
        response = requests.post(
            WORKFLOW_URL,
            headers=headers,
            json=payload,
            stream=False,
            timeout=30
        )
        response.raise_for_status()
        return f"工作流请求发送成功: {response.status_code}"

    except requests.RequestException as e:
        error_msg = f"请求失败: {e}"
        print(error_msg)
        return error_msg
    except Exception as e:
        error_msg = f"未处理异常: {type(e).__name__} - {str(e)}"
        print(error_msg)
        return error_msg

@celery_app.task
def celery_test_task(x: int | None = None, y: int | None = None) -> str:
    from random import randint
    _x = x or randint(1, 100)
    _y = y or randint(1, 100)
    result = _x + _y
    return f"Result: {_x} + {_y} = {result}"


@celery_app.task
def daily_isyourday_events_check():
    """
    Celery任务：检查每日事件
    """
    try:
        # 使用 celery_app 的上下文确保在正确的环境中执行
        send_workflow_request(mode=0)
        send_workflow_request(mode=1)
        return "OK"
    except Exception as e:
        # 捕获并记录任何异常
        return f"任务执行失败: {str(e)}"
