from pydantic import BaseModel, Field, field_validator, model_validator


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_]+$")
    email: str
    password: str = Field(..., min_length=8, max_length=128)
    password_confirm: str = Field(..., min_length=8, max_length=128)

    @model_validator(mode="before")
    def passwords_match(cls, values):
        if values["password"] != values["password_confirm"]:
            raise ValueError("Passwords do not match")
        return values
