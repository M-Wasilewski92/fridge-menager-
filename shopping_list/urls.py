from django.urls import path
from . import views

app_name = 'shopping_list'

urlpatterns = [
    path('', views.ShoppingListView.as_view(), name='list'),
    path('create/', views.ShoppingListCreateView.as_view(), name='create'),
    path('<int:pk>/', views.ShoppingListDetailView.as_view(), name='detail'),
    path('<int:pk>/delete/', views.ShoppingListDeleteView.as_view(), name='delete'),
    path('<int:pk>/add-item/', views.add_item, name='add_item'),
    path('<int:pk>/toggle-item/<int:item_pk>/', views.toggle_item_status, name='toggle_item_status'),
] 