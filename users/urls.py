from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('profile/', views.profile_view, name='profile'),
    path('friends/', views.friends_view, name='friends'),
    path('add-friend/', views.add_friend, name='add_friend'),
    path('accept-friend-request/<int:request_id>/', views.accept_friend_request, name='accept_friend_request'),
    path('reject-friend-request/<int:request_id>/', views.reject_friend_request, name='reject_friend_request'),
    path('remove-friend/<int:friend_id>/', views.remove_friend, name='remove_friend'),
] 