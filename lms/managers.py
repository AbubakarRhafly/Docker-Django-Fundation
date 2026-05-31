from django.db import models
from django.db.models import Count, Q


class CourseQuerySet(models.QuerySet):
    def for_listing(self):
        return (
            self.select_related(
                "instructor",
                "instructor__profile",
                "category",
                "category__parent",
            )
            .prefetch_related("lessons")
            .annotate(
                total_lessons=Count("lessons", distinct=True),
                total_students=Count("enrollments", distinct=True),
            )
        )


class EnrollmentQuerySet(models.QuerySet):
    def for_student_dashboard(self):
        return (
            self.select_related(
                "student",
                "student__profile",
                "course",
                "course__instructor",
                "course__instructor__profile",
                "course__category",
            )
            .prefetch_related("progress_records__lesson")
            .annotate(
                total_lessons=Count("course__lessons", distinct=True),
                completed_lessons=Count(
                    "progress_records",
                    filter=Q(progress_records__completed=True),
                    distinct=True,
                ),
            )
        )


class CourseManager(models.Manager.from_queryset(CourseQuerySet)):
    pass


class EnrollmentManager(models.Manager.from_queryset(EnrollmentQuerySet)):
    pass