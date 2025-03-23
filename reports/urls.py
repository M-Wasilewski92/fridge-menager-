from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('consumption/add/', views.ProductConsumptionCreateView.as_view(), name='add_consumption'),
    path('expense/add/', views.ShoppingExpenseCreateView.as_view(), name='add_expense'),
    path('wastage/add/', views.ProductWastageCreateView.as_view(), name='add_wastage'),
    path('expenses/', views.expense_report, name='expense_report'),
    path('expenses/export/csv/', views.export_expenses_csv, name='export_csv'),
    path('expenses/export/pdf/', views.export_expenses_pdf, name='export_pdf'),
    path('consumption/', views.consumption_report, name='consumption_report'),
    path('wastage/', views.wastage_report, name='wastage_report'),
    # Eksport raportów
    path('export/expenses/<str:format>/', views.export_expense_report, name='export_expense_report'),
    path('export/consumption/<str:format>/', views.export_consumption_report, name='export_consumption_report'),
    path('export/wastage/<str:format>/', views.export_wastage_report, name='export_wastage_report'),
    # API dla wykresów
    path('api/expense-trends/', views.expense_trends_api, name='expense_trends_api'),
    path('api/consumption-trends/', views.consumption_trends_api, name='consumption_trends_api'),
    path('api/wastage-trends/', views.wastage_trends_api, name='wastage_trends_api'),
    # Export endpoints
    path('export/expense/csv/', views.export_expense_csv, name='export_expense_csv'),
    path('export/expense/pdf/', views.export_expense_pdf, name='export_expense_pdf'),
    path('export/consumption/csv/', views.export_consumption_csv, name='export_consumption_csv'),
    path('export/consumption/pdf/', views.export_consumption_pdf, name='export_consumption_pdf'),
    path('export/wastage/csv/', views.export_wastage_csv, name='export_wastage_csv'),
    path('export/wastage/pdf/', views.export_wastage_pdf, name='export_wastage_pdf'),
] 