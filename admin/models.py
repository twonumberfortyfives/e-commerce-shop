from fastapi_admin.app import app as admin_app
from fastapi_admin.providers.login import UsernamePasswordProvider
from fastapi_admin.models import AbstractAdmin

from database.models import DBUser
from database.engine import engine


class UserAdmin(AbstractAdmin):
    # Customize how you display the User model in the admin panel
    search_fields = ["username", "email"]
    list_display = ["id", "username", "email", "role"]


async def init_fastapi_admin():
    await admin_app.init(
        admin_secret="your-secret-key",  # Change this to a secure secret
        database=engine,  # Use the SQLAlchemy engine
        models=[UserAdmin],  # Add your models here
        providers=[
            UsernamePasswordProvider(
                admin_model=DBUser,  # Admin login model
                login_path="http://localhost:8000/api/v1/login"
            ),
        ],
    )
