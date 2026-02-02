"""Database service for Keystone Phase 0, Phase 1, Phase 2, and Phase 3."""
import sqlite3
import uuid
from typing import Any, Optional
from contextlib import contextmanager


class DatabaseService:
    """Manages SQLite database connection and operations."""

    @staticmethod
    def generate_id() -> str:
        """Generate a unique identifier."""
        return str(uuid.uuid4())

    def __init__(self, db_path: str = "keystone.db"):
        """Initialize database service.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._persistent_conn = None
        
        # For in-memory databases, keep a persistent connection
        if db_path == ":memory:":
            self._persistent_conn = sqlite3.connect(db_path)
            self._persistent_conn.row_factory = sqlite3.Row
            self._persistent_conn.execute("PRAGMA foreign_keys = ON")
        
        self._initialize_schema()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections."""
        if self._persistent_conn:
            # Use persistent connection for in-memory databases
            try:
                yield self._persistent_conn
                self._persistent_conn.commit()
            except Exception:
                self._persistent_conn.rollback()
                raise
        else:
            # Use new connection for file databases
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON")
            try:
                yield conn
                conn.commit()
            except Exception:
                conn.rollback()
                raise
            finally:
                conn.close()
    
    def _initialize_schema(self):
        """Create all tables if they don't exist."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Phase 0: Schools
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS schools (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    contact_info TEXT
                )
            """)
            
            # Phase 0: Grades
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS grades (
                    id TEXT PRIMARY KEY,
                    school_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    ordinal INTEGER,
                    FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE CASCADE,
                    UNIQUE(school_id, name)
                )
            """)
            
            # Phase 0: Teachers
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS teachers (
                    id TEXT PRIMARY KEY,
                    school_id TEXT NOT NULL,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE CASCADE
                )
            """)
            
            # Phase 0: Students
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS students (
                    id TEXT PRIMARY KEY,
                    school_id TEXT NOT NULL,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    enrollment_status TEXT NOT NULL,
                    FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE CASCADE
                )
            """)
            
            # Phase 0: Subjects
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS subjects (
                    id TEXT PRIMARY KEY,
                    school_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE CASCADE,
                    UNIQUE(school_id, name)
                )
            """)
            
            # Phase 0: Classes
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS classes (
                    id TEXT PRIMARY KEY,
                    school_id TEXT NOT NULL,
                    grade_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE CASCADE,
                    FOREIGN KEY (grade_id) REFERENCES grades(id) ON DELETE CASCADE
                )
            """)
            
            # Phase 0: Student-Class enrollment
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS student_classes (
                    student_id TEXT NOT NULL,
                    class_id TEXT NOT NULL,
                    PRIMARY KEY (student_id, class_id),
                    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
                    FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE
                )
            """)
            
            # Phase 0: Teacher-Class assignment
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS teacher_classes (
                    teacher_id TEXT NOT NULL,
                    class_id TEXT NOT NULL,
                    PRIMARY KEY (teacher_id, class_id),
                    FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE CASCADE,
                    FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE
                )
            """)
            
            # Phase 0: Class-Subject mapping
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS class_subjects (
                    class_id TEXT NOT NULL,
                    subject_id TEXT NOT NULL,
                    PRIMARY KEY (class_id, subject_id),
                    FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE,
                    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE
                )
            """)
            
            # Phase 0: Terms
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS terms (
                    id TEXT PRIMARY KEY,
                    school_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    start_date TEXT NOT NULL,
                    end_date TEXT NOT NULL,
                    FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE CASCADE,
                    CHECK (start_date < end_date)
                )
            """)
            
            # Phase 0: Teaching Days
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS teaching_days (
                    id TEXT PRIMARY KEY,
                    school_id TEXT NOT NULL,
                    date TEXT NOT NULL,
                    FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE CASCADE,
                    UNIQUE(school_id, date)
                )
            """)
            
            # Phase 0: Holidays
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS holidays (
                    id TEXT PRIMARY KEY,
                    school_id TEXT NOT NULL,
                    date TEXT NOT NULL,
                    description TEXT NOT NULL,
                    FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE CASCADE,
                    UNIQUE(school_id, date)
                )
            """)
            
            # Phase 0: Exam Periods
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS exam_periods (
                    id TEXT PRIMARY KEY,
                    school_id TEXT NOT NULL,
                    start_date TEXT NOT NULL,
                    end_date TEXT NOT NULL,
                    FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE CASCADE,
                    CHECK (start_date < end_date)
                )
            """)
            
            # Phase 1: Lesson Plans
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS lesson_plans (
                    id TEXT PRIMARY KEY,
                    teacher_id TEXT NOT NULL,
                    class_id TEXT NOT NULL,
                    subject_id TEXT NOT NULL,
                    start_date TEXT,
                    end_date TEXT,
                    instructional_notes TEXT,
                    topic TEXT,
                    reference_materials TEXT,
                    duration TEXT,
                    status TEXT NOT NULL CHECK (status IN ('draft', 'finalized')),
                    FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE RESTRICT,
                    FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE,
                    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE
                )
            """)
            
            # Phase 1: Assessments
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS assessments (
                    id TEXT PRIMARY KEY,
                    teacher_id TEXT NOT NULL,
                    class_id TEXT NOT NULL,
                    subject_id TEXT NOT NULL,
                    date TEXT NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    maximum_marks REAL,
                    FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE RESTRICT,
                    FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE,
                    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE
                )
            """)
            
            # Phase 1: Assessment Marks
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS assessment_marks (
                    id TEXT PRIMARY KEY,
                    assessment_id TEXT NOT NULL,
                    student_id TEXT NOT NULL,
                    value REAL NOT NULL CHECK (value >= 0),
                    FOREIGN KEY (assessment_id) REFERENCES assessments(id) ON DELETE CASCADE,
                    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
                    UNIQUE(assessment_id, student_id)
                )
            """)
            
            # Phase 2: Curriculum Units
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS curriculum_units (
                    id TEXT PRIMARY KEY,
                    school_id TEXT NOT NULL,
                    grade_id TEXT NOT NULL,
                    subject_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    sequence_order INTEGER,
                    FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE CASCADE,
                    FOREIGN KEY (grade_id) REFERENCES grades(id) ON DELETE CASCADE,
                    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
                    UNIQUE(school_id, grade_id, subject_id, name)
                )
            """)
            
            # Phase 2: Curriculum Topics
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS curriculum_topics (
                    id TEXT PRIMARY KEY,
                    unit_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    sequence_order INTEGER,
                    estimated_weeks INTEGER,
                    FOREIGN KEY (unit_id) REFERENCES curriculum_units(id) ON DELETE CASCADE,
                    UNIQUE(unit_id, name)
                )
            """)
            
            # Phase 3: Textbooks
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS textbooks (
                    id TEXT PRIMARY KEY,
                    subject_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    edition TEXT,
                    publisher TEXT,
                    isbn TEXT,
                    publication_year INTEGER,
                    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE RESTRICT
                )
            """)
            
            # Phase 3: Content Mappings
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS content_mappings (
                    id TEXT PRIMARY KEY,
                    topic_id TEXT NOT NULL,
                    textbook_id TEXT NOT NULL,
                    start_page INTEGER,
                    end_page INTEGER,
                    exercise_references TEXT,
                    estimated_pages INTEGER,
                    estimated_exercises INTEGER,
                    estimated_time_minutes INTEGER,
                    FOREIGN KEY (topic_id) REFERENCES curriculum_topics(id) ON DELETE CASCADE,
                    FOREIGN KEY (textbook_id) REFERENCES textbooks(id) ON DELETE CASCADE
                )
            """)
            
            # Phase 3: Lesson Content Alignments
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS lesson_content_alignments (
                    lesson_plan_id TEXT NOT NULL,
                    content_mapping_id TEXT NOT NULL,
                    PRIMARY KEY (lesson_plan_id, content_mapping_id),
                    FOREIGN KEY (lesson_plan_id) REFERENCES lesson_plans(id) ON DELETE CASCADE,
                    FOREIGN KEY (content_mapping_id) REFERENCES content_mappings(id) ON DELETE CASCADE
                )
            """)

            # Phase 4: Qualitative Observations
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS qualitative_observations (
                    id TEXT PRIMARY KEY,
                    student_id TEXT NOT NULL,
                    teacher_id TEXT NOT NULL,
                    class_id TEXT,
                    subject_id TEXT,
                    date TEXT NOT NULL,
                    category TEXT NOT NULL,
                    observation_text TEXT NOT NULL,
                    intensity TEXT CHECK (intensity IN ('positive', 'neutral', 'concern')),
                    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
                    FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE RESTRICT,
                    FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE SET NULL,
                    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE SET NULL
                )
            """)
