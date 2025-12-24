from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer, ResetPasswordEmailRequestSerializer, UserSerializer, SetNewPasswordSerializer
from .utils import Util
import os
from django.conf import settings

# View de Registro (mantida para contexto)
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({'message': 'Usuário criado com sucesso'}, status=status.HTTP_201_CREATED)

# View 1: Recebe email -> Gera UID/Token -> Envia Email
class RequestPasswordResetEmail(generics.GenericAPIView):
    serializer_class = ResetPasswordEmailRequestSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        user = User.objects.filter(email=email).first()

        # Validações de erro (404 e 403)
        if not user:
            return Response({'detail': 'E-mail não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        if not user.is_active:
            return Response({'detail': 'Conta inativa.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            # 1. Preparar dados
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            token = PasswordResetTokenGenerator().make_token(user)
            smart_code = f"{uidb64}-{token}"
            
            context = {'username': user.username, 'code': smart_code}

            # 2. Renderizar HTML e Texto
            html_content = render_to_string('emails/request_password_reset_email.html', context)
            text_content = strip_tags(html_content)
            
            # 3. Carregar a Logo (Lê o arquivo para enviar ao Utils)
            image_path = os.path.join(settings.BASE_DIR, 'accounts/templates/assets/logo.png')
            logo_data = None
            
            if os.path.exists(image_path):
                with open(image_path, 'rb') as f:
                    logo_data = f.read()

            # 4. Montar Payload para o Util
            data = {
                'email_body': text_content, 
                'email_html': html_content,
                'to_email': user.email, 
                'email_subject': 'Recuperação de Senha - SIGA',
                # Aqui passamos a imagem para o Util processar
                'email_images': {'logo': logo_data} if logo_data else {}
            }
            
            Util.send_email(data)
            
            return Response({'success': 'Código enviado com sucesso.'}, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"Erro: {e}")
            return Response({'detail': 'Erro interno.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# View 2: Recebe UID, Token e Senha -> Altera Senha
class PasswordResetConfirmView(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer
    permission_classes = [AllowAny]

    # MUDOU DE patch PARA post
    def post(self, request, *args, **kwargs): 
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"message": "Senha redefinida com sucesso!"},
            status=status.HTTP_200_OK
        )

class CustomLoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer