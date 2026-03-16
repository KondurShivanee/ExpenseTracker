from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from datetime import datetime, timedelta

from .models import Expense, Category
from .forms import ExpenseForm, CategoryForm, ExpenseFilterForm


class DashboardView(ListView):
    """Dashboard view showing expense summary and recent expenses."""
    model = Expense
    template_name = 'expenses/dashboard.html'
    context_object_name = 'recent_expenses'

    def get_queryset(self):
        return Expense.objects.select_related('category')[:5]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Current month stats
        today = datetime.today()
        first_day_of_month = today.replace(day=1)

        monthly_expenses = Expense.objects.filter(
            date__gte=first_day_of_month,
            date__lte=today
        )

        context['total_this_month'] = monthly_expenses.aggregate(
            total=Sum('amount')
        )['total'] or 0

        context['expense_count'] = monthly_expenses.count()

        # Category breakdown for current month
        context['category_breakdown'] = monthly_expenses.values(
            'category__name', 'category__color'
        ).annotate(
            total=Sum('amount')
        ).order_by('-total')[:5]

        # Monthly trend (last 6 months)
        six_months_ago = today - timedelta(days=180)
        context['monthly_trend'] = Expense.objects.filter(
            date__gte=six_months_ago
        ).annotate(
            month=TruncMonth('date')
        ).values('month').annotate(
            total=Sum('amount')
        ).order_by('month')

        # All-time total
        context['all_time_total'] = Expense.objects.aggregate(
            total=Sum('amount')
        )['total'] or 0

        return context


class ExpenseListView(ListView):
    """List view for all expenses with filtering."""
    model = Expense
    template_name = 'expenses/expense_list.html'
    context_object_name = 'expenses'
    paginate_by = 10

    def get_queryset(self):
        queryset = Expense.objects.select_related('category')

        # Apply filters
        category = self.request.GET.get('category')
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')

        if category:
            queryset = queryset.filter(category_id=category)
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = ExpenseFilterForm(self.request.GET)
        context['total'] = self.get_queryset().aggregate(
            total=Sum('amount')
        )['total'] or 0
        return context


class ExpenseCreateView(CreateView):
    """View for creating a new expense."""
    model = Expense
    form_class = ExpenseForm
    template_name = 'expenses/expense_form.html'
    success_url = reverse_lazy('expense_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Expense'
        context['button_text'] = 'Add Expense'
        return context


class ExpenseUpdateView(UpdateView):
    """View for updating an existing expense."""
    model = Expense
    form_class = ExpenseForm
    template_name = 'expenses/expense_form.html'
    success_url = reverse_lazy('expense_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Expense'
        context['button_text'] = 'Update Expense'
        return context


class ExpenseDeleteView(DeleteView):
    """View for deleting an expense."""
    model = Expense
    template_name = 'expenses/expense_confirm_delete.html'
    success_url = reverse_lazy('expense_list')


class CategoryListView(ListView):
    """List view for all categories."""
    model = Category
    template_name = 'expenses/category_list.html'
    context_object_name = 'categories'


class CategoryCreateView(CreateView):
    """View for creating a new category."""
    model = Category
    form_class = CategoryForm
    template_name = 'expenses/category_form.html'
    success_url = reverse_lazy('category_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Category'
        context['button_text'] = 'Add Category'
        return context


class CategoryUpdateView(UpdateView):
    """View for updating an existing category."""
    model = Category
    form_class = CategoryForm
    template_name = 'expenses/category_form.html'
    success_url = reverse_lazy('category_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Category'
        context['button_text'] = 'Update Category'
        return context


class CategoryDeleteView(DeleteView):
    """View for deleting a category."""
    model = Category
    template_name = 'expenses/category_confirm_delete.html'
    success_url = reverse_lazy('category_list')
