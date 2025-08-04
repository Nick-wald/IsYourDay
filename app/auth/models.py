from sqlmodel import Field, SQLModel, Relationship, Text
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
import jwt
import uuid
from typing import TYPE_CHECKING, List, Optional

from .settings import SECRET_KEY, ALGORITHM
if TYPE_CHECKING:
    from ..file.models import FileDB


class UserBase(SQLModel):
    """Base model for user data."""
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        description="Unique identifier for the user"
        )
    username: str = Field(
        index=True,
        unique=True,
        nullable=False,
        description="Unique username for the user"
        )
    email: str = Field(
        index=True,
        unique=True,
        nullable=False,
        regex=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$",
        description="User's email address"
        )
    is_superuser: bool = Field(
        default=False,
        description="Is the user a superuser?"
        )
    is_stuff: bool = Field(
        default=False,
        description="Is the user a staff member?"
        )
    is_active: bool = Field(
        default=True,
        nullable=False,
        description="Is the user active?"
        )
    password: str = Field(
        nullable=False,
        description="Hashed password"
        )


class User(UserBase, table=True):
    """User model for authentication and user management."""
    real_name: str | None = Field(default=None, description="User's real name")
    avatar_id: uuid.UUID | None = Field(
        default=None,
        foreign_key="filedb.id",
        description="ID of the user's avatar file"
    )
    email_send_history: List["EmailSendHistory"] = Relationship(
        back_populates="sender",
        cascade_delete=True
    )
    
    # Relationships with explicit foreign_keys
    challenge_codes: List["ChallengeCodeDB"] = Relationship(
        back_populates="user",
        cascade_delete=True
    )
    
    files: List["FileDB"] = Relationship(
        back_populates="uploader",
        sa_relationship_kwargs={"foreign_keys": "[FileDB.uploader_id]"}
    )
    avatar: Optional["FileDB"] = Relationship(
        back_populates="avatar_users",
        sa_relationship_kwargs={"foreign_keys": "[User.avatar_id]"}
    )
        


class UserPublic(BaseModel):
    """Public user model for API responses."""
    id: uuid.UUID
    username: str
    email: str = Field(
        regex=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    )
    avatar_id: uuid.UUID | None = None
    active: bool
    is_superuser: bool = False
    is_stuff: bool = False

    @classmethod
    def from_user(cls, user: User):
        """Create a public user model from a User instance."""
        return cls(
            id=user.id,
            username=user.username,
            email=user.email,
            active=user.is_active,
            avatar_id=user.avatar_id,
            is_superuser=user.is_superuser,
            is_stuff=user.is_stuff
        )


class UserUpdate(SQLModel):
    """Model for updating user information."""
    username: str | None = None
    email: str | None = None
    real_name: str | None = None
    password: str | None = None


class EmailSendHistoryUpdate(SQLModel):
    """Model for updating email send history."""
    receiver_type: str | None = None
    receiver_emails: str | None = None
    receiver_names: str | None = None
    subject: str | None = None
    content: str | None = None
    attachments: str | None = None


class Token(BaseModel):
    """Token model for user authentication."""
    access_token: str
    token_type: str = "bearer"

    @staticmethod
    def create_token(data: dict, expires_delta: timedelta | None = None):
        """Create a new token instance."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt


class TokenData(BaseModel):
    """Data model for token payload."""
    user_id: uuid.UUID
    scopes: list[str] = []

def random_code_generator(length: int = 30) -> str:
    """Generate a random challenge code of specified length."""
    import random
    import string
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

class ChallengeCodeDB(SQLModel, table=True):
    """Model for storing challenge codes."""
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    code: str = Field(default_factory=random_code_generator, index=True, unique=True, nullable=False, description="Challenge code")
    call_from: str | None = Field(
        default=None,
        description="Optional field to indicate where the challenge code was called from"
    )
    user_id: uuid.UUID = Field(foreign_key="user.id", ondelete="CASCADE", nullable=False, description="ID of the user associated with the challenge code")
    created_at: datetime = Field(default_factory=datetime.now, nullable=False, description="Creation timestamp of the challenge code")
    
    user: User = Relationship(back_populates="challenge_codes")  # Assuming User has a relationship defined


class EmailSendHistory(SQLModel, table=True):
    """Model for storing email sending history."""
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    receiver_type: str = Field(
        description="Email user search type"
    )
    receiver_emails: str = Field(
        index=True,
        nullable=False,
        description="Email address of the receiver, comma-separated"
    )
    receiver_names: str = Field(
        description="Name of the email receiver, comma-separated",
        nullable=False
    )
    sender_id: uuid.UUID = Field(
        foreign_key="user.id",
        nullable=False,
        description="ID of the user who sent the email"
    )
    sender: User = Relationship(back_populates="email_send_history")
    subject: str = Field(nullable=False, description="Subject of the email")
    content: str = Field(nullable=False, sa_type=Text, description="Content of the email")
    attachments: str = Field(
        default="",
        description="Comma-separated list of attachment file IDs (if any)"
    )
    sent_at: datetime = Field(default_factory=datetime.now, nullable=False, description="Timestamp when the email was sent")
    status: str = Field(default="pending", description="Status of the email sending (e.g., pending, success, failed)")
    reason: str | None = Field(
        default=None,
        description="Reason for failure if the email sending failed"
    )
