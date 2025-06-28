from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ("email","username","phone_number","client", "is_staff", "is_active",)
    list_filter = ("email","username","phone_number","client", "is_staff", "is_active",)
    fieldsets = (
        (None, {"fields": ("email", "password","username","phone_number","client")}),
        ("Permissions", {"fields": ("is_staff", "is_active", "groups", "user_permissions")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email","username","phone_number","client","password1", "password2", "is_staff",
                "is_active", "groups", "user_permissions"
            )}
        ),
    )
    search_fields = ("email",'username')
    ordering = ("email",)


admin.site.register(CustomUser, CustomUserAdmin)