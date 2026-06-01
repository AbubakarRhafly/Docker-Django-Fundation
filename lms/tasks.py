from celery import shared_task
from django.utils import timezone

from .models import Course, Enrollment


@shared_task
def send_enrollment_email(enrollment_id):
    enrollment = Enrollment.objects.select_related("student", "course").get(id=enrollment_id)

    message = (
        f"Enrollment email sent to {enrollment.student.email} "
        f"for course {enrollment.course.title}"
    )

    print(message)
    return message


@shared_task
def generate_certificate(enrollment_id):
    enrollment = Enrollment.objects.select_related("student", "course").get(id=enrollment_id)

    certificate_number = f"CERT-{enrollment.id}-{timezone.now().strftime('%Y%m%d%H%M%S')}"

    message = (
        f"Certificate generated for {enrollment.student.username} "
        f"in course {enrollment.course.title}: {certificate_number}"
    )

    print(message)
    return message


@shared_task
def update_course_statistics():
    courses = Course.objects.all()
    result = []

    for course in courses:
        result.append({
            "course_id": course.id,
            "title": course.title,
            "total_students": course.enrollments.count(),
            "total_lessons": course.lessons.count(),
        })

    print("Course statistics updated")
    return result


@shared_task
def export_course_report():
    courses = Course.objects.all()
    report_data = []

    for course in courses:
        report_data.append({
            "course_id": course.id,
            "title": course.title,
            "total_students": course.enrollments.count(),
            "total_lessons": course.lessons.count(),
        })

    print("Course report generated")
    return report_data