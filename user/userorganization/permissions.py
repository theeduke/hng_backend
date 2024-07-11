from rest_framework import permissions

class IsMemberOfOrganisation(permissions.BasePermission):
    """
    Custom permission to only allow members of an organisation to access its details.
    """
    def has_permission(self, request, view):
        # Example logic: Allow GET requests to all users, but restrict POST to authenticated users
        if request.method == 'GET':
            return True  # Allow any GET request
        elif request.method == 'POST' and request.user.is_authenticated:
            return True  # Allow POST requests if the user is authenticated
        return False  # Default to deny permission for other methods or unauthenticated users

    
    def has_object_permission(self, request, view, obj):
        # Check if the user making the request is a member of the organisation
        user = request.user
        return user in obj.users.all()
    
    