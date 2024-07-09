from django.shortcuts import render
from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Organisation,CustomUser
from .serializers import UserSerializer, OrganisationSerializer
from rest_framework_simplejwt.tokens import RefreshToken

# Create your views here.

class RegisterView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.save()
                org_name = f"{user.first_name}'s Organisation"
                Organisation.objects.create(name=org_name).users.add(user)

                refresh = RefreshToken.for_user(user)
                user_data = {
                    'userId': serializer.data['userId'],
                    'email': serializer.data['email'],
                    'first_name':serializer.data['first_name'],
                    'last_name':serializer.data['last_name'],
                    'phone':serializer.data['email']
                }
                return Response({
                    'status': 'success',
                    'message': 'Registration successful',
                    'data': {
                        'accessToken': str(refresh.access_token),
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
            refresh = RefreshToken.for_user(user)
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
                    'accessToken': str(refresh.access_token),
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
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'userId'

    def get_queryset(self):
        user = self.request.user
        org_ids = user.organisations.values_list('orgId', flat=True)
        return CustomUser.objects.filter(organisations__orgId__in=org_ids)
    


class OrganisationListView(generics.ListAPIView):
    serializer_class = OrganisationSerializer
    permission_classes = [permissions.IsAuthenticated]
 
    def get_queryset(self):
        user = self.request.user
        return Organisation.objects.filter(users=user)

class OrganisationDetailView(generics.RetrieveAPIView):
    queryset = Organisation.objects.all()
    serializer_class = OrganisationSerializer
    permission_classes = [permissions.IsAuthenticated]

class OrganisationCreateView(generics.CreateAPIView):
    serializer_class = OrganisationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        organisation = serializer.save()
        organisation.users.add(self.request.user)

class AddUserToOrganisationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, org_id):
        user_id = request.data.get('id')
        try:
            user = CustomUser.objects.get(id=user_id)
            organisation = Organisation.objects.get(id=org_id)
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
