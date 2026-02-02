"""Lesson content alignment service for Phase 3."""
from typing import Optional, List, Dict, Any
from src.database import DatabaseService


class LessonContentAlignmentService:
    """Manages lesson content alignments (lesson plan → content mapping)."""
    
    def __init__(self, db: DatabaseService):
        """Initialize lesson content alignment service.
        
        Args:
            db: Database service instance
        """
        self.db = db
    
    def align_lesson_to_content(
        self,
        lesson_plan_id: str,
        content_mapping_id: str
    ) -> bool:
        """Align a lesson plan to a content mapping (optional association).
        
        Args:
            lesson_plan_id: Lesson plan ID
            content_mapping_id: Content mapping ID
        
        Returns:
            True if alignment created, False if already exists
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO lesson_content_alignments (lesson_plan_id, content_mapping_id)
                    VALUES (?, ?)
                """, (lesson_plan_id, content_mapping_id))
                return cursor.rowcount > 0
            except Exception:
                # Alignment already exists (UNIQUE constraint)
                return False
    
    def remove_alignment(
        self,
        lesson_plan_id: str,
        content_mapping_id: str
    ) -> bool:
        """Remove a lesson content alignment.
        
        Args:
            lesson_plan_id: Lesson plan ID
            content_mapping_id: Content mapping ID
        
        Returns:
            True if removed, False if not found
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM lesson_content_alignments
                WHERE lesson_plan_id = ? AND content_mapping_id = ?
            """, (lesson_plan_id, content_mapping_id))
            return cursor.rowcount > 0
    
    def list_alignments_for_lesson(self, lesson_plan_id: str) -> List[Dict[str, Any]]:
        """List all content mappings aligned to a lesson plan.
        
        Args:
            lesson_plan_id: Lesson plan ID
        
        Returns:
            List of content mapping dicts
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT cm.id, cm.topic_id, cm.textbook_id, cm.start_page, cm.end_page,
                       cm.exercise_references, cm.estimated_pages, cm.estimated_exercises,
                       cm.estimated_time_minutes
                FROM content_mappings cm
                JOIN lesson_content_alignments lca ON cm.id = lca.content_mapping_id
                WHERE lca.lesson_plan_id = ?
            """, (lesson_plan_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    def list_lessons_for_content(self, content_mapping_id: str) -> List[Dict[str, Any]]:
        """List all lesson plans aligned to a content mapping.
        
        Args:
            content_mapping_id: Content mapping ID
        
        Returns:
            List of lesson plan dicts (read-only from Phase 1)
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT lp.id, lp.teacher_id, lp.class_id, lp.subject_id,
                       lp.start_date, lp.end_date, lp.topic, lp.status
                FROM lesson_plans lp
                JOIN lesson_content_alignments lca ON lp.id = lca.lesson_plan_id
                WHERE lca.content_mapping_id = ?
                ORDER BY lp.start_date
            """, (content_mapping_id,))
            return [dict(row) for row in cursor.fetchall()]
