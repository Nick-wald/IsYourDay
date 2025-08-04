from enum import Enum

MAX_FILE_SIZE_LIMIT_MB = 4096
STREAM_UPLOAD_LIMIT_MB = 10 # 上传时大于此大小则优化为流式上传

class FILE_PATH(str, Enum):
    """Enum for file storage paths."""
    BASE_PATH = "./media"
    TEMP_PATH = "./media/temp"
    USER_PATH = "./media/user"
    AVATAR_PATH = "./media/user/avatar"