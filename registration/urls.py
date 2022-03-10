from django.contrib.auth.views import LogoutView
from django.urls import include, path

from . import views

app_name = 'registration'

USER_PATTERNS = [
    path('edit/<int:pk>/', views.UserUpdateView.as_view(), name='edit'),
]

AUTH_PATTERNS = [
    path('login/', views.LoginView.as_view(redirect_authenticated_user=True), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', views.SignUpView.as_view(), name='register'),
    path('activate/<token>/<int:pk>/', views.ActivateAccountView.as_view(), name='activate'),
    path('resend_email/', views.ResendConfirmationEmailView.as_view(), name='resend_email'),
    path('reset_password/', views.ResetPasswordView.as_view(), name='password_reset'),
    path('reset/<uidb64>/<token>/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
]

urlpatterns = [
    path('auth/', include((AUTH_PATTERNS, 'auth'))),
    path('user/', include((USER_PATTERNS, 'user'))),
    path('token/', views.RequestTokenView.as_view(), name='token'),
]
