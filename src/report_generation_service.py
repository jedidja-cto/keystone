"""Service for generating student progress reports."""
from typing import List, Dict, Any, Optional
from src.database import DatabaseService
from src.aggregation_service import AggregationService
from src.qualitative_observation_service import QualitativeObservationService


class ReportGenerationService:
    """Unifies quantitative and qualitative data for student reporting."""
    
    def __init__(self, db_service: DatabaseService):
        """Initialize service.
        
        Args:
            db_service: Database service instance
        """
        self.db = db_service
        self.aggregation = AggregationService(db_service)
        self.observations = QualitativeObservationService(db_service)

    def generate_student_progress_report(
        self,
        student_id: str,
        term_id: str
    ) -> Dict[str, Any]:
        """Generate a structured progress report for a student for a specific term.
        
        Args:
            student_id: ID of the student
            term_id: ID of the academic term
            
        Returns:
            Dictionary containing student performance and observations
        """
        reportable_categories = ('Academic', 'Social')
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # 1. Get Student Metadata with Grade
            cursor.execute("""
                SELECT s.first_name, s.last_name, g.name as grade_name
                FROM students s
                LEFT JOIN student_classes sc ON s.id = sc.student_id
                LEFT JOIN classes c ON sc.class_id = c.id
                LEFT JOIN grades g ON c.grade_id = g.id
                WHERE s.id = ?
                LIMIT 1
            """, (student_id,))
            student_row = cursor.fetchone()
            if not student_row:
                raise ValueError(f"Student {student_id} not found")

            # 2. Get Term Information
            cursor.execute("""
                SELECT name, start_date, end_date
                FROM terms
                WHERE id = ?
            """, (term_id,))
            term_row = cursor.fetchone()
            if not term_row:
                raise ValueError(f"Term {term_id} not found")
                
            term_start = term_row['start_date']
            term_end = term_row['end_date']

            # 3. Get all observations first (efficiently)
            term_obs = self.observations.list_observations(
                student_id=student_id,
                start_date=term_start,
                end_date=term_end
            )
            
            # Filter reportable observations once
            reportable_obs = [o for o in term_obs if o['category'] in reportable_categories]

            # 4. Get Classes student is enrolled in
            cursor.execute("""
                SELECT c.id, c.name
                FROM classes c
                JOIN student_classes sc ON c.id = sc.class_id
                WHERE sc.student_id = ?
            """, (student_id,))
            classes = cursor.fetchall()

            subject_summaries = []
            
            for cls in classes:
                class_id = cls['id']
                
                # Get subjects for this class
                cursor.execute("""
                    SELECT s.id, s.name
                    FROM subjects s
                    JOIN class_subjects cs ON s.id = cs.subject_id
                    WHERE cs.class_id = ?
                """, (class_id,))
                subjects = cursor.fetchall()
                
                for subj in subjects:
                    subject_id = subj['id']
                    
                    # Term-aware student average
                    cursor.execute("""
                        SELECT AVG(am.value) as average
                        FROM assessment_marks am
                        JOIN assessments a ON am.assessment_id = a.id
                        WHERE am.student_id = ?
                          AND a.class_id = ?
                          AND a.subject_id = ?
                          AND a.date >= ?
                          AND a.date <= ?
                    """, (student_id, class_id, subject_id, term_start, term_end))
                    row = cursor.fetchone()
                    term_student_avg = row['average'] if row else None
                    
                    # Term-aware class average
                    cursor.execute("""
                        SELECT AVG(am.value) as average
                        FROM assessment_marks am
                        JOIN assessments a ON am.assessment_id = a.id
                        WHERE a.class_id = ?
                          AND a.subject_id = ?
                          AND a.date >= ?
                          AND a.date <= ?
                    """, (class_id, subject_id, term_start, term_end))
                    row = cursor.fetchone()
                    term_class_avg = row['average'] if row else None

                    # Subject-specific observations
                    subj_obs = [
                        {
                            'date': o['date'],
                            'category': o['category'],
                            'text': o['observation_text'],
                            'intensity': o['intensity']
                        }
                        for o in reportable_obs if o['subject_id'] == subject_id
                    ]

                    subject_summaries.append({
                        'subject_name': subj['name'],
                        'class_name': cls['name'],
                        'student_average': term_student_avg,
                        'class_average': term_class_avg,
                        'observations': subj_obs
                    })

            # Overall observations (no subject linked)
            overall_obs = [
                {
                    'date': o['date'],
                    'category': o['category'],
                    'text': o['observation_text'],
                    'intensity': o['intensity']
                }
                for o in reportable_obs if o['subject_id'] is None
            ]

            return {
                'student_info': {
                    'first_name': student_row['first_name'],
                    'last_name': student_row['last_name'],
                    'grade': student_row['grade_name']
                },
                'term_info': {
                    'name': term_row['name'],
                    'start_date': term_start,
                    'end_date': term_end
                },
                'subject_summaries': subject_summaries,
                'overall_observations': overall_obs
            }

    def list_student_reports_for_class(
        self,
        class_id: str,
        term_id: str
    ) -> List[Dict[str, Any]]:
        """List progress reports for all students in a class.
        
        Args:
            class_id: ID of the class
            term_id: ID of the term
            
        Returns:
            List of report dictionaries
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT student_id
                FROM student_classes
                WHERE class_id = ?
            """, (class_id,))
            student_ids = [row['student_id'] for row in cursor.fetchall()]

        return [self.generate_student_progress_report(sid, term_id) for sid in student_ids]

    def batch_export_reports(
        self,
        class_id: str,
        term_id: str,
        output_dir: str
    ) -> Dict[str, Any]:
        """Export all reports for a class as individual text files.
        
        Args:
            class_id: ID of the class
            term_id: ID of the term
            output_dir: Directory to save reports
            
        Returns:
            Dict with export summary
        """
        import os
        import json
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        reports = self.list_student_reports_for_class(class_id, term_id)
        
        exported = 0
        for r in reports:
            st = r['student_info']
            filename = f"report_{st['last_name']}_{st['first_name']}.txt".lower().replace(" ", "_")
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, 'w') as f:
                f.write(f"PROGESS REPORT: {st['first_name']} {st['last_name']}\n")
                f.write(f"Grade: {st['grade']}\n")
                f.write(f"Term: {r['term_info']['name']} ({r['term_info']['start_date']} to {r['term_info']['end_date']})\n")
                f.write("-" * 40 + "\n\n")
                
                f.write("--- SUBJECT SUMMARIES ---\n")
                for s in r['subject_summaries']:
                    avg = f"{s['student_average']:.1f}%" if s['student_average'] is not None else "N/A"
                    cls_avg = f"{s['class_average']:.1f}%" if s['class_average'] is not None else "N/A"
                    f.write(f"\n{s['subject_name']} (Class: {s['class_name']})\n")
                    f.write(f"  Student Average: {avg}\n")
                    f.write(f"  Class Average: {cls_avg}\n")
                    if s['observations']:
                        f.write("  Observations:\n")
                        for o in s['observations']:
                            f.write(f"    - [{o['date']}] {o['text']}\n")
                
                if r['overall_observations']:
                    f.write("\n--- OVERALL OBSERVATIONS ---\n")
                    for o in r['overall_observations']:
                        f.write(f"  - [{o['date']}] {o['text']}\n")
            
            exported += 1
            
        return {"reports_exported": exported, "directory": output_dir}
