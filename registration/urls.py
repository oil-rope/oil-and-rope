from django.contrib.auth.views import LogoutView
from django.urls import include, path
from rest_framework import routers

from . import views, viewsets

router = routers.DefaultRouter()
router.register(r'user', viewsets.UserViewSet)
router.register(r'profile', viewsets.ProfileViewSet)

app_name = 'registration'

urlpatterns = [
    path('api/', include((router.urls, 'api'))),
    path('login/', views.LoginView.as_view(redirect_authenticated_user=True), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', views.SignUpView.as_view(), name='register'),
    path('activate/<token>/<int:pk>/', views.ActivateAccountView.as_view(), name='activate'),
    path('resend_email/', views.ResendConfirmationEmailView.as_view(), name='resend_email'),
    path('reset_password/', views.ResetPasswordView.as_view(), name='password_reset'),
    path('reset/<uidb64>/<token>/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm')
]
