"""Assessment Mark service for CRUD operations."""
import uuid
from typing import Optional, Dict, Any, List
from src.database import DatabaseService


class AssessmentMarkService:
    """Service for managing assessment marks."""
    
    def __init__(self, db_service: DatabaseService):
        """Initialize assessment mark service.
        
        Args:
            db_service: Database service instance
        """
        self.db = db_service
    
    def create_mark(
        self,
        assessment_id: str,
        student_id: str,
        value: float
    ) -> str:
        """Create a new assessment mark.
        
        Args:
            assessment_id: ID of the assessment
            student_id: ID of the student
            value: Mark value (must be >= 0)
            
        Returns:
            ID of the created mark
            
        Raises:
            ValueError: If validation fails
        """
        # Validate value is non-negative
        if value < 0:
            raise ValueError("Mark value must be >= 0")
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get assessment details
            cursor.execute("""
                SELECT class_id, maximum_marks FROM assessments WHERE id = ?
            """, (assessment_id,))
            assessment = cursor.fetchone()
            
            if not assessment:
                raise ValueError(f"Assessment {assessment_id} not found")
            
            class_id = assessment['class_id']
            maximum_marks = assessment['maximum_marks']
            
            # Validate value against maximum_marks
            if maximum_marks is not None and value > maximum_marks:
                raise ValueError(
                    f"Mark value {value} exceeds maximum marks {maximum_marks}"
                )
            
            # Validate student is enrolled in the class
            cursor.execute("""
                SELECT 1 FROM student_classes
                WHERE student_id = ? AND class_id = ?
            """, (student_id, class_id))
            
            if not cursor.fetchone():
                raise ValueError(
                    f"Student {student_id} is not enrolled in class {class_id}"
                )
            
            # Create the mark
            mark_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO assessment_marks (id, assessment_id, student_id, value)
                VALUES (?, ?, ?, ?)
            """, (mark_id, assessment_id, student_id, value))
        
        return mark_id
    
    def get_mark(self, mark_id: str) -> Optional[Dict[str, Any]]:
        """Get an assessment mark by ID.
        
        Args:
            mark_id: ID of the mark
            
        Returns:
            Mark dictionary or None if not found
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM assessment_marks WHERE id = ?
            """, (mark_id,))
            row = cursor.fetchone()
            
            if row:
                return dict(row)
            return None
    
    def update_mark(self, mark_id: str, value: float) -> bool:
        """Update an assessment mark value.
        
        Args:
            mark_id: ID of the mark
            value: New mark value (must be >= 0)
            
        Returns:
            True if successful, False if mark not found
            
        Raises:
            ValueError: If validation fails
        """
        # Validate value is non-negative
        if value < 0:
            raise ValueError("Mark value must be >= 0")
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get mark and assessment details
            cursor.execute("""
                SELECT am.assessment_id, a.maximum_marks
                FROM assessment_marks am
                JOIN assessments a ON am.assessment_id = a.id
                WHERE am.id = ?
            """, (mark_id,))
            result = cursor.fetchone()
            
            if not result:
                return False
            
            maximum_marks = result['maximum_marks']
            
            # Validate value against maximum_marks
            if maximum_marks is not None and value > maximum_marks:
                raise ValueError(
                    f"Mark value {value} exceeds maximum marks {maximum_marks}"
                )
            
            # Update the mark
            cursor.execute("""
                UPDATE assessment_marks SET value = ? WHERE id = ?
            """, (value, mark_id))
            
            return cursor.rowcount > 0
    
    def delete_mark(self, mark_id: str) -> bool:
        """Delete an assessment mark.
        
        Args:
            mark_id: ID of the mark
            
        Returns:
            True if successful, False if mark not found
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM assessment_marks WHERE id = ?
            """, (mark_id,))
            
            return cursor.rowcount > 0
    
    def list_marks(
        self,
        assessment_id: Optional[str] = None,
        student_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List assessment marks with optional filters.
        
        Args:
            assessment_id: Optional filter by assessment ID
            student_id: Optional filter by student ID
            
        Returns:
            List of mark dictionaries
        """
        conditions = []
        params = []
        
        if assessment_id:
            conditions.append("assessment_id = ?")
            params.append(assessment_id)
        if student_id:
            conditions.append("student_id = ?")
            params.append(student_id)
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                SELECT * FROM assessment_marks WHERE {where_clause}
            """, params)
            
            return [dict(row) for row in cursor.fetchall()]
