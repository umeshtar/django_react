from django.db import models

from app_system.models import RecurField


# Create your models here.
class Task(RecurField):
    tag_choices = [
        ("Meditation", "Meditation"),
        ("Administration", "Administration"),
        ("Social", "Social"),
        ("Tour and Travelling", "Tour and Travelling"),
        ("Career and Work", "Career and Work"),
    ]
    status_choices = [
        ("Pending", "Pending"),
        ("Active", "Active"),
        ("Overdue", "Overdue"),
        ("Completed", "Completed"),
    ]
    tag = models.CharField(max_length=20, choices=tag_choices)
    status = models.CharField(max_length=20, choices=status_choices, default="Pending")
    description = models.TextField()
    deadline = models.DateTimeField()
    start_time = models.DateTimeField(null=True, blank=True)
    completion_time = models.DateTimeField(null=True, blank=True)
    completion_remark = models.TextField(null=True, blank=True)


class TaskExtension(RecurField):
    past_deadline = models.DateTimeField()
    new_deadline = models.DateTimeField()
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="extensions")
