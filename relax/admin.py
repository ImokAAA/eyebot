from django.contrib import admin

# Register your models here.

from .forms import ProfileForm
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
	list_display = ('id', 'external_id')   
	form = ProfileForm
