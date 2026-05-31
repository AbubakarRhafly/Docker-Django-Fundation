from ninja import Schema
from typing import Optional


class ErrorSchema(Schema):
    message: str


class RegisterSchema(Schema):
    username: str
    email: str
    password: str
    role: str = "student"


class LoginSchema(Schema):
    username: str
    password: str


class RefreshTokenSchema(Schema):
    refresh: str


class TokenSchema(Schema):
    access: str
    refresh: str


class UserOutSchema(Schema):
    id: int
    username: str
    email: str
    role: str


class UserUpdateSchema(Schema):
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class CourseCreateSchema(Schema):
    title: str
    description: Optional[str] = ""
    category_id: Optional[int] = None


class CourseUpdateSchema(Schema):
    title: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None


class CourseOutSchema(Schema):
    id: int
    title: str
    description: str
    instructor_id: int
    instructor_username: str
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    total_lessons: Optional[int] = None
    total_students: Optional[int] = None


class EnrollmentCreateSchema(Schema):
    course_id: int


class EnrollmentOutSchema(Schema):
    id: int
    course_id: int
    course_title: str
    student_id: int
    student_username: str
    status: str


class ProgressCreateSchema(Schema):
    lesson_id: int


class MessageSchema(Schema):
    message: str