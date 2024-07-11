from django.shortcuts import render
from rest_framework import status, generics, permissions
from userorganization.permissions import IsMemberOfOrganisation
from rest_framework.response import Response
from rest_framework.views import APIView
from userorganization.models import Organisation,CustomUser
from userorganization.serializers import UserSerializer, OrganisationSerializer, RegisterSerializer, UserDetailSerializer
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken, TokenError
from rest_framework import viewsets
from userorganization.token_utils import generate_access_token, decode_access_token
# Create your views here.

class RegisterView(APIView):
    
    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.save()
                org_name = f"{user.first_name}'s Organisation"
                Organisation.objects.create(name=org_name).users.add(user)

                # refresh = RefreshToken.for_user(user)
                access_token = generate_access_token(user)
                user_data = {
                    # 'userId': serializer.data['userId'],
                    'userId': str(user.userId),
                    'email': serializer.data['email'],
                    'first_name':serializer.data['first_name'],
                    'last_name':serializer.data['last_name'],
                    'phone':serializer.data['email']
                }
                return Response({
                    'status': 'success',
                    'message': 'Registration successful',
                    'data': {
                        # 'accessToken': str(refresh.access_token),
                        'accessToken': access_token,
                        'user': user_data
                    }
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({
                    'status': 'Bad request',
                    'message': 'Registration unsuccessful',
                    'statusCode': 400
                }, status=status.HTTP_400_BAD_REQUEST)

        validation_errors = [{'field': key, 'message': value[0]} for key, value in serializer.errors.items()]
        return Response({
            'errors': validation_errors
        }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        
    

class LoginView(APIView):
        
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        user = CustomUser.objects.filter(email=email).first()

        if user and user.check_password(password):
            access_token = generate_access_token(user)
            # refresh = RefreshToken.for_user(user)
            user_data = {
                'userId': str(user.userId),  
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'phone': user.phone
                }
            return Response({
                'status': 'success',
                'message': 'Login successful',
                'data': {
                    # 'accessToken': str(refresh.access_token),
                    'accessToken': access_token,
                    'user': user_data
                }
            }, status=status.HTTP_200_OK)
        return Response({
            'status': 'Bad request',
            'message': 'Authentication failed',
            'statusCode': 401
        }, status=status.HTTP_401_UNAUTHORIZED)

class UserDetailView(generics.RetrieveAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserDetailSerializer
    permission_classes = [permissions.IsAuthenticated, IsMemberOfOrganisation]
    lookup_field = 'userId'
    
    def get_queryset(self):
        # Ensure we only allow access to the logged-in user's details
        user = self.request.user
        return CustomUser.objects.filter(userId=user.userId)

    

class OrganisationDetailView(generics.RetrieveAPIView):
    queryset = Organisation.objects.all()
    serializer_class = OrganisationSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'orgId'

# class OrganisationCreateView(generics.CreateAPIView):
class OrganisationCreateView(APIView):
    serializer_class = OrganisationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        user = request.user
        queryset = Organisation.objects.filter(users=user)
        serializer = self.serializer_class(queryset, many=True)
        return Response({
            'status': 'success',
            'message': 'Organisation details',
            'data': {
                'organisations': serializer.data
            }
        }, status=status.HTTP_200_OK)
    
    def post(self, request, *args, **kwargs):
        # serializer = self.get_serializer(data=request.data)
        serializer = self.serializer_class(data=request.data)
        # if serializer.is_valid(raise_exception=True):
        if serializer.is_valid():
            try:
                organisation = serializer.save()
                organisation.users.add(request.user)
                return Response({
                    'status': 'success',
                    'message': 'Organisation created successfully',
                    'data': {
                        'organisation': serializer.data
                    }
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({
                    'status': 'Bad Request',
                    'message': 'Client error',
                    'statusCode': 400
                }, status=status.HTTP_400_BAD_REQUEST)
        return Response({
            'status': 'Bad Request',
            'message': 'Client error',
            'statusCode': 400
        }, status=status.HTTP_400_BAD_REQUEST)
            

class AddUserToOrganisationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, orgId):
        user_id = request.data.get('userId')
        try:
            user = CustomUser.objects.get(userId=user_id)
            organisation = Organisation.objects.get(orgId=orgId)
            organisation.users.add(user)
            return Response({
                'status': 'success',
                'message': 'User added to organisation successfully',
            }, status=status.HTTP_200_OK)
        except (CustomUser.DoesNotExist, Organisation.DoesNotExist):
            return Response({
                'status': 'Bad Request',
                'message': 'Client error',
                'statusCode': 400
            }, status=status.HTTP_400_BAD_REQUEST)
