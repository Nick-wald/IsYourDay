import os
from sqlmodel import create_engine, SQLModel, Session, select
from fastapi import Depends
from typing import Annotated
import importlib
import sys
from pathlib import Path

from .settings import SQL_DEBUG_ECHO, SQL_BACKEND

connect_args = {"check_same_thread": False}
engine = create_engine(SQL_BACKEND, echo=SQL_DEBUG_ECHO)


def get_session():
        with Session(engine) as session:
            yield session


def collect_all_models():
    import typer
    from rich import print
    from rich.table import Table
    from rich.console import Console
    """自动搜集项目中所有models.py文件中的SQLModel模型"""
    # 获取项目根目录
    project_root = Path(__file__).parent.parent
    app_dir = project_root / "app"
    
    # 确保app目录在Python路径中
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    # 搜索所有models.py文件
    models_files = []
    for models_file in app_dir.rglob("models.py"):
        # 转换为相对于项目根目录的模块路径
        relative_path = models_file.relative_to(project_root)
        module_path = str(relative_path).replace(os.sep, ".").replace(".py", "")
        models_files.append(module_path)
    console = Console()
    # 导入所有models模块
    print("[bold yellow]Collecting models...[/bold yellow]")
    table = Table("Path", "Models", "Status")
    for module_path in models_files:
        try:
            model_file = importlib.import_module(module_path)
            model_in_file = [getattr(model_file, attr) for attr in dir(model_file) if isinstance(getattr(model_file, attr), type) and issubclass(getattr(model_file, attr), SQLModel)]
            # 验证其中table属性是否为真
            model_in_file = [model for model in model_in_file if hasattr(model, '__table__') and model.__table__ is not None]
            for model in model_in_file:
                table.add_row(f"[bold green]{module_path}[/bold green]", f"[bold green]{model.__name__}[/bold green]","[green]OK[/green]")
        except Exception as e:
            table.add_row(f"[bold red]{module_path}[/bold red]", "[bold red]None[/bold red]", "[red]ERROR[/red]")
            print(f"Error importing {module_path}: {e}")
    console.print(table)
    return SQLModel.metadata


def create_db_and_tables():
        collect_all_models().create_all(engine)   


SessionDep = Annotated[Session, Depends(get_session)]

if __name__ == "__main__":
    import typer
    create_db_and_tables()
    typer.echo(typer.style("Database and tables created successfully.", fg=typer.colors.GREEN, bold=True))
