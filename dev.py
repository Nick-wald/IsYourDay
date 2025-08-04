#!/usr/bin/env python3
"""
开发环境启动脚本
使用方法：python dev.py
"""
import subprocess
import sys
import os
import signal
from pathlib import Path
import typer
from rich import print
from rich.table import Table
from rich.console import Console

# 确保项目根目录在Python路径中
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# 切换到项目根目录
os.chdir(project_root)

UVICORN_PORT = "8000"
FLOWER_PORT = "5555"

class ServerCommand():
    """开发环境命令行工具"""
    
    def loadloop(self):
        """加载命令行工具"""
        self.do_help()
        while True:
            try:
                input_command = input("(dev) > ").strip()
                if not input_command:
                    continue
                elif input_command.lower() == "exit" or input_command.lower() == "quit":
                    self.do_exit()
                    break
                elif input_command.lower() == "help":
                    self.do_help()
                elif input_command.lower().startswith("alembic"):
                    self.do_alembic(input_command[7:].strip())
                elif input_command.lower() == "run":
                    self.do_run()
                elif input_command.lower() == "add-admin":
                    self.do_add_superuser()
                elif input_command.lower() == "undo-admin":
                    self.do_undo_superuser()
                elif input_command.lower() == "show-admins":
                    self.do_show_superusers()
                else:
                    print(f"[red]未知命令: {input_command}[/red]")
            except KeyboardInterrupt:
                self.do_exit()
                break
            except EOFError:
                self.do_EOF()
                break
            except Exception as e:
                print(f"[red]命令执行出错:[/red] {e}")

    def do_EOF(self):
        """退出命令行工具 (Ctrl+D)"""
        print("\n[bold green]花有重开日，码有运行时~[/bold green]")
        return True

    def do_exit(self):
        """退出开发环境命令行工具"""
        print("[bold green]人生喜相逢，与君再相思~[/bold green]")
        return True

    def do_help(self):
        """显示帮助信息"""
        print("\n[bold cyan]可用命令:[/bold cyan]")
        print("  [green]run[/green]              - 运行开发服务器")
        print("  [green]create_superuser[/green] - 创建超级用户")
        print("  [green]undo_superuser[/green]   - 撤销超级用户权限")
        print("  [green]show_superusers[/green]  - 显示所有超级用户")
        print("  [green]alembic[/green]          - 运行数据库迁移命令")
        print("  [green]help[/green]             - 显示帮助信息")
        print("  [green]exit/quit[/green]        - 退出开发环境")
        print("\n使用 [yellow]help <command>[/yellow] 查看特定命令的详细帮助")

    def do_alembic(self, arg):
        """运行Alembic数据库迁移命令
        """
        if not arg:
            print("[yellow]请提供alembic命令参数，例如：[/yellow]")
            print("  alembic revision --autogenerate -m \"Add new table\"")
            print("  alembic upgrade head")
            print("  alembic downgrade -1")
            return
        
        try:
            subprocess.run(f"alembic {arg}", shell=True, check=True, cwd=project_root / "app")
        except subprocess.CalledProcessError as e:
            print(f"[red]Alembic命令执行失败: {e}[/red]")

    
    def extract_ip(self):
        import socket
        st = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:       
            st.connect(('10.255.255.255', 1))
            IP = st.getsockname()[0]
        except Exception:
            IP = '127.0.0.1'
        finally:
            st.close()
        return IP

    def do_run(self, arg="windows"):
        """运行开发服务器（同时启动服务链）"""
        import uvicorn
        import signal
        
        
        print("[bold cyan]正在启动开发服务器...[/bold cyan]")
        
        process_pool = []
        
        # 启动Redis服务器进程
        redis_process = subprocess.Popen(
            "redis-server.exe redis.conf",
            shell=True,
            cwd=project_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        process_pool.append(redis_process)
        
        # 设置环境变量，确保 Python 能找到 app 模块
        env = os.environ.copy()
        env['PYTHONPATH'] = str(project_root)
        
        # 启动Celery worker进程
        print("[yellow]启动Celery worker...[/yellow]")
        celery_worker_process = subprocess.Popen(
            "celery -A app.tasks.celery_app worker -l info -E",
            shell=True,
            cwd=project_root,
            env=env,
            stderr=subprocess.STDOUT,
        )
        process_pool.append(celery_worker_process)
        
        # 启动Celery beat进程
        print("[yellow]启动Celery beat...[/yellow]")
        celery_beat_process = subprocess.Popen(
            "celery -A app.tasks.celery_app beat",
            shell=True,
            cwd=project_root,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        process_pool.append(celery_beat_process)
        
        # 启动Celery flower 监控进程
        print("[yellow]启动Celery flower监控...[/yellow]")
        celery_flower_process = subprocess.Popen(
            f"celery -A app.tasks.celery_app flower --port={FLOWER_PORT} --basic-auth={os.getenv("FLOWER_ACCOUNT", "admin")}:{os.getenv("FLOWER_PASSWORD", "admin")}",
            shell=True,
            cwd=project_root,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        process_pool.append(celery_flower_process)
        
        # 启动Uvicorn服务器进程
        print("[yellow]启动Uvicorn服务器...[/yellow]")
        uvicorn_process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", "app.main:app",
            "--host", "0.0.0.0",
            "--port", UVICORN_PORT,
            "--reload",
            "--workers", "4",
            "--reload-dir", str(project_root / "app"),
            "--log-level", "debug"
        ],
            stderr=subprocess.STDOUT,
            cwd=project_root)
        process_pool.append(uvicorn_process)
        
        print("[bold green]开发服务器已启动！[/bold green]")
        # 获取本机IP地址并拼凑出服务器地址
        self_ip = self.extract_ip()
        
        print("[cyan]Celery任务调度已在后台运行[/cyan]")
        print("[cyan]Redis服务器已启动[/cyan]")
        print(f"[bold green]Uvicorn服务器已启动，访问地址: http://{self_ip}:{UVICORN_PORT}[/bold green]")
        print(f"[bold green]API文档地址: http://{self_ip}:{UVICORN_PORT}/docs[/bold green]")
        print(f"[bold green]Celery Flower监控地址: http://{self_ip}:{FLOWER_PORT}[/bold green]")
        print(f"[bold green]Celery Flower登录用户名：flower 密码：floweradmin123456[/bold green]")
        print("[yellow]按 Ctrl+C 停止服务器[/yellow]")
        
        # 定义信号处理函数
        def signal_handler(signum, frame):
            try:
                for process in process_pool:
                    if process.poll() is None:
                        process.terminate()
                        process.wait(timeout=5)
                        if process.poll() is None:
                            process.kill()
            except Exception as e:
                print(f"[red]停止服务时出错: {e}[/red]")
            print("[green]所有服务已停止[/green]")
        
        # 注册信号处理器
        signal.signal(signal.SIGINT, signal_handler)
        if hasattr(signal, 'SIGTERM'):
            signal.signal(signal.SIGTERM, signal_handler)
        
        try:
            # 等待进程结束
            uvicorn_process.wait()
            celery_worker_process.wait()
            celery_beat_process.wait()
            celery_flower_process.wait()
            redis_process.wait()
            
        except KeyboardInterrupt:
            print("\n[yellow]收到中断信号，正在停止服务器...[/yellow]")
            signal_handler(None, None)
        except Exception as e:
            print(f"[red]服务器运行出错: {e}[/red]")
            signal_handler(None, None)
        finally:
            # 确保所有进程都被终止
            for process in process_pool:
                if process.poll() is None:
                    process.terminate()
                    process.wait(timeout=5)
                    if process.poll() is None:
                        process.kill()

    def do_add_superuser(self, arg=""):
        """ 创建超级用户 """
        from app.auth.models import User
        from sqlmodel import select, Session
        from app.db_manager import engine
        from app.auth.utils import hash_password

        input_username = input("请输入超级用户的用户名: ")

        with Session(engine) as session:
            # 检查是否已存在超级用户
            user = session.exec(select(User).where(User.username == input_username)).first()
            if user:
                print("[yellow]用户已存在，是否授予管理员权限？[/yellow]")
                input_accept = input("输入 'y' 授予管理员权限，其他输入则跳过: ")
                if input_accept.lower() == 'y':
                    user.is_superuser = True
                    session.add(user)
                    session.commit()
                    print("[green]已授予管理员权限。[/green]")
                else:
                    print("[yellow]跳过授予管理员权限。[/yellow]")
            else:
                input_email = input("请输入超级用户的邮箱: ")
                input_password = input("请输入超级用户的密码: ")
                input_password_confirm = input("请再次输入密码以确认: ")
                if input_password != input_password_confirm:
                    print("[red]两次输入的密码不一致，请重新运行脚本。[/red]")
                    return
                # 创建新超级用户
                user = User(
                    username=input_username,
                    email=input_email,
                    password=hash_password(input_password),
                    is_superuser=True,
                    is_active=True
                )
                session.add(user)
                session.commit()
                print(f"[green]超级用户 {input_username} 已创建。[/green]")

    def do_undo_superuser(self, arg=""):
        """ 撤销超级用户权限 """
        from app.auth.models import User
        from app.file.models import FileDB
        from sqlmodel import select, Session
        from app.db_manager import engine

        input_username = input("请输入要撤销超级用户权限的用户名: ")

        with Session(engine) as session:
            # 查找超级用户
            user = session.exec(select(User).where(User.username == input_username)).first()
            if user and user.is_superuser:
                user.is_superuser = False
                session.add(user)
                session.commit()
                print(f"[green]已撤销 {input_username} 的超级用户权限。[/green]")
            else:
                print("[red]未找到用户或该用户不是管理员。[/red]")
    
    def do_show_superusers(self, arg=""):
        """ 显示所有超级用户 """
        from app.auth.models import User
        from app.file.models import FileDB
        from sqlmodel import select, Session
        from app.db_manager import engine
        from rich.table import Table
        from rich.console import Console

        console = Console()
        table = Table("用户名", "用户ID", "邮箱", title="管理员列表")
        with Session(engine) as session:
            superusers = session.exec(select(User).where(User.is_superuser == True)).all()
            if superusers:
                for user in superusers:
                    table.add_row(user.username, str(user.id), user.email)
            else:
                print("[yellow]数据库未查询到管理员。[/yellow]")
        console.print(table)


if __name__ == "__main__":
    ServerCommand().loadloop()
