import unittest
import os
import shutil
import csv
from src.database import DatabaseService
from src.import_service import ImportService
from src.report_generation_service import ReportGenerationService


class TestPhase6Professionalization(unittest.TestCase):
    def setUp(self):
        self.db_path = "test_phase6.db"
        self.db = DatabaseService(self.db_path)
        self.importer = ImportService(self.db)
        self.reporter = ReportGenerationService(self.db)
        
        # Setup foundation
        self.school_id = str(DatabaseService.generate_id())
        self.teacher_id = str(DatabaseService.generate_id())
        self.grade_id = str(DatabaseService.generate_id())
        self.subject_id = str(DatabaseService.generate_id())
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO schools (id, name) VALUES (?, ?)", (self.school_id, "Import High"))
            cursor.execute("INSERT INTO teachers (id, school_id, first_name, last_name) VALUES (?, ?, ?, ?)", 
                         (self.teacher_id, self.school_id, "John", "Doe"))
            cursor.execute("INSERT INTO grades (id, school_id, name) VALUES (?, ?, ?)", 
                         (self.grade_id, self.school_id, "Grade 10"))
            cursor.execute("INSERT INTO subjects (id, school_id, name) VALUES (?, ?, ?)", 
                         (self.subject_id, self.school_id, "Science"))

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        if os.path.exists("test_reports"):
            shutil.rmtree("test_reports")

    def test_student_import(self):
        csv_content = "first_name,last_name,grade_id\nAlice,Wonder,G1\nBob,Builder,G1"
        result = self.importer.import_students(self.school_id, csv_content)
        
        self.assertEqual(result['success_count'], 2)
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM students WHERE school_id=?", (self.school_id,))
            self.assertEqual(cursor.fetchone()['count'], 2)

    def test_curriculum_import(self):
        csv_content = "unit_name,topic_name,topic_order,topic_weeks\nUnit 1,Topic A,1,2\nUnit 1,Topic B,2,1"
        result = self.importer.import_curriculum(self.school_id, self.grade_id, self.subject_id, csv_content)
        
        self.assertEqual(result['units_imported'], 1)
        self.assertEqual(result['topics_imported'], 2)
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM curriculum_units WHERE name='Unit 1'")
            unit_id = cursor.fetchone()['id']
            cursor.execute("SELECT COUNT(*) as count FROM curriculum_topics WHERE unit_id=?", (unit_id,))
            self.assertEqual(cursor.fetchone()['count'], 2)

    def test_batch_report_export(self):
        # Setup class and student
        class_id = str(DatabaseService.generate_id())
        student_id = str(DatabaseService.generate_id())
        term_id = str(DatabaseService.generate_id())
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO classes (id, school_id, grade_id, name) VALUES (?, ?, ?, ?)",
                         (class_id, self.school_id, self.grade_id, "10A"))
            cursor.execute("INSERT INTO teacher_classes (teacher_id, class_id) VALUES (?, ?)",
                         (self.teacher_id, class_id))
            cursor.execute("INSERT INTO students (id, school_id, first_name, last_name, enrollment_status) VALUES (?, ?, ?, ?, ?)",
                         (student_id, self.school_id, "Max", "Power", "active"))
            cursor.execute("INSERT INTO student_classes (student_id, class_id) VALUES (?, ?)", (student_id, class_id))
            cursor.execute("INSERT INTO terms (id, school_id, name, start_date, end_date) VALUES (?, ?, ?, ?, ?)",
                         (term_id, self.school_id, "Term 1", "2024-01-01", "2024-03-31"))

        result = self.reporter.batch_export_reports(class_id, term_id, "test_reports")
        
        self.assertEqual(result['reports_exported'], 1)
        self.assertTrue(os.path.exists("test_reports/report_power_max.txt"))


if __name__ == "__main__":
    unittest.main()
