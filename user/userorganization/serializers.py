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
    
    def validate(self, attrs):
        # Ensure email uniqueness
        if CustomUser.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError("Email already exists")
        
        # Hash the password before saving
        attrs['password'] = make_password(attrs['password'])
        return attrs
    
    # def create(self, validated_data):
    #     validated_data['password'] = make_password(validated_data['password'])
    #     user = User.objects.create(**validated_data)
    #     return user
    
    # def create(self, validated_data):
    #     validated_data['password'] = make_password(validated_data['password'])
    #     user = User.objects.create(**validated_data)
    #     return user
    
    # def create(self, validated_data):
    #     user = User(
    #         # userId=validated_data['userId'],
    #         first_name=validated_data['first_name'], 
    #         last_name=validated_data['last_name'],
    #         email=validated_data['email']  
    #     )
    #     # user.set_password(validated_data['password'])
    #     validated_data['password']= make_password(validated_data['password'])
    #     user.save()
    #     return user

    # def create(self, validated_data):
    #     validated_data['password'] = make_password(validated_data['password'])
    #     return super().create(validated_data)
    

class OrganisationSerializer(serializers.ModelSerializer):
    # users = serializers.SerializerMethodField()
    class Meta:
        model = Organisation
        fields = ['orgId', 'name', 'description']
        
    # def get_users(self, obj):
    #     return [{'userId': user.userId, 'email': user.email} for user in obj.users.all()]
