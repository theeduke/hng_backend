from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
import uuid
from django.utils.translation import gettext_lazy as _

# Create your models here.
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        
        # Set userId if provided or generate a new one
        user.userId = extra_fields.get('userId', uuid.uuid4())

        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser):
    # id = models.AutoField(primary_key=True)  # AutoField with primary_key=True generates an integer primary key
    userId = models.UUIDField(unique=True, default=uuid.uuid4, editable=False, primary_key=True)
    # userId = models.CharField(unique=True, max_length=255, null=False, primary_key=True)
    email = models.EmailField(unique=True, null=False)
    first_name = models.CharField(max_length=30, null=False)
    last_name = models.CharField(max_length=30, null=False)
    phone = models.CharField(max_length=15, blank=True, null=True)
    password=models.CharField(_('password'), max_length=128)
    
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    

    # objects = UserManager()
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    def __str__(self):
        return self.userId
    class Meta:
        verbose_name = "CustomUser"
        verbose_name_plural = "CustomUsers"
    

class Organisation(models.Model):
    orgId = models.UUIDField(unique=True, default=uuid.uuid4, editable=False, primary_key=True)
    name = models.CharField(max_length=255, null=False)
    description = models.TextField(blank=True, null=True)
    users = models.ManyToManyField(CustomUser, related_name='organisations')

    def __str__(self):
        return self.name
    class Meta:
        verbose_name = "Organisation"
        verbose_name_plural = "Organisations"