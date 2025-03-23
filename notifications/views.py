from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.http import JsonResponse
from .models import Notification
from .services import generate_all_notifications

class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = 'notifications/notification_list.html'
    context_object_name = 'notifications'
    paginate_by = 10
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['unread_count'] = self.get_queryset().filter(read=False).count()
        return context

@login_required
def mark_notification_read(request, pk):
    """Oznacza powiadomienie jako przeczytane."""
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.mark_as_read()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
    return redirect('notifications:list')

@login_required
def mark_all_read(request):
    """Oznacza wszystkie powiadomienia jako przeczytane."""
    Notification.objects.filter(user=request.user, read=False).update(read=True)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
    return redirect('notifications:list')

@login_required
def get_unread_count(request):
    """Zwraca liczbę nieprzeczytanych powiadomień."""
    count = Notification.objects.filter(user=request.user, read=False).count()
    return JsonResponse({'count': count})

@login_required
def refresh_notifications(request):
    """Odświeża powiadomienia dla użytkownika."""
    generate_all_notifications(request.user)
    return redirect('notifications:list') 