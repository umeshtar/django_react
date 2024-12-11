from django.contrib import admin
from django.contrib.admin import TabularInline, ModelAdmin
from django.db.models import Case, When, IntegerField
from django.utils import timezone

from app_system.admin import RecurAdmin
from app_task.models import Task, TaskExtension


# Register your models here.
def refresh_task_status(modeladmin, request, queryset):
    current = timezone.now()
    for task in queryset:
        if task.completion_time:
            task.status = 'Completed'
        elif current > task.deadline:
            task.status = 'Overdue'
        elif task.start_time and current > task.start_time:
            task.status = 'Active'
        else:
            task.status = 'Pending'
        task.save()


class ExtensionInline(TabularInline):
    model = TaskExtension
    extra = 1
    fields = ('name', 'past_deadline', 'new_deadline')


@admin.register(Task)
class TaskAdmin(ModelAdmin):
    list_display = ('id', 'name', 'tag', 'status', 'deadline', 'start_time', 'completion_time', 'extensions')
    list_filter = ('status', 'tag', 'deadline')
    exclude = ('status',)
    inlines = [ExtensionInline]
    actions = [refresh_task_status]

    def extensions(self, obj):
        return obj.extensions.count()

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            status_order=Case(
                When(status='Overdue', then=1),
                When(status='Active', then=2),
                When(status='Pending', then=3),
                When(status='Completed', then=4),
                default=1,
                output_field=IntegerField()
            )
        ).order_by('status_order', 'deadline')

