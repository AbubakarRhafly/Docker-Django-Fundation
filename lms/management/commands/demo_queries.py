from django.core.management.base import BaseCommand
from django.db import connection
from django.test.utils import CaptureQueriesContext

from lms.models import Course, Enrollment


class Command(BaseCommand):
    help = "Compare naive queries vs optimized queries"

    def handle(self, *args, **kwargs):
        self.stdout.write("=== COURSE LIST VIEW ===")

        with CaptureQueriesContext(connection) as ctx:
            for course in Course.objects.all():
                instructor_name = course.instructor.username
                category_name = course.category.name if course.category else "-"
                lessons = [lesson.title for lesson in course.lessons.all()]

                self.stdout.write(
                    f"{course.title} | {instructor_name} | "
                    f"{category_name} | {len(lessons)} lessons"
                )

        self.stdout.write(
            self.style.WARNING(f"Naive query count: {len(ctx)}")
        )

        with CaptureQueriesContext(connection) as ctx:
            for course in Course.objects.for_listing():
                instructor_name = course.instructor.username
                category_name = course.category.name if course.category else "-"
                lessons = [lesson.title for lesson in course.lessons.all()]

                self.stdout.write(
                    f"{course.title} | {instructor_name} | "
                    f"{category_name} | {len(lessons)} lessons"
                )

        self.stdout.write(
            self.style.SUCCESS(f"Optimized query count: {len(ctx)}")
        )

        self.stdout.write("\n=== STUDENT DASHBOARD ===")

        with CaptureQueriesContext(connection) as ctx:
            for enrollment in Enrollment.objects.all():
                student_name = enrollment.student.username
                course_title = enrollment.course.title
                completed = enrollment.progress_records.filter(
                    completed=True
                ).count()
                total = enrollment.course.lessons.count()

                self.stdout.write(
                    f"{student_name} | {course_title} | "
                    f"progress: {completed}/{total}"
                )

        self.stdout.write(
            self.style.WARNING(f"Naive query count: {len(ctx)}")
        )

        with CaptureQueriesContext(connection) as ctx:
            for enrollment in Enrollment.objects.for_student_dashboard():
                student_name = enrollment.student.username
                course_title = enrollment.course.title
                completed = enrollment.completed_lessons
                total = enrollment.total_lessons

                self.stdout.write(
                    f"{student_name} | {course_title} | "
                    f"progress: {completed}/{total}"
                )

        self.stdout.write(
            self.style.SUCCESS(f"Optimized query count: {len(ctx)}")
        )