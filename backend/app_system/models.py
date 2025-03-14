import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your managers here.
class RecurManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_del=False)


class AdminManager(models.Manager):
    pass


# Recur Model
class RecurField(models.Model):
    objects = RecurManager()
    admin_objects = AdminManager()
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    add_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(app_label)s%(class)s_add",
    )
    modify_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(app_label)s%(class)s_change",
    )
    delete_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(app_label)s%(class)s_delete",
    )
    add_date = models.DateTimeField(auto_now_add=True)
    modify_date = models.DateTimeField(auto_now=True)
    delete_date = models.DateTimeField(null=True, blank=True)
    is_del = models.BooleanField(default=False)
    name = models.CharField(max_length=100)

    class Meta:
        abstract = True
        ordering = ["add_date"]

    def __str__(self):
        return self.name


# User Model
class CustomUser(AbstractUser):
    pass

    @property
    def full_name(self):
        return self.get_full_name() if self.first_name and self.last_name else self.get_username()

    def __str__(self):
        return self.full_name

    def has_model_perms(self, model, *perms, key="all"):
        if self.is_active and self.is_superuser:
            return True

        if not perms:
            perms = ("view", "add", "change", "delete")

        app_label = model._meta.app_label
        model_name = model._meta.model_name
        perm_code = f"{app_label}.{{perm}}_{model_name}"

        func = any if key == "any" else all
        return func([self.has_perm(perm_code.format(perm=perm)) for perm in perms])

    def has_dynamic_perms(self, dynamic_form, *perms, key='all'):
        if self.is_active and self.is_superuser:
            return True

        if not perms:
            perms = ("View", "Add", "Change", "Delete")

        perm_code = f"{{perm}} {dynamic_form.name}"

        func = any if key == "any" else all
        queryset = getattr(self, 'dynamic_permissions', None)
        if queryset:
            dynamic_permissions = queryset.filter(dynamic_form=dynamic_form).values_list('name', flat=True)
            return func([perm_code.format(perm=perm) in dynamic_permissions for perm in perms])
        return False


class SystemConfiguration(RecurField):
    pass
