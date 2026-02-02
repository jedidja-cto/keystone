"""Service for managing qualitative student observations."""
import uuid
from typing import List, Optional, Dict, Any
from src.database import DatabaseService


class QualitativeObservationService:
    """Manages qualitative observations about students."""
    
    def __init__(self, db_service: DatabaseService):
        """Initialize service.
        
        Args:
            db_service: Database service instance
        """
        self.db = db_service

    def create_observation(
        self,
        student_id: str,
        teacher_id: str,
        date: str,
        category: str,
        observation_text: str,
        class_id: Optional[str] = None,
        subject_id: Optional[str] = None,
        intensity: Optional[str] = None
    ) -> str:
        """Create a new qualitative observation.
        
        Args:
            student_id: ID of the student
            teacher_id: ID of the teacher
            date: Observation date (YYYY-MM-DD)
            category: Observation category (e.g., 'Academic')
            observation_text: free-text notes
            class_id: Optional class ID
            subject_id: Optional subject ID
            intensity: Optional intensity ('positive', 'neutral', 'concern')
            
        Returns:
            ID of the created observation
        """
        if not observation_text:
            raise ValueError("Observation text cannot be empty")
            
        if intensity and intensity not in ('positive', 'neutral', 'concern'):
            raise ValueError("Invalid intensity level")

        observation_id = str(uuid.uuid4())
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO qualitative_observations (
                    id, student_id, teacher_id, class_id, subject_id, 
                    date, category, observation_text, intensity
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                observation_id, student_id, teacher_id, class_id, subject_id,
                date, category, observation_text, intensity
            ))
            
        return observation_id

    def get_observation(self, observation_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific observation by ID.
        
        Args:
            observation_id: ID of the observation
            
        Returns:
            Observation dictionary or None if not found
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM qualitative_observations WHERE id = ?
            """, (observation_id,))
            
            row = cursor.fetchone()
            return dict(row) if row else None

    def update_observation(self, observation_id: str, **fields) -> bool:
        """Update an existing observation.
        
        Args:
            observation_id: ID of the observation
            **fields: Fields to update (date, category, observation_text, intensity, etc.)
            
        Returns:
            True if updated, False if not found
        """
        if not fields:
            return False
            
        valid_fields = {
            'date', 'category', 'observation_text', 'class_id', 
            'subject_id', 'intensity'
        }
        
        update_parts = []
        params = []
        
        for field, value in fields.items():
            if field not in valid_fields:
                continue
            
            if field == 'observation_text' and not value:
                raise ValueError("Observation text cannot be empty")
            
            if field == 'intensity' and value and value not in ('positive', 'neutral', 'concern'):
                raise ValueError("Invalid intensity level")
                
            update_parts.append(f"{field} = ?")
            params.append(value)
            
        if not update_parts:
            return False
            
        params.append(observation_id)
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                UPDATE qualitative_observations
                SET {', '.join(update_parts)}
                WHERE id = ?
            """, params)
            
            return cursor.rowcount > 0

    def delete_observation(self, observation_id: str) -> bool:
        """Delete an observation.
        
        Args:
            observation_id: ID of the observation
            
        Returns:
            True if deleted, False if not found
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM qualitative_observations WHERE id = ?", (observation_id,))
            return cursor.rowcount > 0

    def list_observations(
        self,
        student_id: Optional[str] = None,
        teacher_id: Optional[str] = None,
        category: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List observations with optional filters.
        
        Args:
            student_id: Filter by student
            teacher_id: Filter by teacher
            category: Filter by category
            start_date: Filter by date (>=)
            end_date: Filter by date (<=)
            
        Returns:
            List of observation dictionaries
        """
        query = "SELECT * FROM qualitative_observations"
        conditions = []
        params = []
        
        if student_id:
            conditions.append("student_id = ?")
            params.append(student_id)
            
        if teacher_id:
            conditions.append("teacher_id = ?")
            params.append(teacher_id)
            
        if category:
            conditions.append("category = ?")
            params.append(category)
            
        if start_date:
            conditions.append("date >= ?")
            params.append(start_date)
            
        if end_date:
            conditions.append("date <= ?")
            params.append(end_date)
            
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
            
        query += " ORDER BY date DESC"
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
