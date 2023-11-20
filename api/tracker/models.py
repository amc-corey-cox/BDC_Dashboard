import logging

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from simple_history.models import HistoricalRecords
from allauth.account.signals import user_logged_in, user_logged_out
from django.dispatch import receiver

logger = logging.getLogger("django")


class UserManager(BaseUserManager):
    def _create_user(self, email, password, is_staff, is_superuser, **extra_data):
        if not email:
            raise ValueError("Users must have an email address")

        email = self.normalize_email(email)
        now = timezone.now()
        user = self.model(
            email=email,
            is_staff=is_staff,
            is_active=True,
            is_superuser=is_superuser,
            last_login=now,
            date_joined=now,
            **extra_data
        )
        user.set_password(password)
        user.save(using=self._db)
        logger.info("Created user " + email)
        return user

    def create_user(self, email, password, **extra_data):
        return self._create_user(email, password, False, False, **extra_data)

    def create_superuser(self, email, password, **extra_data):
        user = self._create_user(email, password, True, True, **extra_data)
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(verbose_name="Email", unique=True)
    name = models.CharField(max_length=100, verbose_name="Name")

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    last_login = models.DateTimeField(null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    history = HistoricalRecords()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def get_absolute_url(self):
        return "users/%i" % self.pk
        
    def get_short_name(self):
        return self.name
        

@receiver(user_logged_in)
def login_logger(request, user, **kwargs):
    logger.info("User {} logged in with {}".format(user.email, request))


@receiver(user_logged_out)
def login_logger(request, user, **kwargs):
    logger.info("User {} logged out.".format(user.email))


