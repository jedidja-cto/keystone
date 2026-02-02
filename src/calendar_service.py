"""Calendar service for teaching time calculations."""
from datetime import datetime, timedelta
from typing import List, Dict, Any
from src.database import DatabaseService


class CalendarService:
    """Service for calendar-aware planning calculations."""
    
    # Configurable constant (heuristic, not enforced policy)
    DAYS_PER_WEEK = 5
    
    def __init__(self, db_service: DatabaseService):
        """Initialize calendar service.
        
        Args:
            db_service: Database service instance
        """
        self.db = db_service
    
    def calculate_teaching_days(
        self,
        school_id: str,
        start_date: str,
        end_date: str
    ) -> List[str]:
        """Calculate available teaching days within a date range.
        
        Excludes holidays and exam periods.
        
        Args:
            school_id: ID of the school
            start_date: Start date (ISO 8601: YYYY-MM-DD)
            end_date: End date (ISO 8601: YYYY-MM-DD)
            
        Returns:
            List of teaching day dates (ISO 8601 format)
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get teaching days in range
            cursor.execute("""
                SELECT date FROM teaching_days
                WHERE school_id = ? AND date >= ? AND date <= ?
                ORDER BY date
            """, (school_id, start_date, end_date))
            teaching_days = {row["date"] for row in cursor.fetchall()}
            
            # Get holidays in range
            cursor.execute("""
                SELECT date FROM holidays
                WHERE school_id = ? AND date >= ? AND date <= ?
            """, (school_id, start_date, end_date))
            holidays = {row["date"] for row in cursor.fetchall()}
            
            # Get exam period dates
            cursor.execute("""
                SELECT start_date, end_date FROM exam_periods
                WHERE school_id = ?
                  AND NOT (end_date < ? OR start_date > ?)
            """, (school_id, start_date, end_date))
            
            exam_dates = set()
            for row in cursor.fetchall():
                # Generate all dates in exam period
                exam_start = datetime.fromisoformat(row["start_date"])
                exam_end = datetime.fromisoformat(row["end_date"])
                current = exam_start
                while current <= exam_end:
                    exam_dates.add(current.strftime("%Y-%m-%d"))
                    current += timedelta(days=1)
            
            # Calculate available teaching days
            available_days = teaching_days - holidays - exam_dates
            
            return sorted(list(available_days))
    
    def identify_lost_days(
        self,
        school_id: str,
        start_date: str,
        end_date: str
    ) -> List[Dict[str, str]]:
        """Identify lost teaching days within a date range.
        
        Args:
            school_id: ID of the school
            start_date: Start date (ISO 8601: YYYY-MM-DD)
            end_date: End date (ISO 8601: YYYY-MM-DD)
            
        Returns:
            List of lost day dictionaries with date and reason
        """
        lost_days = []
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get holidays
            cursor.execute("""
                SELECT date, description FROM holidays
                WHERE school_id = ? AND date >= ? AND date <= ?
                ORDER BY date
            """, (school_id, start_date, end_date))
            
            for row in cursor.fetchall():
                lost_days.append({
                    "date": row["date"],
                    "reason": "holiday",
                    "description": row["description"]
                })
            
            # Get exam periods
            cursor.execute("""
                SELECT start_date, end_date FROM exam_periods
                WHERE school_id = ?
                  AND NOT (end_date < ? OR start_date > ?)
                ORDER BY start_date
            """, (school_id, start_date, end_date))
            
            for row in cursor.fetchall():
                # Generate all dates in exam period
                exam_start = datetime.fromisoformat(row["start_date"])
                exam_end = datetime.fromisoformat(row["end_date"])
                current = exam_start
                while current <= exam_end:
                    date_str = current.strftime("%Y-%m-%d")
                    if start_date <= date_str <= end_date:
                        lost_days.append({
                            "date": date_str,
                            "reason": "exam_period",
                            "description": "Exam period"
                        })
                    current += timedelta(days=1)
        
        # Sort by date
        lost_days.sort(key=lambda x: x["date"])
        return lost_days
    
    def get_planning_window(
        self,
        school_id: str,
        start_date: str,
        end_date: str
    ) -> Dict[str, Any]:
        """Get planning window with available teaching time.
        
        Args:
            school_id: ID of the school
            start_date: Start date (ISO 8601: YYYY-MM-DD)
            end_date: End date (ISO 8601: YYYY-MM-DD)
            
        Returns:
            Planning window dictionary with available days, weeks, and lost days
        """
        teaching_days = self.calculate_teaching_days(school_id, start_date, end_date)
        lost_days = self.identify_lost_days(school_id, start_date, end_date)
        
        available_teaching_days = len(teaching_days)
        available_weeks = available_teaching_days // self.DAYS_PER_WEEK
        
        return {
            "start_date": start_date,
            "end_date": end_date,
            "available_teaching_days": available_teaching_days,
            "available_weeks": available_weeks,
            "lost_days": lost_days,
            "teaching_days": teaching_days
        }
