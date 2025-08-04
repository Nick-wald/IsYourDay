import sys
from pathlib import Path

# 确保项目根目录在Python路径中
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# 现在可以使用绝对导入
from app.tasks.celery_tasks import daily_isyourday_events_check

def main():
    """测试Celery任务执行"""
    print("🚀 正在启动Celery任务...")
    # 提交异步任务，delay是误报，celery会动态创建
    res = daily_isyourday_events_check.delay( # type: ignore
        )
    print(f"✅ 任务已提交，任务ID: {res.id}")
    print(f"📊 任务状态: {res.status}")
    
    # 等待任务完成（可选）
    print("⏳ 等待任务完成...")
    result = res.get(timeout=30)  # 30秒超时
    print(f"🎉 任务完成，结果: {result}")
    return result

if __name__ == "__main__":
    main()
