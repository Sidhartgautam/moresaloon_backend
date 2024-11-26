import uuid
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser, PermissionsMixin, BaseUserManager

class CustomUserManager(BaseUserManager):

    def create_user(self, email,username, password, **extra_fields):
        if not email:
            raise ValueError(_('The Email must be set'))
        if not username:
            raise ValueError(_('Username must be set'))
        if not password:
            raise ValueError(_('Password must be set'))

        email = self.normalize_email(email)
        user = self.model(email=email,username=username, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email,username, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email,username, password, **extra_fields)

class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=True)
    username = models.CharField(max_length=200,unique=True, null=True)
    phone_number = models.CharField(
        _("Phone Number"),
        max_length=100,
        null=True,
        unique=True,
        help_text = "Phone number of the user"
    )
    is_saloon_user = models.BooleanField(default=False)
   

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    class Meta:
        ordering = ['-date_joined']
        verbose_name_plural="Users"

    def __str__(self):
        return f'{self.username}'
    
    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'
    