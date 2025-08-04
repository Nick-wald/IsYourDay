from sqlmodel import Relationship, SQLModel, Field
from pydantic import BaseModel
from datetime import datetime, timedelta
import uuid


class VirtualUser(SQLModel, table=True):
    """ Virtual user model for isyourday project. """
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        description="Unique identifier for the virtual user"
    )
    real_name: str = Field(
        nullable=False,
        description="Real name of the virtual user"
    )
    sex: int = Field(
        default=0,
        description="0 is unknown, 1 is man, 2 is woman"
    )
    birthday: datetime | None = Field(
        default=None,
        description="Birthday of the virtual user, default is 20 years ago"
    )
    tel: str | None = Field(
        default=None,
        description="Telephone number of the virtual user"
    )
    prompt: str | None = Field(
        default=None,
        description="Prompt for the virtual user, used in AI interactions"
    )
    location: str | None = Field(
        default=None,
        description="Location of the virtual user"
    )
    QQ: str | None = Field(
        default=None,
        description="QQ number of the virtual user"
    )
    wechat: str | None = Field(
        default=None,
        description="WeChat ID of the virtual user"
    )
    identify: str | None = Field(
        default=None,
        description="Identification information of the virtual user"
    )
    is_active: bool = Field(
        default=True,
        description="Indicates if the virtual user is active"
    )
    email: str = Field(
        index=True,
        unique=True,
        nullable=False,
        regex=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$",
        description="Email address of the virtual user"
    )
    updated_at: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp when the virtual user was last updated"
    )
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp when the virtual user was created"
    )
    
    events: list["Event"] = Relationship(
        back_populates="user", cascade_delete=True
    )


class VirtualUserPublic(BaseModel):
    """ Data model for creating a new virtual user. """
    real_name: str | None = None
    sex: int = 0
    birthday: datetime | None = None
    tel: str | None = None
    prompt: str | None = None
    location: str | None = None
    QQ: str | None = None
    wechat: str | None = None
    identify: str | None = None
    email: str
    
    
class Event(SQLModel, table=True):
    """ Event model for isyourday project. """
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        description="Unique identifier for the event"
    )
    user_id: uuid.UUID = Field(
        foreign_key="virtualuser.id",
        nullable=False,
        ondelete="CASCADE",
        description="ID of the virtual user associated with the event"
    )
    user: VirtualUser = Relationship(back_populates="events")
    title: str = Field(
        nullable=False,
        description="Title of the event"
    )
    description: str | None = Field(
        default=None,
        description="Description of the event"
    )
    prompt: str | None = Field(
        default=None,
        description="Prompt for the event, used in AI interactions"
    )
    start_time: datetime | None = Field(
        default_factory=datetime.now,
        description="Start time of the event"
    )
    end_time: datetime | None = Field(
        default=None,
        description="End time of the event, if applicable"
    )
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp when the event was created"
    )


class EventPublic(BaseModel):
    """ Data model for creating a new event. """
    title: str
    description: str | None = None
    prompt: str | None = None
    start_time: datetime | None = Field(default_factory=datetime.now)
    end_time: datetime | None = None
