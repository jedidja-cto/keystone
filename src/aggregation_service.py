"""Aggregation service for calculating averages and generating export summaries."""
from typing import Optional, Dict, Any, List
from src.database import DatabaseService


class AggregationService:
    """Service for calculating class and student averages."""
    
    def __init__(self, db_service: DatabaseService):
        """Initialize aggregation service.
        
        Args:
            db_service: Database service instance
        """
        self.db = db_service
    
    def calculate_class_average(self, assessment_id: str) -> Optional[float]:
        """Calculate the average mark for a class on an assessment.
        
        Args:
            assessment_id: ID of the assessment
            
        Returns:
            Average mark or None if no marks exist
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT AVG(value) as average
                FROM assessment_marks
                WHERE assessment_id = ?
            """, (assessment_id,))
            
            result = cursor.fetchone()
            return result['average'] if result['average'] is not None else None
    
    def calculate_student_average(
        self,
        student_id: str,
        class_id: str,
        subject_id: str
    ) -> Optional[float]:
        """Calculate the average mark for a student in a class/subject.
        
        Args:
            student_id: ID of the student
            class_id: ID of the class
            subject_id: ID of the subject
            
        Returns:
            Average mark or None if no marks exist
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT AVG(am.value) as average
                FROM assessment_marks am
                JOIN assessments a ON am.assessment_id = a.id
                WHERE am.student_id = ?
                  AND a.class_id = ?
                  AND a.subject_id = ?
            """, (student_id, class_id, subject_id))
            
            result = cursor.fetchone()
            return result['average'] if result['average'] is not None else None
    
    def generate_export_summary(
        self,
        class_id: str,
        subject_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate an export summary for a class and subject.
        
        Args:
            class_id: ID of the class
            subject_id: ID of the subject
            start_date: Optional start date filter (ISO 8601)
            end_date: Optional end date filter (ISO 8601)
            
        Returns:
            Export summary dictionary
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get class metadata
            cursor.execute("""
                SELECT c.id, c.name, c.school_id, g.name as grade_name
                FROM classes c
                JOIN grades g ON c.grade_id = g.id
                WHERE c.id = ?
            """, (class_id,))
            class_data = cursor.fetchone()
            
            # Get subject metadata
            cursor.execute("""
                SELECT id, name, description
                FROM subjects
                WHERE id = ?
            """, (subject_id,))
            subject_data = cursor.fetchone()
            
            # Build assessment query with optional date filters
            assessment_conditions = ["class_id = ?", "subject_id = ?"]
            assessment_params = [class_id, subject_id]
            
            if start_date:
                assessment_conditions.append("date >= ?")
                assessment_params.append(start_date)
            if end_date:
                assessment_conditions.append("date <= ?")
                assessment_params.append(end_date)
            
            assessment_where = " AND ".join(assessment_conditions)
            
            # Get assessments
            cursor.execute(f"""
                SELECT id, name, date, maximum_marks
                FROM assessments
                WHERE {assessment_where}
                ORDER BY date
            """, assessment_params)
            assessments = cursor.fetchall()
            
            # Build assessment list with class averages
            assessment_list = []
            for assessment in assessments:
                class_avg = self.calculate_class_average(assessment['id'])
                assessment_list.append({
                    'id': assessment['id'],
                    'name': assessment['name'],
                    'date': assessment['date'],
                    'maximum_marks': assessment['maximum_marks'],
                    'class_average': class_avg
                })
            
            # Get students enrolled in the class
            cursor.execute("""
                SELECT s.id, s.first_name, s.last_name
                FROM students s
                JOIN student_classes sc ON s.id = sc.student_id
                WHERE sc.class_id = ?
                ORDER BY s.last_name, s.first_name
            """, (class_id,))
            students = cursor.fetchall()
            
            # Build student list with averages and marks
            student_list = []
            for student in students:
                student_avg = self.calculate_student_average(
                    student['id'], class_id, subject_id
                )
                
                # Get marks for this student
                marks = []
                for assessment in assessments:
                    cursor.execute("""
                        SELECT value
                        FROM assessment_marks
                        WHERE assessment_id = ? AND student_id = ?
                    """, (assessment['id'], student['id']))
                    mark_row = cursor.fetchone()
                    
                    if mark_row:
                        marks.append({
                            'assessment_id': assessment['id'],
                            'value': mark_row['value']
                        })
                
                student_list.append({
                    'id': student['id'],
                    'first_name': student['first_name'],
                    'last_name': student['last_name'],
                    'student_average': student_avg,
                    'marks': marks
                })
            
            return {
                'class_metadata': dict(class_data) if class_data else None,
                'subject_metadata': dict(subject_data) if subject_data else None,
                'assessments': assessment_list,
                'students': student_list
            }
