"""Workload aggregation service for Phase 3."""
from typing import Dict, Any
from src.database import DatabaseService


class WorkloadAggregationService:
    """Aggregates workload estimates from content mappings (informational only)."""
    
    def __init__(self, db: DatabaseService):
        """Initialize workload aggregation service.
        
        Args:
            db: Database service instance
        """
        self.db = db
    
    def calculate_workload_for_period(
        self,
        class_id: str,
        subject_id: str,
        start_date: str,
        end_date: str
    ) -> Dict[str, Any]:
        """Calculate aggregated workload for a planning period.
        
        Only includes lessons with explicit content alignments.
        All values are informational only (no enforcement).
        
        Args:
            class_id: Class ID
            subject_id: Subject ID
            start_date: Period start date (ISO 8601)
            end_date: Period end date (ISO 8601)
        
        Returns:
            {
                "total_pages": int,
                "total_exercises": int,
                "total_time_minutes": int,
                "lesson_count": int,
                "aligned_lesson_count": int
            }
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get all lesson plans in period (read-only Phase 1 access)
            # Only include lessons with actual dates (drafts without dates are excluded from period calculations)
            cursor.execute("""
                SELECT id
                FROM lesson_plans
                WHERE class_id = ? AND subject_id = ?
                  AND start_date IS NOT NULL AND end_date IS NOT NULL
                  AND start_date >= ? AND end_date <= ?
            """, (class_id, subject_id, start_date, end_date))
            lesson_ids = [row['id'] for row in cursor.fetchall()]
            
            if not lesson_ids:
                return {
                    "total_pages": 0,
                    "total_exercises": 0,
                    "total_time_minutes": 0,
                    "lesson_count": 0,
                    "aligned_lesson_count": 0
                }
            
            # Get workload from aligned content mappings
            placeholders = ','.join('?' * len(lesson_ids))
            cursor.execute(f"""
                SELECT 
                    cm.estimated_pages,
                    cm.estimated_exercises,
                    cm.estimated_time_minutes,
                    lca.lesson_plan_id
                FROM content_mappings cm
                JOIN lesson_content_alignments lca ON cm.id = lca.content_mapping_id
                WHERE lca.lesson_plan_id IN ({placeholders})
            """, lesson_ids)
            
            total_pages = 0
            total_exercises = 0
            total_time_minutes = 0
            aligned_lessons = set()
            
            for row in cursor.fetchall():
                # Aggregate workload estimates (all optional)
                total_pages += row['estimated_pages'] or 0
                total_exercises += row['estimated_exercises'] or 0
                total_time_minutes += row['estimated_time_minutes'] or 0
                aligned_lessons.add(row['lesson_plan_id'])
            
            return {
                "total_pages": total_pages,
                "total_exercises": total_exercises,
                "total_time_minutes": total_time_minutes,
                "lesson_count": len(lesson_ids),
                "aligned_lesson_count": len(aligned_lessons)
            }
    
    def calculate_workload_for_topic(self, topic_id: str) -> Dict[str, Any]:
        """Calculate aggregated workload for a curriculum topic.
        
        Sums workload from all content mappings for the topic.
        All values are informational only (no enforcement).
        
        Args:
            topic_id: Curriculum topic ID
        
        Returns:
            {
                "total_pages": int,
                "total_exercises": int,
                "total_time_minutes": int,
                "mapping_count": int
            }
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get all content mappings for topic (read-only Phase 2 access)
            cursor.execute("""
                SELECT estimated_pages, estimated_exercises, estimated_time_minutes
                FROM content_mappings
                WHERE topic_id = ?
            """, (topic_id,))
            
            total_pages = 0
            total_exercises = 0
            total_time_minutes = 0
            mapping_count = 0
            
            for row in cursor.fetchall():
                # Aggregate workload estimates (all optional)
                total_pages += row['estimated_pages'] or 0
                total_exercises += row['estimated_exercises'] or 0
                total_time_minutes += row['estimated_time_minutes'] or 0
                mapping_count += 1
            
            return {
                "total_pages": total_pages,
                "total_exercises": total_exercises,
                "total_time_minutes": total_time_minutes,
                "mapping_count": mapping_count
            }
