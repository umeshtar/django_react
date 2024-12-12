from datetime import timedelta

from django.contrib import admin
from django.contrib.admin import TabularInline, ModelAdmin, SimpleListFilter
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


class DeadlineFilter(SimpleListFilter):
    title = "Filter by Deadline"
    parameter_name = "deadline"

    def lookups(self, request, model_admin):
        return [
            ("today", "Today"),
            ("tomorrow", "Tomorrow"),
            ("next_3_days", "Next 3 Days"),
            ("next_7_days", "Next 7 Days"),
            ("next_15_days", "Next 15 Days"),
            ("next_30_days", "Next 30 Days"),
            ("this_month", "This Month"),
        ]

    def queryset(self, request, queryset):
        current = timezone.now()
        if self.value() == "today":
            return queryset.filter(deadline=current)
        if self.value() == "tomorrow":
            return queryset.filter(deadline=current + timedelta(days=1))
        if self.value() == 'next_3_days':
            return queryset.filter(deadline__lte=current + timedelta(days=2))
        if self.value() == 'next_7_days':
            return queryset.filter(deadline__lte=current + timedelta(days=6))
        if self.value() == 'next_15_days':
            return queryset.filter(deadline__lte=current + timedelta(days=14))
        if self.value() == 'next_30_days':
            return queryset.filter(deadline__lte=current + timedelta(days=30))
        if self.value() == 'this_month':
            return queryset.filter(deadline__month=current.month)
        return queryset


@admin.register(Task)
class TaskAdmin(ModelAdmin):
    list_display = ('id', 'name', 'tag', 'status', 'deadline', 'start_time', 'completion_time', 'extensions')
    list_filter = ('status', 'tag', DeadlineFilter)
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


