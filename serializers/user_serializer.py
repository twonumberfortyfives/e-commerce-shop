from pydantic import BaseModel, Field, model_validator, EmailStr


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_]+$")
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    password_confirm: str = Field(min_length=8, max_length=128)

    @model_validator(mode="before")
    def passwords_match(cls, values):
        if values["password"] != values["password_confirm"]:
            raise ValueError("Passwords do not match")
        return values


class UserCreateOutput(BaseModel):
    username: str
    email: str
    profile_picture: str


class Token(BaseModel):
    access_token: str
    token_type: str


class User(BaseModel):
    username: str
    email: str | None = None
    disabled: bool | None = None


class LoginInput(BaseModel):
    username: str
    password: str


class Logout(BaseModel):
    message: str


class EmailVerification(BaseModel):
    message: str


class MyProfile(BaseModel):
    username: str
    email: str
    profile_picture: str
    phone_number: str | None
