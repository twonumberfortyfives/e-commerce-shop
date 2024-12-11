from sqladmin import ModelView

from database.models import DBUser
from main import admin


class UserAdmin(ModelView, model=DBUser):
    column_list = [DBUser.id, DBUser.username]
    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-user"
    category = "accounts"


admin.add_view(UserAdmin)
