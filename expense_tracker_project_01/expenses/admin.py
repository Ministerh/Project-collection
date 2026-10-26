from django.contrib import admin
from expenses.models import Expense

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('amount', 'category', 'description', 'date')
    list_filter = ('category', 'date')

