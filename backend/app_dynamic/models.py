from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from app_system.models import RecurField
from backend.settings import mongo_db


# Create your models here.
class DynamicForm(RecurField):
    pass


class DynamicFormField(RecurField):
    field_type_choices = [
        ('text', 'Text'),
        ('textarea', 'Text Area'),
        ('email', 'Email'),
        ('url', 'URL'),
        ('date', 'Date'),
        ('time', 'Time'),
        ('datetime-local', 'Date and Time'),
        ('checkbox', 'Check Box'),
        ('number', 'Number'),
        ('select', 'Select'),
        ('file', 'File'),
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
def dynamic_form_post_save(sender, instance, created, **kwargs):
    """
        Create CRUD Permission Objects
        Create Collection in MongoDB Database
    """
    if created:
        DynamicFormPermission.objects.create(dynamic_form=instance, name=f"View {instance.name}")
        DynamicFormPermission.objects.create(dynamic_form=instance, name=f"Add {instance.name}")
        DynamicFormPermission.objects.create(dynamic_form=instance, name=f"Change {instance.name}")
        DynamicFormPermission.objects.create(dynamic_form=instance, name=f"Delete {instance.name}")
        mongo_db.create_collection(str(instance.pk))


