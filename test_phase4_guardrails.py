import unittest
import uuid
from src import DatabaseService, QualitativeObservationService

def _id():
    return str(uuid.uuid4())

class TestPhase4Guardrails(unittest.TestCase):
    """
    Guardrail tests: Phase 4 Qualitative Observations must remain teacher-private
    and non-enforcing.
    """
    
    def setUp(self):
        self.db = DatabaseService(":memory:")
        self.os = QualitativeObservationService(self.db)
        
        # Minimal Phase 0 entities
        self.school_id = _id()
        self.grade_id = _id()
        self.student_id = _id()
        self.teacher_id = _id()
        self.subject_id = _id()
        self.class_id = _id()
        
        with self.db.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO schools (id, name) VALUES (?, ?)", (self.school_id, "Test School"))
            cur.execute("INSERT INTO grades (id, school_id, name, ordinal) VALUES (?, ?, ?, ?)",
                        (self.grade_id, self.school_id, "Year 10", 10))
            cur.execute("INSERT INTO students (id, school_id, first_name, last_name, enrollment_status) VALUES (?, ?, ?, ?, ?)",
                        (self.student_id, self.school_id, "Jane", "Doe", "active"))
            cur.execute("INSERT INTO teachers (id, school_id, first_name, last_name) VALUES (?, ?, ?, ?)",
                        (self.teacher_id, self.school_id, "Ada", "Lovelace"))
            cur.execute("INSERT INTO subjects (id, school_id, name) VALUES (?, ?, ?)",
                        (self.subject_id, self.school_id, "Philosophy"))
            cur.execute("INSERT INTO classes (id, school_id, grade_id, name) VALUES (?, ?, ?, ?)",
                        (self.class_id, self.school_id, self.grade_id, "Ethics 101"))

    def test_create_and_list_observation(self):
        """Verify basic CRUD and filtering."""
        obs_id = self.os.create_observation(
            student_id=self.student_id,
            teacher_id=self.teacher_id,
            date="2024-03-01",
            category="Academic",
            observation_text="Strong participation in today's discussion.",
            intensity="positive"
        )
        
        obs = self.os.get_observation(obs_id)
        self.assertEqual(obs['observation_text'], "Strong participation in today's discussion.")
        
        list_obs = self.os.list_observations(student_id=self.student_id)
        self.assertEqual(len(list_obs), 1)
        self.assertEqual(list_obs[0]['id'], obs_id)

    def test_student_deletion_cascades_to_observations(self):
        """Verify that observations don't outlive their students."""
        self.os.create_observation(
            self.student_id, self.teacher_id, "2024-03-01", "Social", "Helpful to peers."
        )
        
        with self.db.get_connection() as conn:
            conn.execute("DELETE FROM students WHERE id = ?", (self.student_id,))
            
        list_obs = self.os.list_observations(student_id=self.student_id)
        self.assertEqual(len(list_obs), 0)

    def test_teacher_deletion_is_restricted_by_observations(self):
        """Verify Phase 1 compatibility: teachers cannot be deleted if they authored observations."""
        self.os.create_observation(
            self.student_id, self.teacher_id, "2024-03-01", "Behavioral", "Interrupted class."
        )
        
        import sqlite3
        with self.assertRaises(sqlite3.IntegrityError):
            with self.db.get_connection() as conn:
                conn.execute("DELETE FROM teachers WHERE id = ?", (self.teacher_id,))

    def test_invalid_intensity_raises_error(self):
        """Verify strict non-enforcement boundaries for data types."""
        with self.assertRaises(ValueError):
            self.os.create_observation(
                self.student_id, self.teacher_id, "2024-03-01", "Academic", "Text",
                intensity="invalid_level"
            )

    def test_empty_text_raises_error(self):
        with self.assertRaises(ValueError):
            self.os.create_observation(
                self.student_id, self.teacher_id, "2024-03-01", "Academic", ""
            )

if __name__ == "__main__":
    unittest.main()
