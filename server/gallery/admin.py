# -*- coding: utf-8 -*-
from django.contrib import admin
from gallery.models import Settings

class SettingsInLine(admin.TabularInline):
    model = Settings

class SettingsAdmin(admin.ModelAdmin):
    inline = (SettingsInLine)
    lis_display = ('Settings')

admin.site.register(Settings)
