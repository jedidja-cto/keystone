"""Example demonstration of Phase 5: Aggregation & Reporting."""
import uuid
import os
import json
from src.database import DatabaseService
from src.report_generation_service import ReportGenerationService
from src.qualitative_observation_service import QualitativeObservationService

def demo():
    db_path = "keystone_demo_phase5.db"
    if os.path.exists(db_path):
        os.remove(db_path)
        
    db = DatabaseService(db_path)
    report_service = ReportGenerationService(db)
    obs_service = QualitativeObservationService(db)
    
    # 1. Setup Phase 0 Foundational Data
    school_id = str(uuid.uuid4())
    grade_id = str(uuid.uuid4())
    term_s1 = str(uuid.uuid4())
    student_id = str(uuid.uuid4())
    teacher_id = str(uuid.uuid4())
    math_id = str(uuid.uuid4())
    science_id = str(uuid.uuid4())
    class_10a = str(uuid.uuid4())
    
    with db.get_connection() as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO schools (id, name) VALUES (?, ?)", (school_id, "Keystone Academy"))
        cur.execute("INSERT INTO grades (id, school_id, name, ordinal) VALUES (?, ?, ?, ?)",
                  (grade_id, school_id, "Grade 10", 10))
        cur.execute("INSERT INTO terms (id, school_id, name, start_date, end_date) VALUES (?, ?, ?, ?, ?)",
                  (term_s1, school_id, "First Trimester", "2024-09-01", "2024-11-30"))
        cur.execute("INSERT INTO students (id, school_id, first_name, last_name, enrollment_status) VALUES (?, ?, ?, ?, ?)",
                  (student_id, school_id, "Max", "Verstappen", "active"))
        cur.execute("INSERT INTO teachers (id, school_id, first_name, last_name) VALUES (?, ?, ?, ?)",
                  (teacher_id, school_id, "Christian", "Horner"))
        cur.execute("INSERT INTO subjects (id, school_id, name) VALUES (?, ?, ?)",
                  (math_id, school_id, "Mathematics"))
        cur.execute("INSERT INTO subjects (id, school_id, name) VALUES (?, ?, ?)",
                  (science_id, school_id, "Physics"))
        cur.execute("INSERT INTO classes (id, school_id, grade_id, name) VALUES (?, ?, ?, ?)",
                  (class_10a, school_id, grade_id, "10-Alpha"))
        
        # En enrollments
        cur.execute("INSERT INTO student_classes (student_id, class_id) VALUES (?, ?)", (student_id, class_10a))
        cur.execute("INSERT INTO class_subjects (class_id, subject_id) VALUES (?, ?)", (class_10a, math_id))
        cur.execute("INSERT INTO class_subjects (class_id, subject_id) VALUES (?, ?)", (class_10a, science_id))

    # 2. Add Phase 1 Assessments & Marks
    with db.get_connection() as conn:
        cur = conn.cursor()
        # Math Quiz 1 (In Term)
        quiz_id = str(uuid.uuid4())
        cur.execute("INSERT INTO assessments (id, class_id, subject_id, teacher_id, name, date, maximum_marks) VALUES (?, ?, ?, ?, ?, ?, ?)",
                  (quiz_id, class_10a, math_id, teacher_id, "Algebra Quiz", "2024-10-15", 50))
        cur.execute("INSERT INTO assessment_marks (id, assessment_id, student_id, value) VALUES (?, ?, ?, ?)",
                  (str(uuid.uuid4()), quiz_id, student_id, 45))
        
        # Physics Test 1 (In Term)
        test_id = str(uuid.uuid4())
        cur.execute("INSERT INTO assessments (id, class_id, subject_id, teacher_id, name, date, maximum_marks) VALUES (?, ?, ?, ?, ?, ?, ?)",
                  (test_id, class_10a, science_id, teacher_id, "Dynamics Test", "2024-11-05", 100))
        cur.execute("INSERT INTO assessment_marks (id, assessment_id, student_id, value) VALUES (?, ?, ?, ?)",
                  (str(uuid.uuid4()), test_id, student_id, 88))

    # 3. Add Phase 4 Observations
    # Subject Specific (Math)
    obs_service.create_observation(student_id, teacher_id, "2024-10-20", "Academic", 
                                 "Excellent grasp of quadratic equations.", 
                                 class_id=class_10a, subject_id=math_id, intensity="positive")
    
    # Subject Specific (Physics)
    obs_service.create_observation(student_id, teacher_id, "2024-11-10", "Academic", 
                                 "Shows great curiosity in experimental setups.", 
                                 class_id=class_10a, subject_id=science_id, intensity="positive")
    
    # Overall
    obs_service.create_observation(student_id, teacher_id, "2024-10-01", "Social", 
                                 "Collaborates well with peers on group tasks.", intensity="positive")
    
    # Internal (Should not show in report)
    obs_service.create_observation(student_id, teacher_id, "2024-11-01", "Behavioral", 
                                 "Arrived late twice this week.", intensity="neutral")

    # 4. Generate Phase 5 Progress Report
    print("=== Generating Student Progress Report (Phase 5) ===")
    report = report_service.generate_student_progress_report(student_id, term_s1)
    
    print(f"\nReport for: {report['student_info']['first_name']} {report['student_info']['last_name']}")
    print(f"Grade: {report['student_info']['grade']}")
    print(f"Term: {report['term_info']['name']} ({report['term_info']['start_date']} to {report['term_info']['end_date']})")
    
    print("\n--- Subject Summaries ---")
    for subj in report['subject_summaries']:
        print(f"\nSubject: {subj['subject_name']}")
        print(f"Average Mark: {subj['student_average']}%")
        print("Observations:")
        for o in subj['observations']:
            print(f"  - [{o['date']}] {o['text']} ({o['intensity']})")
            
    print("\n--- Overall Observations ---")
    for o in report['overall_observations']:
        print(f"  - [{o['date']}] {o['text']} ({o['intensity']})")

    print("\n=== Phase 5 Demo Complete ===")
    
    if os.path.exists(db_path):
        os.remove(db_path)

if __name__ == "__main__":
    demo()
