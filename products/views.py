from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Product, Category
from .forms import ProductForm, CategoryForm

class ProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 10
    
    def get_queryset(self):
        return Product.objects.filter(user=self.request.user, is_active=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context

class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/product_form.html'
    success_url = reverse_lazy('products:list')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Produkt został dodany pomyślnie!')
        return super().form_valid(form)

class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/product_form.html'
    success_url = reverse_lazy('products:list')
    
    def get_queryset(self):
        return Product.objects.filter(user=self.request.user)
    
    def form_valid(self, form):
        messages.success(self.request, 'Produkt został zaktualizowany pomyślnie!')
        return super().form_valid(form)

class ProductDeleteView(LoginRequiredMixin, DeleteView):
    model = Product
    template_name = 'products/product_confirm_delete.html'
    success_url = reverse_lazy('products:list')
    
    def get_queryset(self):
        return Product.objects.filter(user=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Produkt został usunięty pomyślnie!')
        return super().delete(request, *args, **kwargs)

@login_required
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk, user=request.user)
    return render(request, 'products/product_detail.html', {'product': product})

class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = 'products/category_list.html'
    context_object_name = 'categories'

class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'products/category_form.html'
    success_url = reverse_lazy('products:category_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Kategoria została dodana.')
        return super().form_valid(form)

class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'products/category_form.html'
    success_url = reverse_lazy('products:category_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Kategoria została zaktualizowana.')
        return super().form_valid(form)

class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    model = Category
    template_name = 'products/category_confirm_delete.html'
    success_url = reverse_lazy('products:category_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Kategoria została usunięta.')
        return super().delete(request, *args, **kwargs)
