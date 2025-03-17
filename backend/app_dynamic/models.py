from django.conf import settings
from django.db import models
from django.db.models import JSONField
from django.db.models.signals import post_save
from django.dispatch import receiver

from app_system.models import RecurField
from backend.settings import mongo_db


# Create your models here.
class DynamicForm(RecurField):
    validation = JSONField(null=True, blank=True)
    """
    Form Level Validation are specified here
    
    Common Properties: unique_together, compare_values
    """


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
    """
    Properties as per field types
    Common Properties: required, unique, default
    
    text, email, url
    max_length, min_length
    
    number
    max_value, min_value, decimal_places, number_type=int, float, decimal
    
    select
    relation_type=Choices, One To One, One To Many, Many To Many, choices, related_model, related_model_type=SQL, NoSQL, on_delete=cascade, protect
    
    file
    upload_to (file_path), allowed_extensions, file_size
    1. Server, 2. Google Cloud, 3. Google Drive
    
    Default Values if properties does not provided
    required: false
    unique: false
    default: None, False
    max_length: 99999
    min_length: 0
    max_value: 99999
    min_value: -99999
    decimal_places: 2
    number_type: int
    choices: []
    related_model: None,
    related_model_type: None,
    on_delete=protect
    upload_to='/media/common_files/'
    """
    codename = models.CharField(max_length=100)
    field_type = models.CharField(choices=field_type_choices, max_length=50)
    validation = models.JSONField()  # {'required': False, 'max_length': 100}
    dynamic_form = models.ForeignKey(DynamicForm, on_delete=models.CASCADE, related_name='fields')


class DynamicFormPermission(RecurField):
    dynamic_form = models.ForeignKey(DynamicForm, models.CASCADE, related_name='dynamic_permissions')
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='dynamic_permissions')


# Auto Create Permission for New Form
@receiver(post_save, sender=DynamicForm)
def dynamic_form_post_save(sender, instance, created, **kwargs):
    """
        On Create:
            Create CRUD Permission Objects
            Create Collection in MongoDB Database
        On Update(Non-Recommended):
            Update CRUD Permissions Names
            Update Collection name in MongoDB Database
    """
    if created:
        DynamicFormPermission.objects.get_or_create(dynamic_form=instance, name=f"View {instance.name}")
        DynamicFormPermission.objects.get_or_create(dynamic_form=instance, name=f"Add {instance.name}")
        DynamicFormPermission.objects.get_or_create(dynamic_form=instance, name=f"Change {instance.name}")
        DynamicFormPermission.objects.get_or_create(dynamic_form=instance, name=f"Delete {instance.name}")
        if str(instance.pk) not in mongo_db.list_collection_names():
            mongo_db.create_collection(str(instance.pk))
    else:
        """ Need to Discuss """
