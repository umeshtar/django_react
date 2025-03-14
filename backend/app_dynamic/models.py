from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from app_system.models import RecurField


# Create your models here.
class DynamicForm(RecurField):
    pass


class DynamicFormField(RecurField):
    field_type_choices = [
        ('text', 'Text Input'),
    ]
    codename = models.CharField(max_length=100)
    field_type = models.CharField(choices=field_type_choices, max_length=50)
    validation = models.JSONField()  # {'required': False, 'max_length': 100}
    dynamic_form = models.ForeignKey(DynamicForm, on_delete=models.CASCADE, related_name='fields')


class DynamicFormPermission(RecurField):
    dynamic_form = models.ForeignKey(DynamicForm, models.CASCADE, related_name='dynamic_permissions')
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='dynamic_permissions')


class DynamicFormRecord(RecurField):
    name = None
    record = models.JSONField()
    dynamic_form = models.ForeignKey(DynamicForm, on_delete=models.CASCADE, related_name='records')

    def __str__(self):
        return str(self.pk)


# Auto Create Permission for New Form
@receiver(post_save, sender=DynamicForm)
def create_crud_permissions(sender, instance, created, **kwargs):
    if created:
        permissions = ['View', 'Add', 'Change', 'Delete']
        for perm in permissions:
            DynamicFormPermission.objects.create(dynamic_form=instance, name=f"{perm} {instance.name}")
