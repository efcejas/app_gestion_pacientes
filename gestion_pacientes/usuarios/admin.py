from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario

# Register your models here.

class UsuarioAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Información Adicional", {"fields": ("rol",)}),
    )

admin.site.register(Usuario, UsuarioAdmin)