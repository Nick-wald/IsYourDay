DOCS_TITLE = "IsYourDay项目后端"

DOCS_DESCRIPTION = """
此项目提供了一个集成用户信息管理，文件管理的解决方案，提供数据支持。

它使用 FastAPI 框架构建，支持异步操作和高并发处理。"""

DOCS_TAG_METADATA = {
    "auth": {
        "name": "Auth",
        "description": "用户认证相关操作",
    },
    "users": {
        "name": "Users",
        "description": "用户管理相关操作",
    },
    "oauth2": {
        "name": "OAuth2",
        "description": "OAuth2 认证相关操作",
    },
}

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

import os
mysql_url = os.getenv("SQLALCHEMY_DATABASE_URL", sqlite_url)

SQL_BACKEND = mysql_url
SQL_DEBUG_ECHO = False