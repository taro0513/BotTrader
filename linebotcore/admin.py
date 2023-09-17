from django.contrib import admin

# Register your models here.

from django.contrib import admin

from .models import StockWatchList, ChatGPT

class AdminStockWatchList(admin.ModelAdmin):
    list_display = ('user_id', 'code', 'code_type')

class AdminChatGPT(admin.ModelAdmin):
    list_display = ('user_id', 'active')

admin.site.register(StockWatchList, AdminStockWatchList)
admin.site.register(ChatGPT, AdminChatGPT)