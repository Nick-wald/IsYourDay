import os
SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

OAUTH2_SCOPE = {
    "auth:read_basic": "允许获取账户的基本信息（不含敏感信息）",
    "auth:read_all": "允许获取账户的全部信息（含敏感信息）",
    "auth:write": "允许修改账户信息",
    "auth:delete": "允许删除账户",
    "file:read": "允许读取文件信息、下载文件",
    "file:upload": "允许上传文件",
    "file:write": "允许修改文件信息",
    "file:delete": "允许删除文件",
    "isyourday:read": "允许获取虚拟用户信息",
    "isyourday:write": "允许创建或修改虚拟用户信息",
    "isyourday:delete": "允许删除虚拟用户信息",
}

EMAIL_SENDER_ACCOUNT = os.getenv("EMAIL_SENDER_ACCOUNT", "default_email_sender_account")
EMAIL_SENDER_PASSWORD = os.getenv("EMAIL_SENDER_PASSWORD", "default_email_sender_password")
EMAIL_SENDER_SMTP = os.getenv("EMAIL_SENDER_SMTP", "default_smtp_server")
EMAIL_SENDER_PORT = int(os.getenv("EMAIL_SENDER_PORT", 465))