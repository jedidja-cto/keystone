"""Service for bulk importing data via CSV files."""
import csv
import io
from typing import List, Dict, Any, Optional
from src.database import DatabaseService


class ImportService:
    """Handles bulk data ingestion while maintaining constitutional guardrails."""

    def __init__(self, db_service: DatabaseService):
        """Initialize service.
        
        Args:
            db_service: Database service instance
        """
        self.db = db_service

    def import_students(self, school_id: str, csv_data: str) -> Dict[str, Any]:
        """Import student roster from CSV.
        
        Expected columns: first_name, last_name, grade_id, enrollment_status (optional)
        
        Returns:
            Dict with success count and any error messages
        """
        f = io.StringIO(csv_data)
        reader = csv.DictReader(f)
        
        success = 0
        errors = []
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            for row in reader:
                try:
                    student_id = row.get('id') or str(DatabaseService.generate_id())
                    first_name = row.get('first_name')
                    last_name = row.get('last_name')
                    grade_id = row.get('grade_id')
                    status = row.get('enrollment_status', 'active')
                    
                    if not all([first_name, last_name, grade_id]):
                        errors.append(f"Missing required fields for row {row}")
                        continue
                        
                    cursor.execute("""
                        INSERT INTO students (id, school_id, first_name, last_name, enrollment_status)
                        VALUES (?, ?, ?, ?, ?)
                    """, (student_id, school_id, first_name, last_name, status))
                    
                    # Note: We don't know the grade mapping here, so user should provide grade_id
                    # Future improvement: Lookup grade_id by name within school
                    
                    success += 1
                except Exception as e:
                    errors.append(f"Error importing {row}: {str(e)}")
                    
        return {"success_count": success, "errors": errors}

    def import_curriculum(self, school_id: str, grade_id: str, subject_id: str, csv_data: str) -> Dict[str, Any]:
        """Import curriculum units and topics.
        
        Expected columns: unit_name, topic_name, topic_order (optional), topic_weeks (optional)
        
        Returns:
            Dict with metrics
        """
        f = io.StringIO(csv_data)
        reader = csv.DictReader(f)
        
        units_created = {} # name -> id
        topics_count = 0
        errors = []
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            for row in reader:
                try:
                    u_name = row.get('unit_name')
                    t_name = row.get('topic_name')
                    t_order = int(row.get('topic_order', 0))
                    t_weeks = int(row.get('topic_weeks', 1))
                    
                    if not all([u_name, t_name]):
                        continue

                    # 1. Ensure Unit exists
                    if u_name not in units_created:
                        # Check if already in DB
                        cursor.execute("SELECT id FROM curriculum_units WHERE school_id=? AND grade_id=? AND subject_id=? AND name=?",
                                      (school_id, grade_id, subject_id, u_name))
                        res = cursor.fetchone()
                        if res:
                            u_id = res['id']
                        else:
                            u_id = str(DatabaseService.generate_id())
                            cursor.execute("""
                                INSERT INTO curriculum_units (id, school_id, grade_id, subject_id, name)
                                VALUES (?, ?, ?, ?, ?)
                            """, (u_id, school_id, grade_id, subject_id, u_name))
                        units_created[u_name] = u_id
                    
                    # 2. Add Topic
                    t_id = str(DatabaseService.generate_id())
                    cursor.execute("""
                        INSERT INTO curriculum_topics (id, unit_id, name, sequence_order, estimated_weeks)
                        VALUES (?, ?, ?, ?, ?)
                    """, (t_id, units_created[u_name], t_name, t_order, t_weeks))
                    topics_count += 1
                    
                except Exception as e:
                    errors.append(str(e))
                    
        return {
            "units_imported": len(units_created),
            "topics_imported": topics_count,
            "errors": errors
        }
