from rest_framework import serializers
from .models import CustomUser, Organisation
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['userId','first_name', 'last_name', 'email', 'phone', 'password']
        extra_kwargs = {
            'password': {'write_only': True},
            # 'userId': {'read_only': True},  
        }
class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['userId','first_name', 'last_name', 'email', 'phone', 'password']
        extra_kwargs = {
            'password': {'write_only': True},
             'userId': {'read_only': True},  
        }
        
    
    
    def validate(self, attrs):
        # Ensure email uniqueness
        if CustomUser.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError("Email already exists")
        
        
        # Hash the password before saving
        # attrs['password'] = make_password(attrs['password'])
        return attrs
    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user
    def validate_userId(self, value):
        if CustomUser.objects.filter(userId=value).exists():
            raise serializers.ValidationError("User with this userId already exists.")
        return value

    
    
class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['userId', 'email', 'first_name', 'last_name', 'phone']
    

class OrganisationSerializer(serializers.ModelSerializer):
    # users = serializers.SerializerMethodField()
    class Meta:
        model = Organisation
        fields = ['orgId', 'name', 'description']
        
    # def get_users(self, obj):
    #     return [{'userId': user.userId, 'email': user.email} for user in obj.users.all()]
