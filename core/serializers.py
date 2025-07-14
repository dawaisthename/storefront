from djoser.serializers import UserCreateSerializer as BaseUserCreatSerializer
class UserCreateSerializer(BaseUserCreatSerializer):
    class Meta(BaseUserCreatSerializer.Meta):
        fields = ['id','username','password','email','first_name','last_name']
