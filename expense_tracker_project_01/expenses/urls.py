from django.urls import path
from . import views

urlpatterns = [
    path('', views.expenses_list, name="expenses_list"),
    path('add/', views.add_expense, name="add_expense"),
    path("summary/", views.expense_summary, name="expense_summary"),
    path("<int:pk>/delete", views.expense_delete, name="expense_delete"),
]