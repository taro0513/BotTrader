from django.db import models

# Create your models here.

class StockWatchList(models.Model):
    user_id = models.CharField(max_length=100, null=False)
    code = models.CharField(max_length=50, null=False)
    code_type = models.CharField(max_length=50, null=False)

class ChatGPT(models.Model):
    user_id = models.CharField(max_length=100, null=False)
    active = models.BooleanField(default=False)
    

class HistoricalRecord(models.Model):
    user_id = models.CharField(max_length=100, null=False)
    message = models.TextField(null=False)
    action = models.CharField(max_length=100, null=False)
    remark = models.CharField(max_length=100, null=True)
    created_at = models.DateTimeField(null=False, auto_now_add=True)
