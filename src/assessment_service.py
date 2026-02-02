"""Assessment service for CRUD operations."""
import uuid
from typing import Optional, Dict, Any, List
from src.database import DatabaseService


class AssessmentService:
    """Service for managing assessments."""
    
    def __init__(self, db_service: DatabaseService):
        """Initialize assessment service.
        
        Args:
            db_service: Database service instance
        """
        self.db = db_service
    
    def create_assessment(
        self,
        teacher_id: str,
        class_id: str,
        subject_id: str,
        date: str,
        name: str,
        description: Optional[str] = None,
        maximum_marks: Optional[float] = None
    ) -> str:
        """Create a new assessment.
        
        Args:
            teacher_id: ID of the teacher creating the assessment
            class_id: ID of the class
            subject_id: ID of the subject
            date: Assessment date (ISO 8601)
            name: Assessment name
            description: Optional description
            maximum_marks: Optional maximum marks
            
        Returns:
            ID of the created assessment
        """
        assessment_id = str(uuid.uuid4())
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO assessments (
                    id, teacher_id, class_id, subject_id, date, name,
                    description, maximum_marks
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                assessment_id, teacher_id, class_id, subject_id, date, name,
                description, maximum_marks
            ))
        
        return assessment_id
    
    def get_assessment(self, assessment_id: str) -> Optional[Dict[str, Any]]:
        """Get an assessment by ID.
        
        Args:
            assessment_id: ID of the assessment
            
        Returns:
            Assessment dictionary or None if not found
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM assessments WHERE id = ?
            """, (assessment_id,))
            row = cursor.fetchone()
            
            if row:
                return dict(row)
            return None
    
    def update_assessment(self, assessment_id: str, **fields) -> bool:
        """Update an assessment.
        
        Args:
            assessment_id: ID of the assessment
            **fields: Fields to update
            
        Returns:
            True if successful, False if assessment not found
        """
        if not fields:
            return True
        
        allowed_fields = {
            'teacher_id', 'class_id', 'subject_id', 'date', 'name',
            'description', 'maximum_marks'
        }
        
        update_fields = {k: v for k, v in fields.items() if k in allowed_fields}
        if not update_fields:
            return True
        
        set_clause = ', '.join(f"{field} = ?" for field in update_fields.keys())
        values = list(update_fields.values()) + [assessment_id]
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                UPDATE assessments SET {set_clause} WHERE id = ?
            """, values)
            
            return cursor.rowcount > 0
    
    def delete_assessment(self, assessment_id: str) -> bool:
        """Delete an assessment.
        
        Args:
            assessment_id: ID of the assessment
            
        Returns:
            True if successful, False if assessment not found
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM assessments WHERE id = ?
            """, (assessment_id,))
            
            return cursor.rowcount > 0
    
    def list_assessments(
        self,
        teacher_id: Optional[str] = None,
        class_id: Optional[str] = None,
        subject_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List assessments with optional filters.
        
        Args:
            teacher_id: Optional filter by teacher ID
            class_id: Optional filter by class ID
            subject_id: Optional filter by subject ID
            
        Returns:
            List of assessment dictionaries
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
                SELECT * FROM assessments WHERE {where_clause}
            """, params)
            
            return [dict(row) for row in cursor.fetchall()]
