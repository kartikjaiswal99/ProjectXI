from djoser.serializers import UserSerializer as BaseUserSerializer
from djoser.serializers import UserCreatePasswordRetypeSerializer


class CustomUserCreateSerializer(UserCreatePasswordRetypeSerializer):
    class Meta(UserCreatePasswordRetypeSerializer.Meta):
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'password']

class UserSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        