import unittest
import uuid
import os
from src.database import DatabaseService
from src.report_generation_service import ReportGenerationService
from src.qualitative_observation_service import QualitativeObservationService

def _id():
    return str(uuid.uuid4())

class TestPhase5Guardrails(unittest.TestCase):
    def setUp(self):
        self.db_path = f"test_phase5_{uuid.uuid4()}.db"
        self.db = DatabaseService(self.db_path)
        self.service = ReportGenerationService(self.db)
        self.obs_service = QualitativeObservationService(self.db)
        
        # Setup foundational data (Phase 0)
        self.school_id = _id()
        self.grade_id = _id()
        self.term_id = _id()
        self.student_id = _id()
        self.teacher_id = _id()
        self.subject_id = _id()
        self.class_id = _id()
        
        with self.db.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO schools (id, name) VALUES (?, ?)", (self.school_id, "Test School"))
            cur.execute("INSERT INTO grades (id, school_id, name, ordinal) VALUES (?, ?, ?, ?)",
                        (self.grade_id, self.school_id, "Year 10", 10))
            cur.execute("INSERT INTO terms (id, school_id, name, start_date, end_date) VALUES (?, ?, ?, ?, ?)",
                        (self.term_id, self.school_id, "Term 1", "2024-01-01", "2024-03-31"))
            cur.execute("INSERT INTO students (id, school_id, first_name, last_name, enrollment_status) VALUES (?, ?, ?, ?, ?)",
                        (self.student_id, self.school_id, "Jane", "Doe", "active"))
            cur.execute("INSERT INTO teachers (id, school_id, first_name, last_name) VALUES (?, ?, ?, ?)",
                        (self.teacher_id, self.school_id, "Ada", "Lovelace"))
            cur.execute("INSERT INTO subjects (id, school_id, name) VALUES (?, ?, ?)",
                        (self.subject_id, self.school_id, "Philosophy"))
            cur.execute("INSERT INTO classes (id, school_id, grade_id, name) VALUES (?, ?, ?, ?)",
                        (self.class_id, self.school_id, self.grade_id, "Ethics 101"))
            cur.execute("INSERT INTO student_classes (student_id, class_id) VALUES (?, ?)",
                        (self.student_id, self.class_id))
            cur.execute("INSERT INTO class_subjects (class_id, subject_id) VALUES (?, ?)",
                        (self.class_id, self.subject_id))

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_report_filters_by_term_date(self):
        """Verify that marks outside the term are not aggregated."""
        assessment_in = _id()
        assessment_out = _id()
        
        with self.db.get_connection() as conn:
            cur = conn.cursor()
            # Assessment in term
            cur.execute("INSERT INTO assessments (id, class_id, subject_id, teacher_id, name, date, maximum_marks) VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (assessment_in, self.class_id, self.subject_id, self.teacher_id, "In Term", "2024-02-01", 100))
            cur.execute("INSERT INTO assessment_marks (id, assessment_id, student_id, value) VALUES (?, ?, ?, ?)",
                        (_id(), assessment_in, self.student_id, 80))
            
            # Assessment out of term
            cur.execute("INSERT INTO assessments (id, class_id, subject_id, teacher_id, name, date, maximum_marks) VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (assessment_out, self.class_id, self.subject_id, self.teacher_id, "Out of Term", "2024-04-01", 100))
            cur.execute("INSERT INTO assessment_marks (id, assessment_id, student_id, value) VALUES (?, ?, ?, ?)",
                        (_id(), assessment_out, self.student_id, 20))

        report = self.service.generate_student_progress_report(self.student_id, self.term_id)
        
        # Average should be 80, not (80+20)/2 = 50
        self.assertEqual(report['subject_summaries'][0]['student_average'], 80.0)

    def test_report_filters_qualitative_categories(self):
        """Verify only Academic and Social observations are in parent report."""
        # Reportable (Linked to subject)
        self.obs_service.create_observation(self.student_id, self.teacher_id, "2024-02-01", "Academic", "Great work", class_id=self.class_id, subject_id=self.subject_id)
        # Not Reportable (Internal)
        self.obs_service.create_observation(self.student_id, self.teacher_id, "2024-02-02", "Behavioral", "Struggled with focus", class_id=self.class_id, subject_id=self.subject_id)
        
        report = self.service.generate_student_progress_report(self.student_id, self.term_id)
        
        obs_texts = [o['text'] for s in report['subject_summaries'] for o in s['observations']]
        self.assertIn("Great work", obs_texts)
        self.assertNotIn("Struggled with focus", obs_texts)

    def test_overall_observations_separation(self):
        """Verify obs without subject go into overall section."""
        self.obs_service.create_observation(self.student_id, self.teacher_id, "2024-02-10", "Social", "Helpful peer")
        
        report = self.service.generate_student_progress_report(self.student_id, self.term_id)
        
        self.assertEqual(len(report['overall_observations']), 1)
        self.assertEqual(report['overall_observations'][0]['text'], "Helpful peer")

if __name__ == "__main__":
    import traceback
    try:
        unittest.main()
    except Exception:
        traceback.print_exc()
