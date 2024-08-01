from django.contrib import admin

from .models import Buildings, Users, UsersBuildings, UserTasks, UserUserTasks


class UserBuildingInline(admin.TabularInline):
    model = UsersBuildings


class UserTasksInline(admin.TabularInline):
    model = UserUserTasks


# Register your models here.
@admin.register(Users)
class UsersAdmin(admin.ModelAdmin):
    readonly_fields = ("telegram_id",)

    list_display = ("telegram_id",)
    search_fields = ("telegram_id",)
    inlines = (UserBuildingInline, UserTasksInline)


@admin.register(UserTasks)
class UserTasksAdmin(admin.ModelAdmin):
    list_display = ("name", "reward", "exp_reward", "lvl_required", "cost", "length")
    search_fields = ("name",)


@admin.register(Buildings)
class BuildingsAdmin(admin.ModelAdmin):
    list_display = ("name", "cost", "income")
    search_fields = ("name",)


admin.site.site_header = "Admin Panel"
admin.site.site_title = "Admin Panel"
admin.site.index_title = "Welcome to Admin Panel"
