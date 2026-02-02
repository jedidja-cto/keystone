import unittest
import uuid

from src import (
    DatabaseService,
    WorkloadAggregationService,
    TextbookService,
    ContentMappingService,
    LessonContentAlignmentService,
    LessonPlanService,
    CurriculumService,
)


def _id() -> str:
    return str(uuid.uuid4())


class TestPhase3Guardrails(unittest.TestCase):
    """
    Guardrail tests: Phase 3 must remain OPTIONAL, INEQUALITY-AWARE, and NON-ENFORCING forever.
    
    These tests are intentionally "constitutional":
    - They block enforcement drift via return-shape checks, exception behavior checks,
      and forbidden-language / forbidden-method checks.
    """
    
    def setUp(self):
        # Important: your DatabaseService must keep a single connection for ":memory:" (you already fixed this)
        self.db = DatabaseService(":memory:")
        
        # Phase 3 services
        self.wa = WorkloadAggregationService(self.db)
        self.tb = TextbookService(self.db)
        self.cm = ContentMappingService(self.db)
        self.lca = LessonContentAlignmentService(self.db)
        
        # Phase 1/2 services to create legitimate context data
        self.lp = LessonPlanService(self.db)
        self.curr = CurriculumService(self.db)
        
        # Minimal Phase 0 entities required by FK constraints
        self.school_id = _id()
        self.grade_id = _id()
        self.subject_id = _id()
        self.teacher_id = _id()
        self.class_id = _id()
        
        with self.db.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO schools (id,name,contact_info) VALUES (?,?,?)",
                        (self.school_id, "Test School", None))
            cur.execute("INSERT INTO grades (id,school_id,name,ordinal) VALUES (?,?,?,?)",
                        (self.grade_id, self.school_id, "Grade 10", 10))
            cur.execute("INSERT INTO subjects (id,school_id,name,description) VALUES (?,?,?,?)",
                        (self.subject_id, self.school_id, "Math", None))
            cur.execute("INSERT INTO teachers (id,school_id,first_name,last_name) VALUES (?,?,?,?)",
                        (self.teacher_id, self.school_id, "Ada", "Teacher"))
            cur.execute("INSERT INTO classes (id,school_id,grade_id,name) VALUES (?,?,?,?)",
                        (self.class_id, self.school_id, self.grade_id, "10A"))
        
        # Create a real curriculum_topic for mapping
        loaded = self.curr.load_curriculum(
            self.school_id,
            self.grade_id,
            self.subject_id,
            {"units": [{"name": "Unit 1", "topics": [{"name": "Topic A", "estimated_weeks": 1}]}]},
        )
        self.topic_id = loaded["units"][0]["topics"][0]["id"]
        
        # Create lesson plans in period (Phase 1)
        self.lesson1_id = self.lp.create_lesson_plan(
            teacher_id=self.teacher_id,
            class_id=self.class_id,
            subject_id=self.subject_id,
            status="draft",
            instructional_notes=None,
            topic="Topic A",
            start_date="2024-02-01",
            end_date="2024-02-07",
        )
        self.lesson2_id = self.lp.create_lesson_plan(
            teacher_id=self.teacher_id,
            class_id=self.class_id,
            subject_id=self.subject_id,
            status="draft",
            instructional_notes=None,
            topic="Topic A",
            start_date="2024-02-08",
            end_date="2024-02-14",
        )
    
    # ----------------------------
    # OPTIONALITY GUARDRAILS
    # ----------------------------
    def test_period_workload_returns_zeros_without_textbooks_mappings_alignments(self):
        """
        Nothing in Phase 3 is required.
        With no textbooks/mappings/alignments, workload must return zeros and must not error.
        """
        result = self.wa.calculate_workload_for_period(
            self.class_id, self.subject_id, "2024-02-01", "2024-02-28"
        )
        
        self.assertEqual(result["total_pages"], 0)
        self.assertEqual(result["total_exercises"], 0)
        self.assertEqual(result["total_time_minutes"], 0)
        self.assertEqual(result["lesson_count"], 2)  # two lessons exist
        self.assertEqual(result["aligned_lesson_count"], 0)  # none aligned
    
    def test_topic_workload_returns_zeros_without_mappings(self):
        """
        A topic can exist without mappings; workload must return zeros.
        """
        result = self.wa.calculate_workload_for_topic(self.topic_id)
        
        self.assertEqual(result["total_pages"], 0)
        self.assertEqual(result["total_exercises"], 0)
        self.assertEqual(result["total_time_minutes"], 0)
        self.assertEqual(result["mapping_count"], 0)
    
    # ----------------------------
    # NON-ENFORCEMENT GUARDRAILS
    # ----------------------------
    def test_missing_optional_fields_never_error_and_aggregate_as_zero(self):
        """
        Mappings may have NULL workload fields. Aggregation must not error and must treat NULL as 0.
        """
        tb_id = self.tb.register_textbook(
            subject_id=self.subject_id,
            title="Book 1",
            edition=None,
            publisher=None,
            isbn=None,
            publication_year=None,
        )
        
        mapping_id = self.cm.create_content_mapping(
            topic_id=self.topic_id,
            textbook_id=tb_id,
            start_page=None,
            end_page=None,
            exercise_references=None,
            estimated_pages=None,
            estimated_exercises=None,
            estimated_time_minutes=None,
        )
        
        self.lca.align_lesson_to_content(self.lesson1_id, mapping_id)
        
        result = self.wa.calculate_workload_for_period(
            self.class_id, self.subject_id, "2024-02-01", "2024-02-28"
        )
        
        self.assertEqual(result["lesson_count"], 2)
        self.assertEqual(result["aligned_lesson_count"], 1)  # lesson1 aligned
        self.assertEqual(result["total_pages"], 0)
        self.assertEqual(result["total_exercises"], 0)
        self.assertEqual(result["total_time_minutes"], 0)
    
    def test_deleting_phase3_entities_never_deletes_lessons(self):
        """
        Phase 3 deletions must not affect Phase 1 lesson plans.
        (Mappings may cascade; lesson plans must remain.)
        """
        tb_id = self.tb.register_textbook(self.subject_id, "Book 2", edition="1", publisher="Pub", isbn=None, publication_year=None)
        mapping_id = self.cm.create_content_mapping(self.topic_id, tb_id, estimated_pages=10)
        self.lca.align_lesson_to_content(self.lesson1_id, mapping_id)
        
        # Delete textbook -> content_mappings likely cascade -> alignments cascade
        self.tb.delete_textbook(tb_id)
        
        # Lessons must still exist
        self.assertIsNotNone(self.lp.get_lesson_plan(self.lesson1_id))
        self.assertIsNotNone(self.lp.get_lesson_plan(self.lesson2_id))
        
        # Aggregation must still be safe (no exceptions)
        result = self.wa.calculate_workload_for_period(
            self.class_id, self.subject_id, "2024-02-01", "2024-02-28"
        )
        self.assertIn("total_pages", result)
        self.assertIn("lesson_count", result)
    
    # ----------------------------
    # RETURN SHAPE GUARDRAILS
    # ----------------------------
    def test_period_return_shape_is_informational_only(self):
        """
        If someone adds warnings/flags/status/compliance fields, they're drifting into enforcement.
        """
        result = self.wa.calculate_workload_for_period(
            self.class_id, self.subject_id, "2024-02-01", "2024-02-28"
        )
        
        expected_keys = {
            "total_pages",
            "total_exercises",
            "total_time_minutes",
            "lesson_count",
            "aligned_lesson_count",
        }
        self.assertEqual(set(result.keys()), expected_keys)
    
    def test_topic_return_shape_is_informational_only(self):
        result = self.wa.calculate_workload_for_topic(self.topic_id)
        
        expected_keys = {
            "total_pages",
            "total_exercises",
            "total_time_minutes",
            "mapping_count",
        }
        self.assertEqual(set(result.keys()), expected_keys)
    
    # ----------------------------
    # "NO ENFORCEMENT HOOKS" GUARDRAILS
    # ----------------------------
    def test_phase3_services_do_not_expose_enforcement_methods(self):
        """
        If these method names appear later, someone is building coercion.
        """
        forbidden_fragments = [
            "enforce",
            "require",
            "must",
            "block",
            "lock",
            "penal",
            "compliance",
            "noncompliance",
            "deadline",
            "overdue",
            "threshold",
            "limit",
            "violation",
        ]
        
        services = [self.wa, self.tb, self.cm, self.lca]
        for svc in services:
            names = [n.lower() for n in dir(svc)]
            for frag in forbidden_fragments:
                self.assertTrue(
                    all(frag not in n for n in names),
                    msg=f"Found enforcement-like name fragment '{frag}' on {svc.__class__.__name__}",
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)