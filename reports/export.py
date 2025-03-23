import csv
from io import StringIO
from datetime import datetime, timedelta
from django.http import HttpResponse
from django.template.loader import render_to_string
import pdfkit
from .models import ProductConsumption, ShoppingExpense, ProductWastage
from django.db.models import Sum, Avg
import os

def export_to_csv(model, queryset, filename):
    """
    Eksportuje dane do pliku CSV.
    """
    output = StringIO()
    writer = csv.writer(output)
    
    # Dodaj nagłówki
    if model == ProductConsumption:
        writer.writerow(['Data', 'Produkt', 'Kategoria', 'Ilość', 'Jednostka'])
        for item in queryset:
            writer.writerow([
                item.consumption_date.strftime('%Y-%m-%d'),
                item.product.name,
                item.product.category.name,
                item.quantity,
                item.unit
            ])
    elif model == ShoppingExpense:
        writer.writerow(['Data', 'Lista zakupów', 'Kwota'])
        for item in queryset:
            writer.writerow([
                item.shopping_date.strftime('%Y-%m-%d'),
                item.shopping_list.name,
                item.total_amount
            ])
    elif model == ProductWastage:
        writer.writerow(['Data', 'Produkt', 'Kategoria', 'Ilość', 'Jednostka', 'Powód'])
        for item in queryset:
            writer.writerow([
                item.wastage_date.strftime('%Y-%m-%d'),
                item.product.name,
                item.product.category.name,
                item.quantity,
                item.unit,
                item.reason
            ])

    response = HttpResponse(output.getvalue(), content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}_{datetime.now().strftime("%Y%m%d")}.csv"'
    return response

def export_to_pdf(template_name, context, filename):
    """
    Eksportuje dane do pliku PDF.
    """
    html_string = render_to_string(template_name, context)
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}_{datetime.now().strftime("%Y%m%d")}.pdf"'
    
    try:
        # Konfiguracja wkhtmltopdf
        config = pdfkit.configuration(wkhtmltopdf='C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe')
        pdf = pdfkit.from_string(html_string, False, configuration=config)
        response.write(pdf)
        return response
    except Exception as e:
        return HttpResponse(f'Wystąpił błąd podczas generowania PDF: {str(e)}')

def export_expense_report(request, format='csv'):
    """
    Eksportuje raport wydatków.
    """
    thirty_days_ago = datetime.now() - timedelta(days=30)
    expenses = ShoppingExpense.objects.filter(
        user=request.user,
        shopping_date__gte=thirty_days_ago
    ).order_by('-shopping_date')

    if format == 'csv':
        return export_to_csv(ShoppingExpense, expenses, 'raport_wydatkow')
    else:
        context = {
            'expenses': expenses,
            'total_expenses': expenses.aggregate(total=Sum('total_amount'))['total'] or 0,
            'avg_expense': expenses.aggregate(avg=Avg('total_amount'))['avg'] or 0,
            'date': datetime.now().strftime('%Y-%m-%d')
        }
        return export_to_pdf('reports/pdf/expense_report.html', context, 'raport_wydatkow')

def export_consumption_report(request, format='csv'):
    """
    Eksportuje raport zużycia.
    """
    thirty_days_ago = datetime.now() - timedelta(days=30)
    consumptions = ProductConsumption.objects.filter(
        user=request.user,
        consumption_date__gte=thirty_days_ago
    ).order_by('-consumption_date')

    if format == 'csv':
        return export_to_csv(ProductConsumption, consumptions, 'raport_zuzycia')
    else:
        context = {
            'consumptions': consumptions,
            'total_consumption': consumptions.aggregate(total=Sum('quantity'))['total'] or 0,
            'avg_consumption': consumptions.aggregate(avg=Avg('quantity'))['avg'] or 0,
            'date': datetime.now().strftime('%Y-%m-%d')
        }
        return export_to_pdf('reports/pdf/consumption_report.html', context, 'raport_zuzycia')

def export_wastage_report(request, format='csv'):
    """
    Eksportuje raport marnowania.
    """
    thirty_days_ago = datetime.now() - timedelta(days=30)
    wastages = ProductWastage.objects.filter(
        user=request.user,
        wastage_date__gte=thirty_days_ago
    ).order_by('-wastage_date')

    if format == 'csv':
        return export_to_csv(ProductWastage, wastages, 'raport_marnowania')
    else:
        context = {
            'wastages': wastages,
            'total_wastage': wastages.count(),
            'avg_wastage': wastages.aggregate(avg=Avg('quantity'))['avg'] or 0,
            'date': datetime.now().strftime('%Y-%m-%d')
        }
        return export_to_pdf('reports/pdf/wastage_report.html', context, 'raport_marnowania') 