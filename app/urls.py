from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),

    # --- ROTAS DO SWAGGER ---
    # 1. O arquivo YAML/JSON bruto (o "coração" da documentação)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),

    # 2. A interface visual do Swagger UI (a que você quer)
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # 3. (Opcional) Interface Redoc (outra alternativa visual bonita)
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]