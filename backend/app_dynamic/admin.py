from django.contrib import admin
from django.shortcuts import render
from django.urls import path

from app_dynamic.models import DynamicForm, DynamicFormField, DynamicFormPermission
from app_system.admin import RecurAdmin
from backend.settings import mongo_db


# Register your models here.
@admin.register(DynamicForm)
class DynamicFormAdmin(RecurAdmin):
    list_display = ['name']


@admin.register(DynamicFormField)
class DynamicFormFieldAdmin(RecurAdmin):
    list_display = ['name', 'dynamic_form']


@admin.register(DynamicFormPermission)
class DynamicFormPermissionAdmin(RecurAdmin):
    list_display = ['name', 'dynamic_form']

