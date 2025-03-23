from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from .models import ShoppingList, ShoppingListItem
from .forms import ShoppingListForm, ShoppingListItemForm

class ShoppingListView(LoginRequiredMixin, ListView):
    model = ShoppingList
    template_name = 'shopping_list/shopping_list.html'
    context_object_name = 'shopping_lists'
    
    def get_queryset(self):
        return ShoppingList.objects.filter(user=self.request.user, is_active=True)

class ShoppingListCreateView(LoginRequiredMixin, CreateView):
    model = ShoppingList
    form_class = ShoppingListForm
    template_name = 'shopping_list/shopping_list_form.html'
    success_url = reverse_lazy('shopping_list:list')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Lista zakupów została utworzona pomyślnie!')
        return super().form_valid(form)

class ShoppingListDetailView(LoginRequiredMixin, ListView):
    model = ShoppingListItem
    template_name = 'shopping_list/shopping_list_detail.html'
    context_object_name = 'items'
    
    def get_queryset(self):
        self.shopping_list = get_object_or_404(ShoppingList, pk=self.kwargs['pk'], user=self.request.user)
        return ShoppingListItem.objects.filter(shopping_list=self.shopping_list)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['shopping_list'] = self.shopping_list
        return context

@login_required
def add_item(request, pk):
    shopping_list = get_object_or_404(ShoppingList, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ShoppingListItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.shopping_list = shopping_list
            item.save()
            messages.success(request, 'Produkt został dodany do listy zakupów!')
            return redirect('shopping_list:detail', pk=pk)
    else:
        form = ShoppingListItemForm()
    return render(request, 'shopping_list/add_item.html', {'form': form, 'shopping_list': shopping_list})

@login_required
def toggle_item_status(request, pk, item_pk):
    if request.method == 'POST':
        item = get_object_or_404(ShoppingListItem, pk=item_pk, shopping_list__user=request.user)
        item.is_bought = not item.is_bought
        item.save()
        return JsonResponse({'status': 'success', 'is_bought': item.is_bought})
    return JsonResponse({'status': 'error'}, status=400)

class ShoppingListDeleteView(LoginRequiredMixin, DeleteView):
    model = ShoppingList
    template_name = 'shopping_list/shopping_list_confirm_delete.html'
    success_url = reverse_lazy('shopping_list:list')
    
    def get_queryset(self):
        return ShoppingList.objects.filter(user=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Lista zakupów została usunięta pomyślnie!')
        return super().delete(request, *args, **kwargs)
