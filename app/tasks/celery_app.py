from datetime import timedelta
import os
from pathlib import Path
import sys
from celery import Celery
from celery.schedules import crontab
import typer
from rich import print
from rich.table import Table
from rich.console import Console

# 确保项目根目录在Python路径中
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# 切换到项目根目录
os.chdir(project_root)

celery_app = Celery(
    'app',
    backend=os.getenv('REDIS_BACKEND_URL'),
    broker=os.getenv('REDIS_BROKER_URL'),
    include=[
        'app.tasks.celery_tasks',
    ]
)

celery_app.conf.update(
    result_expires=3600,
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='Asia/Shanghai',
    enable_utc=True,
    # 添加 Windows 兼容性配置
    worker_pool='threads',  # 在 Windows 上使用线程池而不是 eventlet
    worker_concurrency=4,   # 设置并发数
    task_always_eager=False,  # 确保任务异步执行
)

celery_app.conf.beat_schedule = {
    'run-every-10-seconds': {
        'task': 'app.tasks.celery_tasks.celery_test_task',
        'schedule': timedelta(seconds=20),
    },
    'isyourday-events-check': {
        'task': 'app.tasks.celery_tasks.daily_isyourday_events_check',
        'schedule': crontab(hour=0, minute=0),  # 每天午夜执行
        # 'schedule': timedelta(seconds=5),  # 测试时可以改为每5分钟执行
    },
}
