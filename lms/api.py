import jwt

from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.utils import timezone
from ninja import NinjaAPI

from .auth import JWTAuth, create_access_token, create_refresh_token
from .models import Category, Course, Enrollment, Lesson, Progress, UserProfile
from .permissions import is_admin, is_instructor, is_student
from .schemas import (
    CourseCreateSchema,
    CourseOutSchema,
    CourseUpdateSchema,
    EnrollmentCreateSchema,
    EnrollmentOutSchema,
    ErrorSchema,
    LoginSchema,
    MessageSchema,
    ProgressCreateSchema,
    RefreshTokenSchema,
    RegisterSchema,
    TokenSchema,
    UserOutSchema,
    UserUpdateSchema,
)


api = NinjaAPI(
    title="Simple LMS API",
    version="1.0.0",
    description="REST API for Simple LMS with JWT Authentication and Role-Based Access Control",
)


def user_to_dict(user):
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.profile.role,
    }


def course_to_dict(course):
    return {
        "id": course.id,
        "title": course.title,
        "description": course.description,
        "instructor_id": course.instructor_id,
        "instructor_username": course.instructor.username,
        "category_id": course.category_id,
        "category_name": course.category.name if course.category else None,
        "total_lessons": getattr(course, "total_lessons", None),
        "total_students": getattr(course, "total_students", None),
    }


def enrollment_to_dict(enrollment):
    return {
        "id": enrollment.id,
        "course_id": enrollment.course_id,
        "course_title": enrollment.course.title,
        "student_id": enrollment.student_id,
        "student_username": enrollment.student.username,
        "status": enrollment.status,
    }


@api.post("/auth/register", response={200: UserOutSchema, 400: ErrorSchema})
def register(request, payload: RegisterSchema):
    allowed_roles = ["admin", "instructor", "student"]

    if payload.role not in allowed_roles:
        return 400, {"message": "Invalid role. Use admin, instructor, or student."}

    if User.objects.filter(username=payload.username).exists():
        return 400, {"message": "Username already exists."}

    if User.objects.filter(email=payload.email).exists():
        return 400, {"message": "Email already exists."}

    user = User.objects.create_user(
        username=payload.username,
        email=payload.email,
        password=payload.password,
    )

    user.profile.role = payload.role
    user.profile.save()

    return user_to_dict(user)


@api.post("/auth/login", response={200: TokenSchema, 401: ErrorSchema})
def login(request, payload: LoginSchema):
    user = authenticate(username=payload.username, password=payload.password)

    if not user:
        return 401, {"message": "Invalid username or password."}

    return {
        "access": create_access_token(user),
        "refresh": create_refresh_token(user),
    }


@api.post("/auth/refresh", response={200: TokenSchema, 401: ErrorSchema})
def refresh_token(request, payload: RefreshTokenSchema):
    try:
        decoded = jwt.decode(payload.refresh, settings.SECRET_KEY, algorithms=["HS256"])

        if decoded.get("type") != "refresh":
            return 401, {"message": "Invalid token type."}

        user = User.objects.get(id=decoded["user_id"])

        return {
            "access": create_access_token(user),
            "refresh": create_refresh_token(user),
        }

    except Exception:
        return 401, {"message": "Invalid refresh token."}


@api.get("/auth/me", auth=JWTAuth(), response=UserOutSchema)
def get_current_user(request):
    return user_to_dict(request.auth)


@api.put("/auth/me", auth=JWTAuth(), response=UserOutSchema)
def update_profile(request, payload: UserUpdateSchema):
    user = request.auth

    if payload.email is not None:
        user.email = payload.email

    if payload.first_name is not None:
        user.first_name = payload.first_name

    if payload.last_name is not None:
        user.last_name = payload.last_name

    user.save()

    return user_to_dict(user)


@api.get("/courses", response=list[CourseOutSchema])
def list_courses(request):
    courses = Course.objects.for_listing().all()
    return [course_to_dict(course) for course in courses]


@api.get("/courses/{course_id}", response={200: CourseOutSchema, 404: ErrorSchema})
def course_detail(request, course_id: int):
    course = get_object_or_404(
        Course.objects.select_related("instructor", "category"),
        id=course_id,
    )

    return course_to_dict(course)


@api.post("/courses", auth=JWTAuth(), response={200: CourseOutSchema, 403: ErrorSchema, 404: ErrorSchema})
def create_course(request, payload: CourseCreateSchema):
    user = request.auth

    if not is_instructor(user):
        return 403, {"message": "Only instructors can create courses."}

    category = None

    if payload.category_id:
        category = get_object_or_404(Category, id=payload.category_id)

    course = Course.objects.create(
        title=payload.title,
        description=payload.description,
        instructor=user,
        category=category,
    )

    course = Course.objects.select_related("instructor", "category").get(id=course.id)

    return course_to_dict(course)


@api.patch("/courses/{course_id}", auth=JWTAuth(), response={200: CourseOutSchema, 403: ErrorSchema, 404: ErrorSchema})
def update_course(request, course_id: int, payload: CourseUpdateSchema):
    user = request.auth
    course = get_object_or_404(
        Course.objects.select_related("instructor", "category"),
        id=course_id,
    )

    if course.instructor_id != user.id:
        return 403, {"message": "Only the course owner can update this course."}

    if payload.title is not None:
        course.title = payload.title

    if payload.description is not None:
        course.description = payload.description

    if payload.category_id is not None:
        course.category = get_object_or_404(Category, id=payload.category_id)

    course.save()

    return course_to_dict(course)


@api.delete("/courses/{course_id}", auth=JWTAuth(), response={200: MessageSchema, 403: ErrorSchema, 404: ErrorSchema})
def delete_course(request, course_id: int):
    user = request.auth

    if not is_admin(user):
        return 403, {"message": "Only admin can delete courses."}

    course = get_object_or_404(Course, id=course_id)
    course.delete()

    return {"message": "Course deleted successfully."}


@api.post("/enrollments", auth=JWTAuth(), response={200: EnrollmentOutSchema, 403: ErrorSchema, 404: ErrorSchema})
def enroll_course(request, payload: EnrollmentCreateSchema):
    user = request.auth

    if not is_student(user):
        return 403, {"message": "Only students can enroll in courses."}

    course = get_object_or_404(Course, id=payload.course_id)

    enrollment, created = Enrollment.objects.get_or_create(
        student=user,
        course=course,
    )

    enrollment = Enrollment.objects.select_related("student", "course").get(id=enrollment.id)

    return enrollment_to_dict(enrollment)


@api.get("/enrollments/my-courses", auth=JWTAuth(), response=list[EnrollmentOutSchema])
def my_courses(request):
    user = request.auth

    enrollments = Enrollment.objects.for_student_dashboard().filter(student=user)

    return [enrollment_to_dict(enrollment) for enrollment in enrollments]


@api.post("/enrollments/{enrollment_id}/progress", auth=JWTAuth(), response={200: MessageSchema, 403: ErrorSchema, 404: ErrorSchema, 400: ErrorSchema})
def mark_lesson_complete(request, enrollment_id: int, payload: ProgressCreateSchema):
    user = request.auth

    if not is_student(user):
        return 403, {"message": "Only students can mark lesson progress."}

    enrollment = get_object_or_404(
        Enrollment.objects.select_related("student", "course"),
        id=enrollment_id,
    )

    if enrollment.student_id != user.id:
        return 403, {"message": "You can only update your own enrollment progress."}

    lesson = get_object_or_404(Lesson, id=payload.lesson_id)

    if lesson.course_id != enrollment.course_id:
        return 400, {"message": "Lesson does not belong to this enrolled course."}

    progress, created = Progress.objects.get_or_create(
        enrollment=enrollment,
        lesson=lesson,
        defaults={
            "completed": True,
            "completed_at": timezone.now(),
        },
    )

    if not created:
        progress.completed = True
        progress.completed_at = timezone.now()
        progress.save()

    return {"message": "Lesson marked as complete."}