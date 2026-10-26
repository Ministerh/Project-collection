from django.shortcuts import redirect, render, get_object_or_404
from django.db.models import Sum
from django.views.decorators.http import require_POST
from .forms import ExpenseForm
from .models import Expense

def expenses_list(request):
    expenses = Expense.objects.all()
    category = request.GET.get('category')
    if category:
        expenses = expenses.filter(category__iexact=category)
    return render(request, "expenses/expense_list.html", {"expenses": expenses, "category": category})
def add_expense(request):
    if request.method == "POST":
        form = ExpenseForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect("expenses_list")
    else:
        form = ExpenseForm()
    return render(request, "expenses/expense_form.html", {"form": form})

def expense_summary(request):
    totals= (Expense.objects.values("category").annotate(total=Sum("amount")).order_by("-total"))
    grand_total= Expense.objects.aggregate(total=Sum("amount"))["total"] or 0
    return render(request, "expenses/expense_summary.html", {"totals": totals, "grand_total": grand_total})


@require_POST
def expense_delete(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    expense.delete()
    return redirect("expenses_list")