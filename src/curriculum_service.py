"""Curriculum service for read-only access and ingestion."""
import uuid
from typing import Optional, Dict, Any, List
from src.database import DatabaseService


class CurriculumService:
    """Service for curriculum structure management (read-only + ingestion)."""
    
    def __init__(self, db_service: DatabaseService):
        """Initialize curriculum service.
        
        Args:
            db_service: Database service instance
        """
        self.db = db_service
    
    def load_curriculum(
        self,
        school_id: str,
        grade_id: str,
        subject_id: str,
        curriculum_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Load curriculum structure from official or national standards.
        
        This is used for initial curriculum ingestion only.
        Curriculum data is treated as reference material, not enforcement rules.
        
        Args:
            school_id: ID of the school
            grade_id: ID of the grade
            subject_id: ID of the subject
            curriculum_data: Curriculum structure with units and topics
                Format: {
                    "units": [
                        {
                            "name": str,
                            "description": str (optional),
                            "sequence_order": int (optional),
                            "topics": [
                                {
                                    "name": str,
                                    "description": str (optional),
                                    "sequence_order": int (optional),
                                    "estimated_weeks": int (optional)
                                }
                            ]
                        }
                    ]
                }
        
        Returns:
            Summary of loaded curriculum with unit and topic IDs
        """
        loaded_units = []
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            for unit_data in curriculum_data.get("units", []):
                # Create unit
                unit_id = str(uuid.uuid4())
                cursor.execute("""
                    INSERT INTO curriculum_units (
                        id, school_id, grade_id, subject_id, name, description, sequence_order
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    unit_id,
                    school_id,
                    grade_id,
                    subject_id,
                    unit_data["name"],
                    unit_data.get("description"),
                    unit_data.get("sequence_order")
                ))
                
                # Create topics for this unit
                loaded_topics = []
                for topic_data in unit_data.get("topics", []):
                    topic_id = str(uuid.uuid4())
                    cursor.execute("""
                        INSERT INTO curriculum_topics (
                            id, unit_id, name, description, sequence_order, estimated_weeks
                        ) VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        topic_id,
                        unit_id,
                        topic_data["name"],
                        topic_data.get("description"),
                        topic_data.get("sequence_order"),
                        topic_data.get("estimated_weeks", 1)
                    ))
                    
                    loaded_topics.append({
                        "id": topic_id,
                        "name": topic_data["name"]
                    })
                
                loaded_units.append({
                    "id": unit_id,
                    "name": unit_data["name"],
                    "topics": loaded_topics
                })
        
        return {
            "school_id": school_id,
            "grade_id": grade_id,
            "subject_id": subject_id,
            "units_loaded": len(loaded_units),
            "units": loaded_units
        }
    
    def get_unit(self, unit_id: str) -> Optional[Dict[str, Any]]:
        """Get a curriculum unit by ID.
        
        Args:
            unit_id: ID of the unit
            
        Returns:
            Unit dictionary or None if not found
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM curriculum_units WHERE id = ?
            """, (unit_id,))
            row = cursor.fetchone()
            
            if row:
                return dict(row)
            return None
    
    def list_units(
        self,
        school_id: str,
        grade_id: str,
        subject_id: str
    ) -> List[Dict[str, Any]]:
        """List curriculum units for a specific school, grade, and subject.
        
        Args:
            school_id: ID of the school
            grade_id: ID of the grade
            subject_id: ID of the subject
            
        Returns:
            List of unit dictionaries, ordered by sequence_order
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM curriculum_units
                WHERE school_id = ? AND grade_id = ? AND subject_id = ?
                ORDER BY sequence_order, name
            """, (school_id, grade_id, subject_id))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_topic(self, topic_id: str) -> Optional[Dict[str, Any]]:
        """Get a curriculum topic by ID.
        
        Args:
            topic_id: ID of the topic
            
        Returns:
            Topic dictionary or None if not found
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM curriculum_topics WHERE id = ?
            """, (topic_id,))
            row = cursor.fetchone()
            
            if row:
                return dict(row)
            return None
    
    def list_topics(self, unit_id: str) -> List[Dict[str, Any]]:
        """List curriculum topics for a specific unit.
        
        Args:
            unit_id: ID of the unit
            
        Returns:
            List of topic dictionaries, ordered by sequence_order
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM curriculum_topics
                WHERE unit_id = ?
                ORDER BY sequence_order, name
            """, (unit_id,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_curriculum_structure(
        self,
        school_id: str,
        grade_id: str,
        subject_id: str
    ) -> Dict[str, Any]:
        """Get complete curriculum hierarchy for a school, grade, and subject.
        
        Returns units with nested topics.
        
        Args:
            school_id: ID of the school
            grade_id: ID of the grade
            subject_id: ID of the subject
            
        Returns:
            Complete curriculum hierarchy dictionary
        """
        units = self.list_units(school_id, grade_id, subject_id)
        
        curriculum_structure = []
        for unit in units:
            topics = self.list_topics(unit["id"])
            curriculum_structure.append({
                **unit,
                "topics": topics
            })
        
        return {
            "school_id": school_id,
            "grade_id": grade_id,
            "subject_id": subject_id,
            "units": curriculum_structure
        }
