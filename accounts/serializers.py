from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import PermissionDenied

# Serializer para o Registro (opcional, mas bom manter)
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    # Forçamos o email a ser obrigatório na definição do campo
    email = serializers.EmailField(required=True) 

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')

    # --- ADICIONE ESTE MÉTODO ---
    def validate_email(self, value):
        # Normaliza para letras minúsculas para evitar 'Email@teste' e 'email@teste' duplicados
        lower_email = value.lower()
        
        # Verifica se já existe no banco
        if User.objects.filter(email=lower_email).exists():
            raise serializers.ValidationError("Este endereço de email já está cadastrado.")
        
        return lower_email
    # ----------------------------

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'], # Agora usamos o email validado
            password=validated_data['password'],
            is_active=False
        )
        return user

# Serializer 1: Solicitar Reset (Valida email)
class ResetPasswordEmailRequestSerializer(serializers.Serializer):
    # Valida apenas sintaxe (se tem @, ponto, etc)
    # Se falhar aqui, aí sim queremos 400 (Bad Request - Formato inválido)
    email = serializers.EmailField(min_length=2)

    class Meta:
        fields = ['email']

# Serializer 2: Confirmar Reset (Valida UID, Token e Senha)
class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, min_length=6)
    token = serializers.CharField(write_only=True)
    uidb64 = serializers.CharField(write_only=True)

    class Meta:
        fields = ['password', 'token', 'uidb64']

    def validate(self, attrs):
        try:
            uidb64 = attrs.get('uidb64')
            token = attrs.get('token')
            
            # Decodifica o UID para achar o User ID real
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
            
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError("O UID fornecido é inválido ou o usuário não existe.")

        # Verifica se o Token bate com o User
        if not PasswordResetTokenGenerator().check_token(user, token):
            raise serializers.ValidationError("O Token é inválido ou expirou.")

        attrs['user'] = user
        return attrs

    def save(self):
        user = self.validated_data['user']
        password = self.validated_data['password']
        
        user.set_password(password)
        user.save()
        
        return user

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        # Captura os dados
        username = attrs.get("username") # ou "email", dependendo de como você configura
        password = attrs.get("password")

        if username and password:
            # Tenta achar o usuário (ajuste para email=username se necessário)
            user = User.objects.filter(username=username).first()

            if user:
                # 1. Verifica a senha manualmente
                if user.check_password(password):
                    # 2. Se a senha está certa, mas não está ativo:
                    if not user.is_active:
                        # Retorna STATUS 403 com um JSON personalizado
                        raise PermissionDenied({
                            "code": "account_pending", 
                            "detail": "Sua conta foi criada, mas aguarda liberação do administrador."
                        })
        
        # Se passou pelos ifs acima (usuário ativo e senha certa), o método pai gera o token
        return super().validate(attrs)