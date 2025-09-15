from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('', views.UserListCreateView.as_view(), name='user-list-create'),
    path('<str:employee_id>/', views.UserDetailView.as_view(), name='user-detail'),
    path('auth/login/', views.login_view, name='login'),
    path('auth/logout/', views.logout_view, name='logout'),
    path('profile/', views.user_profile, name='user-profile'),
    path('profile/update/', views.update_profile, name='update-profile'),
]
