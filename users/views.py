from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import CustomUserCreationForm, CustomUserChangeForm
from django.contrib.auth import get_user_model
from .models import FriendRequest
from django.db import models

User = get_user_model()

# Create your views here.

class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(self.request, 'Konto zostało utworzone pomyślnie!')
        return response

@login_required
def profile_view(request):
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil został zaktualizowany!')
            return redirect('users:profile')
    else:
        form = CustomUserChangeForm(instance=request.user)
    
    return render(request, 'users/profile.html', {'form': form})

@login_required
def friends_view(request):
    user = request.user
    friends = user.friends.all()
    pending_requests = FriendRequest.objects.filter(
        sender=user,
        status='pending'
    ).select_related('receiver')
    received_requests = FriendRequest.objects.filter(
        receiver=user,
        status='pending'
    ).select_related('sender')
    
    return render(request, 'users/friends.html', {
        'friends': friends,
        'pending_requests': pending_requests,
        'received_requests': received_requests
    })

@login_required
def add_friend(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            friend = User.objects.get(email=email)
            if friend == request.user:
                messages.error(request, 'Nie możesz dodać samego siebie jako przyjaciela.')
            elif friend in request.user.friends.all():
                messages.warning(request, 'Ten użytkownik jest już Twoim przyjacielem.')
            else:
                # Sprawdź czy już istnieje zaproszenie
                existing_request = FriendRequest.objects.filter(
                    (models.Q(sender=request.user, receiver=friend) |
                     models.Q(sender=friend, receiver=request.user)),
                    status='pending'
                ).first()
                
                if existing_request:
                    messages.warning(request, 'Zaproszenie do przyjaciół już zostało wysłane.')
                else:
                    FriendRequest.objects.create(
                        sender=request.user,
                        receiver=friend,
                        status='pending'
                    )
                    messages.success(request, f'Wysłano zaproszenie do {friend.username}!')
        except User.DoesNotExist:
            messages.error(request, 'Nie znaleziono użytkownika o podanym adresie email.')
    return redirect('users:friends')

@login_required
def accept_friend_request(request, request_id):
    friend_request = get_object_or_404(FriendRequest, id=request_id, receiver=request.user, status='pending')
    friend_request.status = 'accepted'
    friend_request.save()
    
    # Dodaj użytkowników do przyjaciół
    request.user.friends.add(friend_request.sender)
    friend_request.sender.friends.add(request.user)
    
    messages.success(request, f'Zaakceptowano zaproszenie od {friend_request.sender.username}!')
    return redirect('users:friends')

@login_required
def reject_friend_request(request, request_id):
    friend_request = get_object_or_404(FriendRequest, id=request_id, receiver=request.user, status='pending')
    friend_request.status = 'rejected'
    friend_request.save()
    
    messages.info(request, f'Odrzucono zaproszenie od {friend_request.sender.username}.')
    return redirect('users:friends')

@login_required
def remove_friend(request, friend_id):
    friend = get_object_or_404(User, id=friend_id)
    if friend in request.user.friends.all():
        request.user.friends.remove(friend)
        friend.friends.remove(request.user)
        messages.success(request, f'Usunięto {friend.username} z przyjaciół.')
    return redirect('users:friends')
