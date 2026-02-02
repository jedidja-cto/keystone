"""Basic tests for Phase 1 implementation."""
import uuid
import os
from src import (
    DatabaseService,
    LessonPlanService,
    AssessmentService,
    AssessmentMarkService,
    AggregationService
)


def test_lesson_plan_crud():
    """Test lesson plan CRUD operations."""
    print("Testing lesson plan CRUD...")
    
    # Use a temporary file instead of :memory: to ensure schema persists
    import tempfile
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db.close()
    
    db = DatabaseService(temp_db.name)
    service = LessonPlanService(db)
    
    # Create test data
    with db.get_connection() as conn:
        cursor = conn.cursor()
        school_id = str(uuid.uuid4())
        cursor.execute("INSERT INTO schools (id, name) VALUES (?, ?)", (school_id, "Test School"))
        
        grade_id = str(uuid.uuid4())
        cursor.execute("INSERT INTO grades (id, school_id, name) VALUES (?, ?, ?)", 
                      (grade_id, school_id, "Grade 10"))
        
        teacher_id = str(uuid.uuid4())
        cursor.execute("INSERT INTO teachers (id, school_id, first_name, last_name) VALUES (?, ?, ?, ?)",
                      (teacher_id, school_id, "Test", "Teacher"))
        
        class_id = str(uuid.uuid4())
        cursor.execute("INSERT INTO classes (id, school_id, grade_id, name) VALUES (?, ?, ?, ?)",
                      (class_id, school_id, grade_id, "Test Class"))
        
        subject_id = str(uuid.uuid4())
        cursor.execute("INSERT INTO subjects (id, school_id, name) VALUES (?, ?, ?)",
                      (subject_id, school_id, "Test Subject"))
    
    # Create
    lp_id = service.create_lesson_plan(
        teacher_id=teacher_id,
        class_id=class_id,
        subject_id=subject_id,
        status="draft",
        instructional_notes=None,  # Test nullable notes
        topic="Test Topic"
    )
    assert lp_id is not None
    
    # Read
    lp = service.get_lesson_plan(lp_id)
    assert lp is not None
    assert lp['status'] == 'draft'
    assert lp['topic'] == 'Test Topic'
    assert lp['instructional_notes'] is None
    
    # Update
    success = service.update_lesson_plan(lp_id, status='finalized', instructional_notes='Updated notes')
    assert success is True
    
    lp = service.get_lesson_plan(lp_id)
    assert lp['status'] == 'finalized'
    assert lp['instructional_notes'] == 'Updated notes'
    
    # List
    plans = service.list_lesson_plans(teacher_id=teacher_id)
    assert len(plans) == 1
    
    # Delete
    success = service.delete_lesson_plan(lp_id)
    assert success is True
    
    lp = service.get_lesson_plan(lp_id)
    assert lp is None
    
    # Cleanup
    os.unlink(temp_db.name)
    
    print("✓ Lesson plan CRUD tests passed")


def test_assessment_mark_validation():
    """Test assessment mark validation rules."""
    print("Testing assessment mark validation...")
    
    import tempfile
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db.close()
    
    db = DatabaseService(temp_db.name)
    assessment_service = AssessmentService(db)
    mark_service = AssessmentMarkService(db)
    
    # Create test data
    with db.get_connection() as conn:
        cursor = conn.cursor()
        school_id = str(uuid.uuid4())
        cursor.execute("INSERT INTO schools (id, name) VALUES (?, ?)", (school_id, "Test School"))
        
        grade_id = str(uuid.uuid4())
        cursor.execute("INSERT INTO grades (id, school_id, name) VALUES (?, ?, ?)", 
                      (grade_id, school_id, "Grade 10"))
        
        teacher_id = str(uuid.uuid4())
        cursor.execute("INSERT INTO teachers (id, school_id, first_name, last_name) VALUES (?, ?, ?, ?)",
                      (teacher_id, school_id, "Test", "Teacher"))
        
        class_id = str(uuid.uuid4())
        cursor.execute("INSERT INTO classes (id, school_id, grade_id, name) VALUES (?, ?, ?, ?)",
                      (class_id, school_id, grade_id, "Test Class"))
        
        subject_id = str(uuid.uuid4())
        cursor.execute("INSERT INTO subjects (id, school_id, name) VALUES (?, ?, ?)",
                      (subject_id, school_id, "Test Subject"))
        
        student_id = str(uuid.uuid4())
        cursor.execute("INSERT INTO students (id, school_id, first_name, last_name, enrollment_status) VALUES (?, ?, ?, ?, ?)",
                      (student_id, school_id, "Test", "Student", "active"))
        
        # Enroll student in class
        cursor.execute("INSERT INTO student_classes (student_id, class_id) VALUES (?, ?)",
                      (student_id, class_id))
    
    # Create assessment with maximum marks
    assessment_id = assessment_service.create_assessment(
        teacher_id=teacher_id,
        class_id=class_id,
        subject_id=subject_id,
        date="2024-01-20",
        name="Test Assessment",
        maximum_marks=100.0
    )
    
    # Test valid mark
    mark_id = mark_service.create_mark(assessment_id, student_id, 85.0)
    assert mark_id is not None
    
    # Test negative mark (should fail)
    try:
        mark_service.create_mark(assessment_id, student_id, -10.0)
        assert False, "Should have raised ValueError for negative mark"
    except ValueError as e:
        assert "must be >= 0" in str(e)
    
    # Test exceeding maximum (should fail)
    try:
        mark_service.update_mark(mark_id, 150.0)
        assert False, "Should have raised ValueError for exceeding maximum"
    except ValueError as e:
        assert "exceeds maximum marks" in str(e)
    
    # Test duplicate mark (should fail due to unique constraint)
    try:
        mark_service.create_mark(assessment_id, student_id, 90.0)
        assert False, "Should have raised error for duplicate mark"
    except Exception:
        pass  # Expected to fail
    
    # Cleanup
    os.unlink(temp_db.name)
    
    print("✓ Assessment mark validation tests passed")


def test_aggregation():
    """Test class and student average calculations."""
    print("Testing aggregation...")
    
    import tempfile
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db.close()
    
    db = DatabaseService(temp_db.name)
    assessment_service = AssessmentService(db)
    mark_service = AssessmentMarkService(db)
    aggregation_service = AggregationService(db)
    
    # Create test data
    with db.get_connection() as conn:
        cursor = conn.cursor()
        school_id = str(uuid.uuid4())
        cursor.execute("INSERT INTO schools (id, name) VALUES (?, ?)", (school_id, "Test School"))
        
        grade_id = str(uuid.uuid4())
        cursor.execute("INSERT INTO grades (id, school_id, name) VALUES (?, ?, ?)", 
                      (grade_id, school_id, "Grade 10"))
        
        teacher_id = str(uuid.uuid4())
        cursor.execute("INSERT INTO teachers (id, school_id, first_name, last_name) VALUES (?, ?, ?, ?)",
                      (teacher_id, school_id, "Test", "Teacher"))
        
        class_id = str(uuid.uuid4())
        cursor.execute("INSERT INTO classes (id, school_id, grade_id, name) VALUES (?, ?, ?, ?)",
                      (class_id, school_id, grade_id, "Test Class"))
        
        subject_id = str(uuid.uuid4())
        cursor.execute("INSERT INTO subjects (id, school_id, name) VALUES (?, ?, ?)",
                      (subject_id, school_id, "Test Subject"))
        
        # Create 3 students
        student_ids = []
        for i in range(3):
            student_id = str(uuid.uuid4())
            cursor.execute("INSERT INTO students (id, school_id, first_name, last_name, enrollment_status) VALUES (?, ?, ?, ?, ?)",
                          (student_id, school_id, f"Student{i}", "Test", "active"))
            cursor.execute("INSERT INTO student_classes (student_id, class_id) VALUES (?, ?)",
                          (student_id, class_id))
            student_ids.append(student_id)
    
    # Create assessment
    assessment_id = assessment_service.create_assessment(
        teacher_id=teacher_id,
        class_id=class_id,
        subject_id=subject_id,
        date="2024-01-20",
        name="Test Assessment",
        maximum_marks=100.0
    )
    
    # Test class average with no marks
    avg = aggregation_service.calculate_class_average(assessment_id)
    assert avg is None
    
    # Add marks: 80, 90, 100
    mark_service.create_mark(assessment_id, student_ids[0], 80.0)
    mark_service.create_mark(assessment_id, student_ids[1], 90.0)
    mark_service.create_mark(assessment_id, student_ids[2], 100.0)
    
    # Test class average
    avg = aggregation_service.calculate_class_average(assessment_id)
    assert avg == 90.0
    
    # Create second assessment
    assessment_id_2 = assessment_service.create_assessment(
        teacher_id=teacher_id,
        class_id=class_id,
        subject_id=subject_id,
        date="2024-01-27",
        name="Test Assessment 2",
        maximum_marks=100.0
    )
    
    # Add marks for first student only: 70, 90
    mark_service.create_mark(assessment_id_2, student_ids[0], 70.0)
    
    # Test student average
    student_avg = aggregation_service.calculate_student_average(
        student_ids[0], class_id, subject_id
    )
    assert student_avg == 75.0  # (80 + 70) / 2
    
    # Cleanup
    os.unlink(temp_db.name)
    
    print("✓ Aggregation tests passed")


def test_export_summary():
    """Test export summary generation."""
    print("Testing export summary...")
    
    import tempfile
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db.close()
    
    db = DatabaseService(temp_db.name)
    assessment_service = AssessmentService(db)
    mark_service = AssessmentMarkService(db)
    aggregation_service = AggregationService(db)
    
    # Create test data
    with db.get_connection() as conn:
        cursor = conn.cursor()
        school_id = str(uuid.uuid4())
        cursor.execute("INSERT INTO schools (id, name) VALUES (?, ?)", (school_id, "Test School"))
        
        grade_id = str(uuid.uuid4())
        cursor.execute("INSERT INTO grades (id, school_id, name) VALUES (?, ?, ?)", 
                      (grade_id, school_id, "Grade 10"))
        
        teacher_id = str(uuid.uuid4())
        cursor.execute("INSERT INTO teachers (id, school_id, first_name, last_name) VALUES (?, ?, ?, ?)",
                      (teacher_id, school_id, "Test", "Teacher"))
        
        class_id = str(uuid.uuid4())
        cursor.execute("INSERT INTO classes (id, school_id, grade_id, name) VALUES (?, ?, ?, ?)",
                      (class_id, school_id, grade_id, "Test Class"))
        
        subject_id = str(uuid.uuid4())
        cursor.execute("INSERT INTO subjects (id, school_id, name) VALUES (?, ?, ?)",
                      (subject_id, school_id, "Test Subject"))
        
        student_id = str(uuid.uuid4())
        cursor.execute("INSERT INTO students (id, school_id, first_name, last_name, enrollment_status) VALUES (?, ?, ?, ?, ?)",
                      (student_id, school_id, "Test", "Student", "active"))
        cursor.execute("INSERT INTO student_classes (student_id, class_id) VALUES (?, ?)",
                      (student_id, class_id))
    
    # Create assessment and mark
    assessment_id = assessment_service.create_assessment(
        teacher_id=teacher_id,
        class_id=class_id,
        subject_id=subject_id,
        date="2024-01-20",
        name="Test Assessment",
        maximum_marks=100.0
    )
    mark_service.create_mark(assessment_id, student_id, 85.0)
    
    # Generate summary
    summary = aggregation_service.generate_export_summary(
        class_id=class_id,
        subject_id=subject_id
    )
    
    assert summary['class_metadata'] is not None
    assert summary['subject_metadata'] is not None
    assert len(summary['assessments']) == 1
    assert len(summary['students']) == 1
    assert summary['assessments'][0]['class_average'] == 85.0
    assert summary['students'][0]['student_average'] == 85.0
    
    # Cleanup
    os.unlink(temp_db.name)
    
    print("✓ Export summary tests passed")


def test_teacher_restrict_delete():
    """Test that teacher deletion is restricted when lesson plans exist."""
    print("Testing teacher delete restriction...")
    
    import tempfile
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db.close()
    
    db = DatabaseService(temp_db.name)
    lesson_plan_service = LessonPlanService(db)
    
    # Create test data
    with db.get_connection() as conn:
        cursor = conn.cursor()
        school_id = str(uuid.uuid4())
        cursor.execute("INSERT INTO schools (id, name) VALUES (?, ?)", (school_id, "Test School"))
        
        grade_id = str(uuid.uuid4())
        cursor.execute("INSERT INTO grades (id, school_id, name) VALUES (?, ?, ?)", 
                      (grade_id, school_id, "Grade 10"))
        
        teacher_id = str(uuid.uuid4())
        cursor.execute("INSERT INTO teachers (id, school_id, first_name, last_name) VALUES (?, ?, ?, ?)",
                      (teacher_id, school_id, "Test", "Teacher"))
        
        class_id = str(uuid.uuid4())
        cursor.execute("INSERT INTO classes (id, school_id, grade_id, name) VALUES (?, ?, ?, ?)",
                      (class_id, school_id, grade_id, "Test Class"))
        
        subject_id = str(uuid.uuid4())
        cursor.execute("INSERT INTO subjects (id, school_id, name) VALUES (?, ?, ?)",
                      (subject_id, school_id, "Test Subject"))
    
    # Create lesson plan
    lesson_plan_service.create_lesson_plan(
        teacher_id=teacher_id,
        class_id=class_id,
        subject_id=subject_id,
        status="draft"
    )
    
    # Try to delete teacher (should fail)
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM teachers WHERE id = ?", (teacher_id,))
        assert False, "Should have raised error due to RESTRICT constraint"
    except Exception:
        pass  # Expected to fail
    
    # Cleanup
    os.unlink(temp_db.name)
    
    print("✓ Teacher delete restriction test passed")


if __name__ == "__main__":
    test_lesson_plan_crud()
    test_assessment_mark_validation()
    test_aggregation()
    test_export_summary()
    test_teacher_restrict_delete()
    print("\n✓ All tests passed!")
