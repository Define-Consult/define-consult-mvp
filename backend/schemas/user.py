from pydantic import BaseModel, Field

class UserCreate(BaseModel):
    firebase_uid: str = Field(..., description="The unique Firebase User ID.")
    email: str
    name: str | None = None
    avatar_url: str | None = None