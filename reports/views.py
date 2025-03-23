from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, TemplateView
from django.contrib import messages
from django.db.models import Sum, Count, Avg
from django.db.models.functions import TruncMonth
from django.utils import timezone
from datetime import timedelta
from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse
from .models import ProductConsumption, ShoppingExpense, CategoryExpense, ProductWastage
from .forms import ProductConsumptionForm, ShoppingExpenseForm, ProductWastageForm
from .notifications import generate_report_notifications
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.template.loader import render_to_string
from .export import export_to_csv, export_to_pdf
import csv
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from datetime import datetime
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'reports/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        thirty_days_ago = timezone.now() - timedelta(days=30)

        # Generuj powiadomienia
        generate_report_notifications(user)

        # Statystyki zużycia
        consumption_data = ProductConsumption.objects.filter(
            user=user,
            consumption_date__gte=thirty_days_ago
        )
        context['consumption_stats'] = {
            'total_consumptions': consumption_data.count(),
            'total_quantity': consumption_data.aggregate(total=Sum('quantity'))['total'] or 0
        }
        context['top_products'] = consumption_data.values(
            'product__name'
        ).annotate(
            total_quantity=Sum('quantity'),
            count=Count('id')
        ).order_by('-total_quantity')[:5]

        # Statystyki wydatków
        expense_data = ShoppingExpense.objects.filter(
            user=user,
            shopping_date__gte=thirty_days_ago
        )
        context['expense_stats'] = {
            'total_expenses': expense_data.count(),
            'total_amount': expense_data.aggregate(total=Sum('total_amount'))['total'] or 0
        }

        # Statystyki marnowania
        wastage_data = ProductWastage.objects.filter(
            user=user,
            wastage_date__gte=thirty_days_ago
        )
        context['wastage_stats'] = {
            'total_wastages': wastage_data.count(),
            'total_quantity': wastage_data.aggregate(total=Sum('quantity'))['total'] or 0
        }

        # Trendy wydatków
        context['expense_trends'] = expense_data.annotate(
            month=TruncMonth('shopping_date')
        ).values('month').annotate(
            total=Sum('total_amount')
        ).order_by('month')

        return context

class ProductConsumptionCreateView(LoginRequiredMixin, CreateView):
    model = ProductConsumption
    form_class = ProductConsumptionForm
    template_name = 'reports/product_consumption_form.html'
    success_url = reverse_lazy('reports:dashboard')

    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, 'Zużycie produktu zostało dodane.')
        generate_report_notifications(self.request.user)
        return response

class ShoppingExpenseCreateView(LoginRequiredMixin, CreateView):
    model = ShoppingExpense
    form_class = ShoppingExpenseForm
    template_name = 'reports/shopping_expense_form.html'
    success_url = reverse_lazy('reports:dashboard')

    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, 'Wydatek został dodany.')
        generate_report_notifications(self.request.user)
        return response

class ProductWastageCreateView(LoginRequiredMixin, CreateView):
    model = ProductWastage
    form_class = ProductWastageForm
    template_name = 'reports/product_wastage_form.html'
    success_url = reverse_lazy('reports:dashboard')

    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, 'Marnowanie produktu zostało dodane.')
        generate_report_notifications(self.request.user)
        return response

@login_required
def expense_report(request):
    now = timezone.now()
    month_ago = now - timedelta(days=30)

    expenses = ShoppingExpense.objects.filter(
        user=request.user,
        shopping_date__gte=month_ago
    ).order_by('-shopping_date')

    total_expenses = expenses.aggregate(total=Sum('total_amount'))['total'] or 0
    avg_expense = expenses.aggregate(avg=Avg('total_amount'))['avg'] or 0
    total_shopping_trips = expenses.count()

    # Przygotuj dane dla wykresu
    expense_trends = expenses.annotate(
        month=TruncMonth('shopping_date')
    ).values('month').annotate(
        total=Sum('total_amount')
    ).order_by('month')

    # Konwertuj daty na format JSON
    for trend in expense_trends:
        trend['month'] = trend['month'].strftime('%Y-%m-%d')

    context = {
        'expenses': expenses,
        'total_expenses': total_expenses,
        'avg_expense': avg_expense,
        'total_shopping_trips': total_shopping_trips,
        'expense_trends': DjangoJSONEncoder().encode(list(expense_trends)),
    }
    return render(request, 'reports/expense_report.html', context)

@login_required
def consumption_report(request):
    now = timezone.now()
    month_ago = now - timedelta(days=30)

    consumptions = ProductConsumption.objects.filter(
        user=request.user,
        consumption_date__gte=month_ago
    ).order_by('-consumption_date')

    total_consumption = consumptions.aggregate(total=Sum('quantity'))['total'] or 0
    avg_consumption = consumptions.aggregate(avg=Avg('quantity'))['avg'] or 0
    total_products = consumptions.values('product').distinct().count()

    # Przygotuj dane dla wykresu
    consumption_trends = consumptions.annotate(
        month=TruncMonth('consumption_date')
    ).values('month').annotate(
        total=Sum('quantity')
    ).order_by('month')

    # Konwertuj daty na format JSON
    for trend in consumption_trends:
        trend['month'] = trend['month'].strftime('%Y-%m-%d')

    context = {
        'consumptions': consumptions,
        'total_consumption': total_consumption,
        'avg_consumption': avg_consumption,
        'total_products': total_products,
        'consumption_trends': DjangoJSONEncoder().encode(list(consumption_trends)),
    }
    return render(request, 'reports/consumption_report.html', context)

@login_required
def wastage_report(request):
    now = timezone.now()
    month_ago = now - timedelta(days=30)

    wastages = ProductWastage.objects.filter(
        user=request.user,
        wastage_date__gte=month_ago
    ).order_by('-wastage_date')

    total_wastage = wastages.aggregate(total=Sum('quantity'))['total'] or 0
    avg_wastage = wastages.aggregate(avg=Avg('quantity'))['avg'] or 0
    total_products = wastages.values('product').distinct().count()

    # Przygotuj dane dla wykresu
    wastage_trends = wastages.annotate(
        month=TruncMonth('wastage_date')
    ).values('month').annotate(
        total=Sum('quantity')
    ).order_by('month')

    # Konwertuj daty na format JSON
    for trend in wastage_trends:
        trend['month'] = trend['month'].strftime('%Y-%m-%d')

    context = {
        'wastages': wastages,
        'total_wastage': total_wastage,
        'avg_wastage': avg_wastage,
        'total_products': total_products,
        'wastage_trends': DjangoJSONEncoder().encode(list(wastage_trends)),
    }
    return render(request, 'reports/wastage_report.html', context)

def export_expense_report(request, format):
    """Eksportuje raport wydatków do CSV lub PDF."""
    if format not in ['csv', 'pdf']:
        return HttpResponse('Nieprawidłowy format', status=400)
    
    # Pobierz dane
    end_date = timezone.now()
    start_date = end_date - timedelta(days=30)
    
    expenses = ShoppingExpense.objects.filter(
        user=request.user,
        shopping_date__range=[start_date, end_date]
    ).order_by('-shopping_date')
    
    total_expenses = expenses.aggregate(total=Sum('total_amount'))['total'] or 0
    avg_expense = expenses.aggregate(avg=Avg('total_amount'))['avg'] or 0
    
    context = {
        'expenses': expenses,
        'total_expenses': total_expenses,
        'avg_expense': avg_expense,
        'start_date': start_date,
        'end_date': end_date,
    }
    
    if format == 'csv':
        response = export_to_csv(
            expenses,
            ['shopping_date', 'shopping_list__name', 'total_amount'],
            ['Data', 'Lista zakupów', 'Kwota']
        )
        response['Content-Disposition'] = 'attachment; filename="expense_report.csv"'
        return response
    else:
        html = render_to_string('reports/pdf/expense_report.html', context)
        response = export_to_pdf(html, 'expense_report.pdf')
        return response

def export_consumption_report(request, format):
    """Eksportuje raport zużycia do CSV lub PDF."""
    if format not in ['csv', 'pdf']:
        return HttpResponse('Nieprawidłowy format', status=400)
    
    # Pobierz dane
    end_date = timezone.now()
    start_date = end_date - timedelta(days=30)
    
    consumptions = ProductConsumption.objects.filter(
        user=request.user,
        consumption_date__range=[start_date, end_date]
    ).order_by('-consumption_date')
    
    total_consumption = consumptions.count()
    avg_consumption = consumptions.aggregate(avg=Avg('quantity'))['avg'] or 0
    
    context = {
        'consumptions': consumptions,
        'total_consumption': total_consumption,
        'avg_consumption': avg_consumption,
        'start_date': start_date,
        'end_date': end_date,
    }
    
    if format == 'csv':
        response = export_to_csv(
            consumptions,
            ['consumption_date', 'product__name', 'product__category__name', 'quantity', 'unit'],
            ['Data', 'Produkt', 'Kategoria', 'Ilość', 'Jednostka']
        )
        response['Content-Disposition'] = 'attachment; filename="consumption_report.csv"'
        return response
    else:
        html = render_to_string('reports/pdf/consumption_report.html', context)
        response = export_to_pdf(html, 'consumption_report.pdf')
        return response

def export_wastage_report(request, format):
    """Eksportuje raport marnowania do CSV lub PDF."""
    if format not in ['csv', 'pdf']:
        return HttpResponse('Nieprawidłowy format', status=400)
    
    # Pobierz dane
    end_date = timezone.now()
    start_date = end_date - timedelta(days=30)
    
    wastages = ProductWastage.objects.filter(
        user=request.user,
        wastage_date__range=[start_date, end_date]
    ).order_by('-wastage_date')
    
    total_wastage = wastages.count()
    avg_wastage = wastages.aggregate(avg=Avg('quantity'))['avg'] or 0
    
    context = {
        'wastages': wastages,
        'total_wastage': total_wastage,
        'avg_wastage': avg_wastage,
        'start_date': start_date,
        'end_date': end_date,
    }
    
    if format == 'csv':
        response = export_to_csv(
            wastages,
            ['wastage_date', 'product__name', 'product__category__name', 'quantity', 'unit', 'reason'],
            ['Data', 'Produkt', 'Kategoria', 'Ilość', 'Jednostka', 'Powód']
        )
        response['Content-Disposition'] = 'attachment; filename="wastage_report.csv"'
        return response
    else:
        html = render_to_string('reports/pdf/wastage_report.html', context)
        response = export_to_pdf(html, 'wastage_report.pdf')
        return response

@login_required
def expense_trends_api(request):
    """API endpoint zwracający dane trendów wydatków."""
    now = timezone.now()
    month_ago = now - timedelta(days=30)

    expenses = ShoppingExpense.objects.filter(
        user=request.user,
        shopping_date__gte=month_ago
    )

    trends = expenses.annotate(
        month=TruncMonth('shopping_date')
    ).values('month').annotate(
        total=Sum('total_amount')
    ).order_by('month')

    # Konwertuj daty na format JSON
    for trend in trends:
        trend['month'] = trend['month'].strftime('%Y-%m-%d')

    return JsonResponse(list(trends), safe=False)

@login_required
def consumption_trends_api(request):
    """API endpoint zwracający dane trendów zużycia."""
    now = timezone.now()
    month_ago = now - timedelta(days=30)

    consumptions = ProductConsumption.objects.filter(
        user=request.user,
        consumption_date__gte=month_ago
    )

    trends = consumptions.annotate(
        month=TruncMonth('consumption_date')
    ).values('month').annotate(
        total=Sum('quantity')
    ).order_by('month')

    # Konwertuj daty na format JSON
    for trend in trends:
        trend['month'] = trend['month'].strftime('%Y-%m-%d')

    return JsonResponse(list(trends), safe=False)

@login_required
def wastage_trends_api(request):
    """API endpoint zwracający dane trendów marnowania."""
    now = timezone.now()
    month_ago = now - timedelta(days=30)

    wastages = ProductWastage.objects.filter(
        user=request.user,
        wastage_date__gte=month_ago
    )

    trends = wastages.annotate(
        month=TruncMonth('wastage_date')
    ).values('month').annotate(
        total=Sum('quantity')
    ).order_by('month')

    # Konwertuj daty na format JSON
    for trend in trends:
        trend['month'] = trend['month'].strftime('%Y-%m-%d')

    return JsonResponse(list(trends), safe=False)

@login_required
def export_expense_csv(request):
    thirty_days_ago = timezone.now() - timedelta(days=30)
    expenses = ShoppingExpense.objects.filter(
        user=request.user,
        shopping_date__gte=thirty_days_ago
    ).order_by('-shopping_date')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="expenses.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Data', 'Lista zakupów', 'Kwota'])
    
    for expense in expenses:
        writer.writerow([
            expense.shopping_date,
            expense.shopping_list.name,
            expense.total_amount
        ])
    
    return response

@login_required
def export_expense_pdf(request):
    thirty_days_ago = timezone.now() - timedelta(days=30)
    expenses = ShoppingExpense.objects.filter(
        user=request.user,
        shopping_date__gte=thirty_days_ago
    ).order_by('-shopping_date')
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="expenses.pdf"'
    
    p = canvas.Canvas(response, pagesize=letter)
    p.setTitle("Raport wydatków")
    
    # Nagłówek
    p.setFont("Helvetica-Bold", 16)
    p.drawString(1*inch, 10*inch, "Raport wydatków")
    p.setFont("Helvetica", 12)
    
    # Data
    p.drawString(1*inch, 9.5*inch, f"Data: {datetime.now().strftime('%Y-%m-%d')}")
    
    # Tabela
    y = 9*inch
    p.setFont("Helvetica-Bold", 12)
    p.drawString(1*inch, y, "Data")
    p.drawString(3*inch, y, "Lista zakupów")
    p.drawString(6*inch, y, "Kwota")
    
    p.setFont("Helvetica", 10)
    y -= 0.5*inch
    
    for expense in expenses:
        p.drawString(1*inch, y, str(expense.shopping_date))
        p.drawString(3*inch, y, expense.shopping_list.name)
        p.drawString(6*inch, y, f"{expense.total_amount} zł")
        y -= 0.3*inch
        
        if y < 1*inch:
            p.showPage()
            y = 9*inch
    
    p.showPage()
    p.save()
    
    return response

@login_required
def export_consumption_csv(request):
    thirty_days_ago = timezone.now() - timedelta(days=30)
    consumptions = ProductConsumption.objects.filter(
        user=request.user,
        consumption_date__gte=thirty_days_ago
    ).order_by('-consumption_date')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="consumption.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Data', 'Produkt', 'Ilość', 'Jednostka'])
    
    for consumption in consumptions:
        writer.writerow([
            consumption.consumption_date,
            consumption.product.name,
            consumption.quantity,
            consumption.unit
        ])
    
    return response

@login_required
def export_consumption_pdf(request):
    thirty_days_ago = timezone.now() - timedelta(days=30)
    consumptions = ProductConsumption.objects.filter(
        user=request.user,
        consumption_date__gte=thirty_days_ago
    ).order_by('-consumption_date')
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="consumption.pdf"'
    
    p = canvas.Canvas(response, pagesize=letter)
    p.setTitle("Raport zużycia")
    
    # Nagłówek
    p.setFont("Helvetica-Bold", 16)
    p.drawString(1*inch, 10*inch, "Raport zużycia produktów")
    p.setFont("Helvetica", 12)
    
    # Data
    p.drawString(1*inch, 9.5*inch, f"Data: {datetime.now().strftime('%Y-%m-%d')}")
    
    # Tabela
    y = 9*inch
    p.setFont("Helvetica-Bold", 12)
    p.drawString(1*inch, y, "Data")
    p.drawString(3*inch, y, "Produkt")
    p.drawString(6*inch, y, "Ilość")
    p.drawString(7.5*inch, y, "Jednostka")
    
    p.setFont("Helvetica", 10)
    y -= 0.5*inch
    
    for consumption in consumptions:
        p.drawString(1*inch, y, str(consumption.consumption_date))
        p.drawString(3*inch, y, consumption.product.name)
        p.drawString(6*inch, y, str(consumption.quantity))
        p.drawString(7.5*inch, y, consumption.unit)
        y -= 0.3*inch
        
        if y < 1*inch:
            p.showPage()
            y = 9*inch
    
    p.showPage()
    p.save()
    
    return response

@login_required
def export_wastage_csv(request):
    thirty_days_ago = timezone.now() - timedelta(days=30)
    wastages = ProductWastage.objects.filter(
        user=request.user,
        wastage_date__gte=thirty_days_ago
    ).order_by('-wastage_date')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="wastage.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Data', 'Produkt', 'Ilość', 'Jednostka', 'Powód'])
    
    for wastage in wastages:
        writer.writerow([
            wastage.wastage_date,
            wastage.product.name,
            wastage.quantity,
            wastage.unit,
            wastage.reason
        ])
    
    return response

@login_required
def export_wastage_pdf(request):
    thirty_days_ago = timezone.now() - timedelta(days=30)
    wastages = ProductWastage.objects.filter(
        user=request.user,
        wastage_date__gte=thirty_days_ago
    ).order_by('-wastage_date')
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="wastage.pdf"'
    
    p = canvas.Canvas(response, pagesize=letter)
    p.setTitle("Raport marnowania")
    
    # Nagłówek
    p.setFont("Helvetica-Bold", 16)
    p.drawString(1*inch, 10*inch, "Raport marnowania produktów")
    p.setFont("Helvetica", 12)
    
    # Data
    p.drawString(1*inch, 9.5*inch, f"Data: {datetime.now().strftime('%Y-%m-%d')}")
    
    # Tabela
    y = 9*inch
    p.setFont("Helvetica-Bold", 12)
    p.drawString(1*inch, y, "Data")
    p.drawString(2.5*inch, y, "Produkt")
    p.drawString(5*inch, y, "Ilość")
    p.drawString(6.5*inch, y, "Jednostka")
    p.drawString(8*inch, y, "Powód")
    
    p.setFont("Helvetica", 10)
    y -= 0.5*inch
    
    for wastage in wastages:
        p.drawString(1*inch, y, str(wastage.wastage_date))
        p.drawString(2.5*inch, y, wastage.product.name)
        p.drawString(5*inch, y, str(wastage.quantity))
        p.drawString(6.5*inch, y, wastage.unit)
        p.drawString(8*inch, y, wastage.reason)
        y -= 0.3*inch
        
        if y < 1*inch:
            p.showPage()
            y = 9*inch
    
    p.showPage()
    p.save()
    
    return response

@login_required
def export_expenses_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="wydatki.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Data', 'Produkt', 'Kwota', 'Status'])
    
    expenses = ShoppingExpense.objects.filter(user=request.user).order_by('-shopping_date')
    for expense in expenses:
        writer.writerow([
            expense.shopping_date.strftime('%d.%m.%Y'),
            expense.product.name,
            f"{expense.amount:.2f}",
            expense.get_status_display()
        ])
    
    return response

@login_required
def export_expenses_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="wydatki.pdf"'
    
    doc = SimpleDocTemplate(response, pagesize=letter)
    elements = []
    
    styles = getSampleStyleSheet()
    title = Paragraph("Raport wydatków", styles['Heading1'])
    elements.append(title)
    
    data = [['Data', 'Produkt', 'Kwota', 'Status']]
    expenses = ShoppingExpense.objects.filter(user=request.user).order_by('-shopping_date')
    for expense in expenses:
        data.append([
            expense.shopping_date.strftime('%d.%m.%Y'),
            expense.product.name,
            f"{expense.amount:.2f} zł",
            expense.get_status_display()
        ])
    
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(table)
    
    doc.build(elements)
    return response
