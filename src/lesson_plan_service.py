"""Lesson Plan service for CRUD operations."""
import uuid
from typing import Optional, Dict, Any, List
from src.database import DatabaseService


class LessonPlanService:
    """Service for managing lesson plans."""
    
    def __init__(self, db_service: DatabaseService):
        """Initialize lesson plan service.
        
        Args:
            db_service: Database service instance
        """
        self.db = db_service
    
    def create_lesson_plan(
        self,
        teacher_id: str,
        class_id: str,
        subject_id: str,
        status: str,
        instructional_notes: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        topic: Optional[str] = None,
        reference_materials: Optional[str] = None,
        duration: Optional[str] = None
    ) -> str:
        """Create a new lesson plan.
        
        Args:
            teacher_id: ID of the teacher creating the plan
            class_id: ID of the class
            subject_id: ID of the subject
            status: Status ('draft' or 'finalized')
            instructional_notes: Optional instructional notes
            start_date: Optional start date (ISO 8601)
            end_date: Optional end date (ISO 8601)
            topic: Optional topic
            reference_materials: Optional reference materials
            duration: Optional duration
            
        Returns:
            ID of the created lesson plan
        """
        lesson_plan_id = str(uuid.uuid4())
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO lesson_plans (
                    id, teacher_id, class_id, subject_id, start_date, end_date,
                    instructional_notes, topic, reference_materials, duration, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                lesson_plan_id, teacher_id, class_id, subject_id, start_date, end_date,
                instructional_notes, topic, reference_materials, duration, status
            ))
        
        return lesson_plan_id
    
    def get_lesson_plan(self, lesson_plan_id: str) -> Optional[Dict[str, Any]]:
        """Get a lesson plan by ID.
        
        Args:
            lesson_plan_id: ID of the lesson plan
            
        Returns:
            Lesson plan dictionary or None if not found
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM lesson_plans WHERE id = ?
            """, (lesson_plan_id,))
            row = cursor.fetchone()
            
            if row:
                return dict(row)
            return None
    
    def update_lesson_plan(self, lesson_plan_id: str, **fields) -> bool:
        """Update a lesson plan.
        
        Args:
            lesson_plan_id: ID of the lesson plan
            **fields: Fields to update
            
        Returns:
            True if successful, False if lesson plan not found
        """
        if not fields:
            return True
        
        allowed_fields = {
            'teacher_id', 'class_id', 'subject_id', 'start_date', 'end_date',
            'instructional_notes', 'topic', 'reference_materials', 'duration', 'status'
        }
        
        update_fields = {k: v for k, v in fields.items() if k in allowed_fields}
        if not update_fields:
            return True
        
        set_clause = ', '.join(f"{field} = ?" for field in update_fields.keys())
        values = list(update_fields.values()) + [lesson_plan_id]
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                UPDATE lesson_plans SET {set_clause} WHERE id = ?
            """, values)
            
            return cursor.rowcount > 0
    
    def delete_lesson_plan(self, lesson_plan_id: str) -> bool:
        """Delete a lesson plan.
        
        Args:
            lesson_plan_id: ID of the lesson plan
            
        Returns:
            True if successful, False if lesson plan not found
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM lesson_plans WHERE id = ?
            """, (lesson_plan_id,))
            
            return cursor.rowcount > 0
    
    def list_lesson_plans(
        self,
        teacher_id: Optional[str] = None,
        class_id: Optional[str] = None,
        subject_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List lesson plans with optional filters.
        
        Args:
            teacher_id: Optional filter by teacher ID
            class_id: Optional filter by class ID
            subject_id: Optional filter by subject ID
            
        Returns:
            List of lesson plan dictionaries
        """
        conditions = []
        params = []
        
        if teacher_id:
            conditions.append("teacher_id = ?")
            params.append(teacher_id)
        if class_id:
            conditions.append("class_id = ?")
            params.append(class_id)
        if subject_id:
            conditions.append("subject_id = ?")
            params.append(subject_id)
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                SELECT * FROM lesson_plans WHERE {where_clause}
            """, params)
            
            return [dict(row) for row in cursor.fetchall()]
