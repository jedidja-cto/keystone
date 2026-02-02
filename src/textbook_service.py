"""Textbook service for Phase 3 content mapping."""
import uuid
from typing import Optional, List, Dict, Any
from src.database import DatabaseService


class TextbookService:
    """Manages textbook registration (optional reference material)."""
    
    def __init__(self, db: DatabaseService):
        """Initialize textbook service.
        
        Args:
            db: Database service instance
        """
        self.db = db
    
    def register_textbook(
        self,
        subject_id: str,
        title: str,
        edition: Optional[str] = None,
        publisher: Optional[str] = None,
        isbn: Optional[str] = None,
        publication_year: Optional[int] = None
    ) -> str:
        """Register a textbook (optional reference material).
        
        Args:
            subject_id: Subject this textbook is for
            title: Textbook title (required)
            edition: Edition (optional)
            publisher: Publisher name (optional)
            isbn: ISBN (optional)
            publication_year: Publication year (optional)
        
        Returns:
            textbook_id: Generated UUID for the textbook
        """
        textbook_id = str(uuid.uuid4())
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO textbooks (
                    id, subject_id, title, edition, publisher, isbn, publication_year
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (textbook_id, subject_id, title, edition, publisher, isbn, publication_year))
        
        return textbook_id
    
    def get_textbook(self, textbook_id: str) -> Optional[dict]:
        """Get textbook by ID.
        
        Args:
            textbook_id: Textbook ID
        
        Returns:
            Textbook dict or None if not found
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, subject_id, title, edition, publisher, isbn, publication_year
                FROM textbooks
                WHERE id = ?
            """, (textbook_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def list_textbooks(self, subject_id: str) -> List[Dict[str, Any]]:
        """List all textbooks for a subject.
        
        Args:
            subject_id: Subject ID
        
        Returns:
            List of textbook dicts
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, subject_id, title, edition, publisher, isbn, publication_year
                FROM textbooks
                WHERE subject_id = ?
                ORDER BY title, edition
            """, (subject_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    def update_textbook(
        self,
        textbook_id: str,
        title: Optional[str] = None,
        edition: Optional[str] = None,
        publisher: Optional[str] = None,
        isbn: Optional[str] = None,
        publication_year: Optional[int] = None
    ) -> bool:
        """Update textbook fields.
        
        Args:
            textbook_id: Textbook ID
            title: New title (optional)
            edition: New edition (optional)
            publisher: New publisher (optional)
            isbn: New ISBN (optional)
            publication_year: New publication year (optional)
        
        Returns:
            True if updated, False if not found
        """
        updates = []
        params = []
        
        if title is not None:
            updates.append("title = ?")
            params.append(title)
        if edition is not None:
            updates.append("edition = ?")
            params.append(edition)
        if publisher is not None:
            updates.append("publisher = ?")
            params.append(publisher)
        if isbn is not None:
            updates.append("isbn = ?")
            params.append(isbn)
        if publication_year is not None:
            updates.append("publication_year = ?")
            params.append(publication_year)
        
        if not updates:
            return False
        
        params.append(textbook_id)
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                UPDATE textbooks
                SET {', '.join(updates)}
                WHERE id = ?
            """, params)
            return cursor.rowcount > 0
    
    def delete_textbook(self, textbook_id: str) -> bool:
        """Delete a textbook.
        
        Deletion removes content mappings but does not affect lesson plans.
        
        Args:
            textbook_id: Textbook ID
        
        Returns:
            True if deleted, False if not found
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM textbooks WHERE id = ?", (textbook_id,))
            return cursor.rowcount > 0
