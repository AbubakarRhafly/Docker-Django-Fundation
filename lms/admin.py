from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.contrib.admin.sites import NotRegistered

from .models import UserProfile, Category, Course, Lesson, Enrollment, Progress


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    extra = 0


try:
    admin.site.unregister(User)
except NotRegistered:
    pass


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = [UserProfileInline]
    list_display = (
        "username",
        "email",
        "get_role",
        "is_staff",
        "is_active",
    )
    list_filter = (
        "profile__role",
        "is_staff",
        "is_active",
    )
    search_fields = (
        "username",
        "email",
    )

    def get_role(self, obj):
        try:
            return obj.profile.role
        except UserProfile.DoesNotExist:
            return "-"
    get_role.short_description = "Role"


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role")
    search_fields = ("user__username", "user__email")
    list_filter = ("role",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "parent")
    search_fields = ("name",)
    list_filter = ("parent",)


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "instructor",
        "category",
        "created_at",
    )
    search_fields = (
        "title",
        "description",
        "instructor__username",
        "category__name",
    )
    list_filter = (
        "category",
        "instructor",
    )
    inlines = [LessonInline]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            "instructor",
            "category"
        )


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "course",
        "order",
    )
    search_fields = (
        "title",
        "course__title",
    )
    list_filter = (
        "course",
    )


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = (
        "student",
        "course",
        "status",
        "enrolled_at",
    )
    search_fields = (
        "student__username",
        "course__title",
    )
    list_filter = (
        "status",
        "course",
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            "student",
            "course"
        )


@admin.register(Progress)
class ProgressAdmin(admin.ModelAdmin):
    list_display = (
        "enrollment",
        "lesson",
        "completed",
        "completed_at",
    )
    search_fields = (
        "enrollment__student__username",
        "lesson__title",
        "enrollment__course__title",
    )
    list_filter = (
        "completed",
        "lesson__course",
    )