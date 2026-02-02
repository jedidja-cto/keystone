"""Example usage of Keystone Phase 1 system."""
import uuid
from src import (
    DatabaseService,
    LessonPlanService,
    AssessmentService,
    AssessmentMarkService,
    AggregationService
)


def main():
    """Demonstrate Phase 1 functionality."""
    # Initialize services
    db = DatabaseService("example.db")
    lesson_plan_service = LessonPlanService(db)
    assessment_service = AssessmentService(db)
    mark_service = AssessmentMarkService(db)
    aggregation_service = AggregationService(db)
    
    # Create Phase 0 foundational data
    print("Creating foundational data...")
    
    with db.get_connection() as conn:
        cursor = conn.cursor()
        
        # Create school
        school_id = str(uuid.uuid4())
        cursor.execute(
            "INSERT INTO schools (id, name, contact_info) VALUES (?, ?, ?)",
            (school_id, "Example High School", "contact@example.edu")
        )
        
        # Create grade
        grade_id = str(uuid.uuid4())
        cursor.execute(
            "INSERT INTO grades (id, school_id, name, ordinal) VALUES (?, ?, ?, ?)",
            (grade_id, school_id, "Grade 10", 10)
        )
        
        # Create teacher
        teacher_id = str(uuid.uuid4())
        cursor.execute(
            "INSERT INTO teachers (id, school_id, first_name, last_name) VALUES (?, ?, ?, ?)",
            (teacher_id, school_id, "Jane", "Smith")
        )
        
        # Create subject
        subject_id = str(uuid.uuid4())
        cursor.execute(
            "INSERT INTO subjects (id, school_id, name, description) VALUES (?, ?, ?, ?)",
            (subject_id, school_id, "Mathematics", "High school mathematics")
        )
        
        # Create class
        class_id = str(uuid.uuid4())
        cursor.execute(
            "INSERT INTO classes (id, school_id, grade_id, name) VALUES (?, ?, ?, ?)",
            (class_id, school_id, grade_id, "Math 10A")
        )
        
        # Link class to subject
        cursor.execute(
            "INSERT INTO class_subjects (class_id, subject_id) VALUES (?, ?)",
            (class_id, subject_id)
        )
        
        # Create students
        student_ids = []
        for i, (first, last) in enumerate([
            ("Alice", "Johnson"),
            ("Bob", "Williams"),
            ("Carol", "Brown")
        ], 1):
            student_id = str(uuid.uuid4())
            cursor.execute(
                "INSERT INTO students (id, school_id, first_name, last_name, enrollment_status) VALUES (?, ?, ?, ?, ?)",
                (student_id, school_id, first, last, "active")
            )
            # Enroll student in class
            cursor.execute(
                "INSERT INTO student_classes (student_id, class_id) VALUES (?, ?)",
                (student_id, class_id)
            )
            student_ids.append(student_id)
    
    print(f"Created school, teacher, class, subject, and {len(student_ids)} students\n")
    
    # Phase 1: Create lesson plan
    print("Creating lesson plan...")
    lesson_plan_id = lesson_plan_service.create_lesson_plan(
        teacher_id=teacher_id,
        class_id=class_id,
        subject_id=subject_id,
        status="draft",
        instructional_notes="Introduction to quadratic equations",
        topic="Quadratic Equations",
        start_date="2024-01-15"
    )
    print(f"Created lesson plan: {lesson_plan_id}")
    
    # Update lesson plan to finalized
    lesson_plan_service.update_lesson_plan(lesson_plan_id, status="finalized")
    print("Updated lesson plan to finalized\n")
    
    # Phase 1: Create assessment
    print("Creating assessment...")
    assessment_id = assessment_service.create_assessment(
        teacher_id=teacher_id,
        class_id=class_id,
        subject_id=subject_id,
        date="2024-01-20",
        name="Quadratic Equations Quiz",
        description="Quiz on solving quadratic equations",
        maximum_marks=100.0
    )
    print(f"Created assessment: {assessment_id}\n")
    
    # Phase 1: Enter marks
    print("Entering marks...")
    marks = [
        (student_ids[0], 85.0),
        (student_ids[1], 92.0),
        (student_ids[2], 78.0)
    ]
    
    for student_id, value in marks:
        mark_id = mark_service.create_mark(assessment_id, student_id, value)
        print(f"  Entered mark {value} for student")
    
    # Calculate class average
    class_avg = aggregation_service.calculate_class_average(assessment_id)
    print(f"\nClass average: {class_avg:.2f}")
    
    # Create second assessment
    print("\nCreating second assessment...")
    assessment_id_2 = assessment_service.create_assessment(
        teacher_id=teacher_id,
        class_id=class_id,
        subject_id=subject_id,
        date="2024-01-27",
        name="Quadratic Equations Test",
        maximum_marks=100.0
    )
    
    # Enter marks for second assessment
    marks_2 = [
        (student_ids[0], 90.0),
        (student_ids[1], 88.0),
        (student_ids[2], 82.0)
    ]
    
    for student_id, value in marks_2:
        mark_service.create_mark(assessment_id_2, student_id, value)
    
    # Calculate student averages
    print("\nStudent averages:")
    for student_id in student_ids:
        avg = aggregation_service.calculate_student_average(
            student_id, class_id, subject_id
        )
        print(f"  Student average: {avg:.2f}")
    
    # Generate export summary
    print("\nGenerating export summary...")
    summary = aggregation_service.generate_export_summary(
        class_id=class_id,
        subject_id=subject_id
    )
    
    print(f"Class: {summary['class_metadata']['name']}")
    print(f"Subject: {summary['subject_metadata']['name']}")
    print(f"Number of assessments: {len(summary['assessments'])}")
    print(f"Number of students: {len(summary['students'])}")
    
    print("\nAssessments:")
    for assessment in summary['assessments']:
        print(f"  - {assessment['name']}: Class avg = {assessment['class_average']:.2f}")
    
    print("\nStudents:")
    for student in summary['students']:
        print(f"  - {student['first_name']} {student['last_name']}: Avg = {student['student_average']:.2f}")
    
    print("\n✓ Phase 1 implementation complete!")


if __name__ == "__main__":
    main()
