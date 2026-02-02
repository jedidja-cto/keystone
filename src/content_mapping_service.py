"""Content mapping service for Phase 3."""
import uuid
from typing import Optional, List, Dict, Any
from src.database import DatabaseService


class ContentMappingService:
    """Manages content mappings (topic → textbook content)."""
    
    def __init__(self, db: DatabaseService):
        """Initialize content mapping service.
        
        Args:
            db: Database service instance
        """
        self.db = db
    
    def create_content_mapping(
        self,
        topic_id: str,
        textbook_id: str,
        start_page: Optional[int] = None,
        end_page: Optional[int] = None,
        exercise_references: Optional[str] = None,
        estimated_pages: Optional[int] = None,
        estimated_exercises: Optional[int] = None,
        estimated_time_minutes: Optional[int] = None
    ) -> str:
        """Create a content mapping.
        
        All fields except topic_id and textbook_id are optional.
        
        Args:
            topic_id: Curriculum topic ID (required)
            textbook_id: Textbook ID (required)
            start_page: Starting page (optional)
            end_page: Ending page (optional)
            exercise_references: Opaque teacher-authored string (optional)
            estimated_pages: Estimated page count (optional)
            estimated_exercises: Estimated exercise count (optional)
            estimated_time_minutes: Estimated time in minutes (optional)
        
        Returns:
            mapping_id: Generated UUID for the content mapping
        """
        mapping_id = str(uuid.uuid4())
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO content_mappings (
                    id, topic_id, textbook_id, start_page, end_page,
                    exercise_references, estimated_pages, estimated_exercises,
                    estimated_time_minutes
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                mapping_id, topic_id, textbook_id, start_page, end_page,
                exercise_references, estimated_pages, estimated_exercises,
                estimated_time_minutes
            ))
        
        return mapping_id
    
    def get_content_mapping(self, mapping_id: str) -> Optional[dict]:
        """Get content mapping by ID.
        
        Args:
            mapping_id: Content mapping ID
        
        Returns:
            Content mapping dict or None if not found
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, topic_id, textbook_id, start_page, end_page,
                       exercise_references, estimated_pages, estimated_exercises,
                       estimated_time_minutes
                FROM content_mappings
                WHERE id = ?
            """, (mapping_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def list_content_mappings(
        self,
        topic_id: Optional[str] = None,
        textbook_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List content mappings filtered by topic or textbook.
        
        Args:
            topic_id: Filter by topic ID (optional)
            textbook_id: Filter by textbook ID (optional)
        
        Returns:
            List of content mapping dicts
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            if topic_id and textbook_id:
                cursor.execute("""
                    SELECT id, topic_id, textbook_id, start_page, end_page,
                           exercise_references, estimated_pages, estimated_exercises,
                           estimated_time_minutes
                    FROM content_mappings
                    WHERE topic_id = ? AND textbook_id = ?
                """, (topic_id, textbook_id))
            elif topic_id:
                cursor.execute("""
                    SELECT id, topic_id, textbook_id, start_page, end_page,
                           exercise_references, estimated_pages, estimated_exercises,
                           estimated_time_minutes
                    FROM content_mappings
                    WHERE topic_id = ?
                """, (topic_id,))
            elif textbook_id:
                cursor.execute("""
                    SELECT id, topic_id, textbook_id, start_page, end_page,
                           exercise_references, estimated_pages, estimated_exercises,
                           estimated_time_minutes
                    FROM content_mappings
                    WHERE textbook_id = ?
                """, (textbook_id,))
            else:
                cursor.execute("""
                    SELECT id, topic_id, textbook_id, start_page, end_page,
                           exercise_references, estimated_pages, estimated_exercises,
                           estimated_time_minutes
                    FROM content_mappings
                """)
            
            return [dict(row) for row in cursor.fetchall()]
    
    def update_content_mapping(
        self,
        mapping_id: str,
        start_page: Optional[int] = None,
        end_page: Optional[int] = None,
        exercise_references: Optional[str] = None,
        estimated_pages: Optional[int] = None,
        estimated_exercises: Optional[int] = None,
        estimated_time_minutes: Optional[int] = None
    ) -> bool:
        """Update content mapping fields.
        
        Args:
            mapping_id: Content mapping ID
            start_page: New starting page (optional)
            end_page: New ending page (optional)
            exercise_references: New exercise references (optional)
            estimated_pages: New estimated page count (optional)
            estimated_exercises: New estimated exercise count (optional)
            estimated_time_minutes: New estimated time (optional)
        
        Returns:
            True if updated, False if not found
        """
        updates = []
        params = []
        
        if start_page is not None:
            updates.append("start_page = ?")
            params.append(start_page)
        if end_page is not None:
            updates.append("end_page = ?")
            params.append(end_page)
        if exercise_references is not None:
            updates.append("exercise_references = ?")
            params.append(exercise_references)
        if estimated_pages is not None:
            updates.append("estimated_pages = ?")
            params.append(estimated_pages)
        if estimated_exercises is not None:
            updates.append("estimated_exercises = ?")
            params.append(estimated_exercises)
        if estimated_time_minutes is not None:
            updates.append("estimated_time_minutes = ?")
            params.append(estimated_time_minutes)
        
        if not updates:
            return False
        
        params.append(mapping_id)
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                UPDATE content_mappings
                SET {', '.join(updates)}
                WHERE id = ?
            """, params)
            return cursor.rowcount > 0
    
    def delete_content_mapping(self, mapping_id: str) -> bool:
        """Delete a content mapping.
        
        Deletion does not affect lesson plans.
        
        Args:
            mapping_id: Content mapping ID
        
        Returns:
            True if deleted, False if not found
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM content_mappings WHERE id = ?", (mapping_id,))
            return cursor.rowcount > 0
