from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.academics.models import (
    ClassGroup,
    Course,
    Enrollment,
    FacultyProfile,
    StudentProfile,
    Subject,
    TeacherSubjectAssignment,
)
from apps.attendance.models import AttendanceRecord, AttendanceSession, Notice
from apps.core.models import AcademicYear, Department, Semester, SystemSetting
from apps.exams.models import Exam, ExamSchedule, GradeScale, MarksRecord, PromotionRecord, Result
from apps.fees.models import FeeCategory, FeeStructure, Invoice, Payment


class Command(BaseCommand):
    help = "Create demo data for the first SCMS login."

    def handle(self, *args, **options):
        User = get_user_model()

        cs_department, _ = Department.objects.get_or_create(
            code="CS",
            defaults={
                "name": "Computer Science",
                "description": "Department of Computer Science",
            },
        )

        academic_year, _ = AcademicYear.objects.get_or_create(
            name="2026",
            defaults={
                "start_date": date(2026, 1, 1),
                "end_date": date(2026, 12, 31),
                "is_active": True,
            },
        )

        semester, _ = Semester.objects.get_or_create(
            academic_year=academic_year,
            number=1,
            defaults={
                "name": "Semester 1",
                "start_date": date(2026, 1, 1),
                "end_date": date(2026, 6, 30),
            },
        )
        next_semester, _ = Semester.objects.get_or_create(
            academic_year=academic_year,
            number=2,
            defaults={
                "name": "Semester 2",
                "start_date": date(2026, 7, 1),
                "end_date": date(2026, 12, 31),
            },
        )

        defaults = [
            ("college_name", "Govt. Degree College Kakki Bannu", "Shown in reports and dashboards."),
            ("system_name", "Smart College Management System", "Application display name."),
        ]
        for key, value, description in defaults:
            SystemSetting.objects.get_or_create(
                key=key,
                defaults={"value": value, "description": description},
            )

        demo_users = [
            {
                "username": "admin",
                "password": "Admin@12345",
                "role": User.Roles.ADMIN,
                "first_name": "Demo",
                "last_name": "Admin",
                "email": "admin@example.com",
                "is_staff": True,
                "is_superuser": True,
            },
            {
                "username": "teacher",
                "password": "Teacher@12345",
                "role": User.Roles.TEACHER,
                "first_name": "Demo",
                "last_name": "Teacher",
                "email": "teacher@example.com",
            },
            {
                "username": "student",
                "password": "Student@12345",
                "role": User.Roles.STUDENT,
                "first_name": "Demo",
                "last_name": "Student",
                "email": "student@example.com",
            },
        ]

        for data in demo_users:
            password = data.pop("password")
            user, created = User.objects.get_or_create(username=data["username"], defaults=data)
            if created:
                user.set_password(password)
                user.save()
                user.profile.department = cs_department
                user.profile.save(update_fields=["department"])
                self.stdout.write(self.style.SUCCESS(f"Created demo user: {user.username}"))
            else:
                self.stdout.write(f"Demo user already exists: {user.username}")

        admin_user = User.objects.get(username="admin")
        teacher_user = User.objects.get(username="teacher")
        student_user = User.objects.get(username="student")

        course, _ = Course.objects.get_or_create(
            code="BSCS",
            defaults={
                "name": "Bachelor of Science in Computer Science",
                "department": cs_department,
                "duration_semesters": 8,
                "description": "Core computer science degree program.",
            },
        )

        programming, _ = Subject.objects.get_or_create(
            code="CS101",
            defaults={
                "course": course,
                "name": "Introduction to Programming",
                "credit_hours": 3,
                "semester_number": 1,
            },
        )
        computing, _ = Subject.objects.get_or_create(
            code="CS102",
            defaults={
                "course": course,
                "name": "Fundamentals of Computing",
                "credit_hours": 3,
                "semester_number": 1,
            },
        )

        class_group, _ = ClassGroup.objects.get_or_create(
            course=course,
            academic_year=academic_year,
            semester=semester,
            section="A",
            defaults={"name": "BSCS Semester 1"},
        )

        faculty_profile, _ = FacultyProfile.objects.get_or_create(
            employee_no="EMP-001",
            defaults={
                "user": teacher_user,
                "full_name": teacher_user.get_full_name() or "Demo Teacher",
                "department": cs_department,
                "designation": "Lecturer",
                "qualification": "MS Computer Science",
                "joining_date": date(2026, 1, 1),
                "phone": teacher_user.phone,
            },
        )
        if faculty_profile.user_id != teacher_user.id:
            faculty_profile.user = teacher_user
            faculty_profile.save(update_fields=["user"])

        student_profile, _ = StudentProfile.objects.get_or_create(
            registration_no="2026-BSCS-001",
            defaults={
                "user": student_user,
                "roll_no": "BSCS-001",
                "full_name": student_user.get_full_name() or "Demo Student",
                "father_name": "Demo Guardian",
                "department": cs_department,
                "course": course,
                "current_class": class_group,
                "admission_date": date(2026, 1, 5),
                "phone": student_user.phone,
            },
        )
        if student_profile.user_id != student_user.id or student_profile.current_class_id != class_group.id:
            student_profile.user = student_user
            student_profile.current_class = class_group
            student_profile.save(update_fields=["user", "current_class"])

        for subject in (programming, computing):
            Enrollment.objects.get_or_create(
                student=student_profile,
                subject=subject,
                academic_year=academic_year,
                semester=semester,
                defaults={"class_group": class_group},
            )

        assignment, _ = TeacherSubjectAssignment.objects.get_or_create(
            teacher=faculty_profile,
            subject=programming,
            class_group=class_group,
            academic_year=academic_year,
            semester=semester,
            defaults={"workload_hours": 3},
        )

        attendance_session, _ = AttendanceSession.objects.get_or_create(
            assignment=assignment,
            date=date(2026, 1, 10),
            defaults={
                "topic": "Introduction to course outline",
                "status": AttendanceSession.Status.SUBMITTED,
                "created_by": teacher_user,
            },
        )
        AttendanceRecord.objects.get_or_create(
            session=attendance_session,
            student=student_profile,
            defaults={"status": AttendanceRecord.Status.PRESENT},
        )

        Notice.objects.get_or_create(
            title="Welcome to Smart College Management System",
            defaults={
                "body": "The SCMS demo environment is ready. Admins can manage academic records, teachers can mark attendance, and students can view notices and attendance.",
                "audience": Notice.Audience.ALL,
                "created_by": admin_user,
            },
        )
        Notice.objects.get_or_create(
            title="Teachers can now mark attendance",
            defaults={
                "body": "Use the Attendance menu to create a session and submit daily student attendance.",
                "audience": Notice.Audience.TEACHERS,
                "created_by": admin_user,
            },
        )

        grade_defaults = [
            ("A", Decimal("80.00"), Decimal("100.00"), Decimal("4.00"), "Excellent"),
            ("B", Decimal("70.00"), Decimal("79.99"), Decimal("3.00"), "Very good"),
            ("C", Decimal("60.00"), Decimal("69.99"), Decimal("2.00"), "Good"),
            ("D", Decimal("50.00"), Decimal("59.99"), Decimal("1.00"), "Pass"),
            ("F", Decimal("0.00"), Decimal("49.99"), Decimal("0.00"), "Fail"),
        ]
        for name, min_percentage, max_percentage, grade_point, remarks in grade_defaults:
            GradeScale.objects.get_or_create(
                name=name,
                defaults={
                    "min_percentage": min_percentage,
                    "max_percentage": max_percentage,
                    "grade_point": grade_point,
                    "remarks": remarks,
                },
            )

        midterm_exam, _ = Exam.objects.get_or_create(
            name="Mid Term",
            academic_year=academic_year,
            semester=semester,
            defaults={
                "start_date": date(2026, 3, 10),
                "end_date": date(2026, 3, 15),
                "status": Exam.Status.PUBLISHED,
                "published_at": timezone.now(),
            },
        )
        if midterm_exam.status != Exam.Status.PUBLISHED:
            midterm_exam.status = Exam.Status.PUBLISHED
            midterm_exam.published_at = timezone.now()
            midterm_exam.save(update_fields=["status", "published_at", "updated_at"])
        exam_schedule, _ = ExamSchedule.objects.get_or_create(
            exam=midterm_exam,
            assignment=assignment,
            defaults={
                "exam_date": date(2026, 3, 10),
                "max_marks": Decimal("100.00"),
                "pass_marks": Decimal("40.00"),
            },
        )
        MarksRecord.objects.update_or_create(
            schedule=exam_schedule,
            student=student_profile,
            defaults={
                "obtained_marks": Decimal("86.00"),
                "remarks": "Strong performance",
                "entered_by": teacher_user,
            },
        )
        result, _ = Result.objects.update_or_create(
            exam=midterm_exam,
            student=student_profile,
            defaults={
                "total_marks": Decimal("100.00"),
                "obtained_marks": Decimal("86.00"),
                "percentage": Decimal("86.00"),
                "grade": "A",
                "status": Result.Status.PASS,
                "published_at": timezone.now(),
            },
        )
        PromotionRecord.objects.update_or_create(
            result=result,
            defaults={
                "student": student_profile,
                "from_semester": semester,
                "to_semester": next_semester,
                "status": PromotionRecord.Status.PROMOTED,
                "remarks": "Demo promotion based on Mid Term result.",
            },
        )

        Notice.objects.get_or_create(
            title="Mid Term result has been published",
            defaults={
                "body": "Students can view their published result card from the Results menu.",
                "audience": Notice.Audience.STUDENTS,
                "created_by": admin_user,
            },
        )

        tuition_category, _ = FeeCategory.objects.get_or_create(
            name="Tuition Fee",
            defaults={"description": "Semester tuition fee."},
        )
        fee_structure, _ = FeeStructure.objects.get_or_create(
            category=tuition_category,
            course=course,
            semester=semester,
            academic_year=academic_year,
            defaults={
                "amount": Decimal("50000.00"),
                "due_days": 30,
            },
        )
        invoice, _ = Invoice.objects.get_or_create(
            invoice_no="INV-2026-0001",
            defaults={
                "student": student_profile,
                "fee_structure": fee_structure,
                "issue_date": date(2026, 1, 10),
                "due_date": date(2026, 2, 10),
                "total_amount": Decimal("50000.00"),
                "paid_amount": Decimal("0.00"),
                "status": Invoice.Status.UNPAID,
                "notes": "Demo semester tuition invoice.",
            },
        )
        payment, _ = Payment.objects.update_or_create(
            receipt_no="RCPT-2026-0001",
            defaults={
                "invoice": invoice,
                "amount": Decimal("20000.00"),
                "payment_date": date(2026, 1, 15),
                "method": Payment.Method.CASH,
                "received_by": admin_user,
                "remarks": "Demo partial payment.",
            },
        )
        invoice.paid_amount = sum((item.amount for item in invoice.payments.all()), Decimal("0.00"))
        invoice.refresh_status()
        invoice.save(update_fields=["paid_amount", "status", "updated_at"])

        Notice.objects.get_or_create(
            title="Fee invoice generated",
            defaults={
                "body": "Students can view fee invoices, remaining dues, and payment receipts from the Fees menu.",
                "audience": Notice.Audience.STUDENTS,
                "created_by": admin_user,
            },
        )

        admin_user.profile.department = cs_department
        admin_user.profile.save(update_fields=["department"])

        self.stdout.write(self.style.SUCCESS("Demo data is ready."))
