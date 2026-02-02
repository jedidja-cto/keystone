from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any, Optional
from src.database import DatabaseService
from src.lesson_plan_service import LessonPlanService
from src.aggregation_service import AggregationService
from src.report_generation_service import ReportGenerationService
from src.qualitative_observation_service import QualitativeObservationService
from src.import_service import ImportService

app = FastAPI(title="Keystone API", description="Operational Backend for Keystone Web App")

# Enable CORS for Next.js
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the Next.js URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Shared Database Dependency
def get_db():
    import os
    db_path = os.getenv("DB_PATH", "keystone.db")
    return DatabaseService(db_path)

@app.get("/health")
def health_check():
    return {"status": "operational", "version": "1.0.0"}

@app.get("/dashboard/stats")
def get_dashboard_stats(db: DatabaseService = Depends(get_db)):
    """Fetch high-level metrics for the dashboard."""
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM students")
        students = cursor.fetchone()['count']
        cursor.execute("SELECT COUNT(*) as count FROM classes")
        classes = cursor.fetchone()['count']
        cursor.execute("SELECT COUNT(*) as count FROM lesson_plans")
        plans = cursor.fetchone()['count']
        
    return {
        "total_students": students,
        "total_classes": classes,
        "active_plans": plans,
        "recent_alerts": []
    }

@app.get("/classes")
def list_classes(db: DatabaseService = Depends(get_db)):
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM classes")
        return cursor.fetchall()

@app.get("/terms")
def list_terms(db: DatabaseService = Depends(get_db)):
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, start_date, end_date FROM terms")
        return cursor.fetchall()

@app.get("/reports/student/{student_id}/{term_id}")
def generate_report(student_id: str, term_id: str, db: DatabaseService = Depends(get_db)):
    reporter = ReportGenerationService(db)
    try:
        return reporter.generate_student_progress_report(student_id, term_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/marks")
def log_mark(mark_data: Dict[str, Any], db: DatabaseService = Depends(get_db)):
    """Log a student assessment mark."""
    from src.assessment_mark_service import AssessmentMarkService
    service = AssessmentMarkService(db)
    try:
        # Expected mark_data: {student_id, assessment_id, value}
        return service.create_mark(
            mark_data['student_id'],
            mark_data['assessment_id'],
            mark_data['value']
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
