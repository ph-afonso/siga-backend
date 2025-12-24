from django.urls import path
from accounts.views import RegisterView, RequestPasswordResetEmail, PasswordResetConfirmView, CustomLoginView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
# Adicione seus imports de JWT se precisar (TokenObtainPairView etc)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Rota 1: Pede o email
    path('password-reset/', RequestPasswordResetEmail.as_view(), name='request-reset'),
    
    # Rota 2: Envia os dados para trocar senha
    path('password-reset-confirm/', PasswordResetConfirmView.as_view(), name='confirm-reset'),
    
    # ... suas outras rotas (register, login) ...
]