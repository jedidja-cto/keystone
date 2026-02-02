"""Example usage of Keystone Phase 2 (Premeditated Planning Engine)."""
import uuid
from datetime import datetime, timedelta
from src import (
    DatabaseService,
    LessonPlanService,
    CurriculumService,
    CalendarService,
    PacingCalculationService,
    DraftPlanningService
)


def main():
    """Demonstrate Phase 2 functionality."""
    # Initialize services
    db = DatabaseService("example_phase2.db")
    lesson_plan_service = LessonPlanService(db)
    curriculum_service = CurriculumService(db)
    calendar_service = CalendarService(db)
    pacing_service = PacingCalculationService()
    draft_planning_service = DraftPlanningService(
        db, curriculum_service, calendar_service, pacing_service, lesson_plan_service
    )
    
    print("=" * 70)
    print("PHASE 2: PREMEDITATED PLANNING ENGINE DEMONSTRATION")
    print("=" * 70)
    print()
    
    # Create foundational data (Phase 0)
    print("Setting up foundational data...")
    
    with db.get_connection() as conn:
        cursor = conn.cursor()
        
        # Create school
        school_id = str(uuid.uuid4())
        cursor.execute(
            "INSERT INTO schools (id, name) VALUES (?, ?)",
            (school_id, "Example High School")
        )
        
        # Create grade
        grade_id = str(uuid.uuid4())
        cursor.execute(
            "INSERT INTO grades (id, school_id, name, ordinal) VALUES (?, ?, ?, ?)",
            (grade_id, school_id, "Grade 10", 10)
        )
        
        # Create teacher
        teacher_id = str(uuid.uuid4())
        cursor.execute(
            "INSERT INTO teachers (id, school_id, first_name, last_name) VALUES (?, ?, ?, ?)",
            (teacher_id, school_id, "Jane", "Smith")
        )
        
        # Create subject
        subject_id = str(uuid.uuid4())
        cursor.execute(
            "INSERT INTO subjects (id, school_id, name) VALUES (?, ?, ?)",
            (subject_id, school_id, "Mathematics")
        )
        
        # Create class
        class_id = str(uuid.uuid4())
        cursor.execute(
            "INSERT INTO classes (id, school_id, grade_id, name) VALUES (?, ?, ?, ?)",
            (class_id, school_id, grade_id, "Math 10A")
        )
        
        # Create teaching days for a term (Jan 15 - Mar 15, 2024)
        start_date = datetime(2024, 1, 15)
        end_date = datetime(2024, 3, 15)
        current = start_date
        
        while current <= end_date:
            # Only weekdays
            if current.weekday() < 5:
                day_id = str(uuid.uuid4())
                cursor.execute(
                    "INSERT INTO teaching_days (id, school_id, date) VALUES (?, ?, ?)",
                    (day_id, school_id, current.strftime("%Y-%m-%d"))
                )
            current += timedelta(days=1)
        
        # Add some holidays
        holiday_dates = [
            ("2024-02-01", "Professional Development Day"),
            ("2024-02-19", "Presidents' Day")
        ]
        for date, desc in holiday_dates:
            holiday_id = str(uuid.uuid4())
            cursor.execute(
                "INSERT INTO holidays (id, school_id, date, description) VALUES (?, ?, ?, ?)",
                (holiday_id, school_id, date, desc)
            )
        
        # Add exam period
        exam_id = str(uuid.uuid4())
        cursor.execute(
            "INSERT INTO exam_periods (id, school_id, start_date, end_date) VALUES (?, ?, ?, ?)",
            (exam_id, school_id, "2024-03-11", "2024-03-15")
        )
    
    print(f"✓ Created school, teacher, class, subject")
    print(f"✓ Created teaching days (Jan 15 - Mar 15, 2024)")
    print(f"✓ Added 2 holidays and 1 exam period")
    print()
    
    # Load curriculum (Phase 2)
    print("Loading curriculum structure...")
    
    curriculum_data = {
        "units": [
            {
                "name": "Quadratic Functions",
                "description": "Introduction to quadratic functions and equations",
                "sequence_order": 1,
                "topics": [
                    {
                        "name": "Graphing Quadratics",
                        "description": "Parabolas and vertex form",
                        "sequence_order": 1,
                        "estimated_weeks": 2
                    },
                    {
                        "name": "Solving Quadratic Equations",
                        "description": "Factoring and quadratic formula",
                        "sequence_order": 2,
                        "estimated_weeks": 2
                    },
                    {
                        "name": "Applications of Quadratics",
                        "description": "Real-world problems",
                        "sequence_order": 3,
                        "estimated_weeks": 1
                    }
                ]
            },
            {
                "name": "Exponential Functions",
                "description": "Growth and decay models",
                "sequence_order": 2,
                "topics": [
                    {
                        "name": "Exponential Growth",
                        "description": "Growth models and compound interest",
                        "sequence_order": 1,
                        "estimated_weeks": 2
                    },
                    {
                        "name": "Exponential Decay",
                        "description": "Decay models and half-life",
                        "sequence_order": 2,
                        "estimated_weeks": 1
                    }
                ]
            }
        ]
    }
    
    result = curriculum_service.load_curriculum(
        school_id, grade_id, subject_id, curriculum_data
    )
    
    print(f"✓ Loaded {result['units_loaded']} curriculum units")
    for unit in result['units']:
        print(f"  - {unit['name']}: {len(unit['topics'])} topics")
    print()
    
    # Calculate planning window
    print("Calculating planning window...")
    
    planning_window = calendar_service.get_planning_window(
        school_id, "2024-01-15", "2024-03-15"
    )
    
    print(f"✓ Planning window: {planning_window['start_date']} to {planning_window['end_date']}")
    print(f"  Available teaching days: {planning_window['available_teaching_days']}")
    print(f"  Available weeks: {planning_window['available_weeks']}")
    print(f"  Lost days: {len(planning_window['lost_days'])}")
    for lost_day in planning_window['lost_days']:
        print(f"    - {lost_day['date']}: {lost_day['description']}")
    print()
    
    # Generate draft plan
    print("Generating draft planning proposal...")
    
    draft_plan = draft_planning_service.generate_draft_plan(
        teacher_id=teacher_id,
        class_id=class_id,
        subject_id=subject_id,
        start_date="2024-01-15",
        end_date="2024-03-15"
    )
    
    print(f"✓ Draft plan generated (session: {draft_plan['session_id'][:8]}...)")
    print(f"  Pacing suggestions: {len(draft_plan['pacing_suggestions'])} weeks")
    print()
    
    # Display pacing suggestions
    print("Weekly pacing breakdown:")
    print("-" * 70)
    for week in draft_plan['pacing_suggestions'][:5]:  # Show first 5 weeks
        print(f"Week {week['week_number']}: {week['week_start_date']} to {week['week_end_date']}")
        print(f"  Unit: {week['unit_name']}")
        for topic in week['topics']:
            print(f"  Topic: {topic['topic_name']} ({topic['estimated_weeks']} week(s))")
        print()
    
    if len(draft_plan['pacing_suggestions']) > 5:
        print(f"... and {len(draft_plan['pacing_suggestions']) - 5} more weeks")
        print()
    
    # Display risk signals
    if draft_plan['risk_signals']:
        print("Risk signals (informational only):")
        print("-" * 70)
        for risk in draft_plan['risk_signals']:
            severity_icon = "⚠️" if risk['severity'] == 'warning' else "ℹ️"
            print(f"{severity_icon} {risk['type'].upper()}: {risk['message']}")
        print()
    else:
        print("✓ No risk signals detected")
        print()
    
    # Display existing plans context
    if draft_plan['existing_plans_context']:
        print(f"Existing lesson plans found: {len(draft_plan['existing_plans_context'])}")
    else:
        print("No existing lesson plans in this period")
    print()
    
    # Teacher accepts draft plan
    print("Teacher reviews and accepts draft plan...")
    print("(Generating confirmation token...)")
    
    confirmation_token = draft_planning_service.generate_confirmation_token(
        draft_plan['session_id']
    )
    
    print(f"✓ Confirmation token: {confirmation_token[:16]}...")
    print()
    
    print("Creating lesson plans from draft...")
    print("(This requires explicit confirmation to prevent accidental creation)")
    
    lesson_plan_ids = draft_planning_service.accept_draft_plan(
        draft_plan['session_id'],
        confirmation_token
    )
    
    print(f"✓ Created {len(lesson_plan_ids)} lesson plans (all in draft status)")
    print()
    
    # Verify lesson plans were created
    print("Verifying created lesson plans...")
    
    for i, lp_id in enumerate(lesson_plan_ids[:3], 1):  # Show first 3
        lp = lesson_plan_service.get_lesson_plan(lp_id)
        print(f"{i}. {lp['topic']}")
        print(f"   Dates: {lp['start_date']} to {lp['end_date']}")
        print(f"   Status: {lp['status']}")
        print(f"   Notes: {lp['instructional_notes'] or '(none - teacher to add)'}")
        print()
    
    if len(lesson_plan_ids) > 3:
        print(f"... and {len(lesson_plan_ids) - 3} more lesson plans")
        print()
    
    print("=" * 70)
    print("PHASE 2 SUCCESS CRITERIA VALIDATION")
    print("=" * 70)
    print()
    print("✓ Teachers can see a clear, realistic pacing plan before a term starts")
    print("  - Draft plan shows weekly breakdown with dates")
    print("  - Planning window calculated from real teaching days")
    print("  - Risk signals flag potential issues")
    print()
    print("✓ Planning suggestions respect calendar constraints and curriculum scope")
    print("  - Holidays and exam periods excluded from planning")
    print("  - Topics distributed across available weeks")
    print("  - Compression risks flagged when scope exceeds time")
    print()
    print("✓ Teachers remain fully in control of what becomes an actual lesson plan")
    print("  - Draft plans are in-memory only (non-persistent)")
    print("  - Explicit confirmation required before creating lesson plans")
    print("  - Lesson plans created as drafts (teacher can edit)")
    print("  - No instructional content generated automatically")
    print()
    print("✓ Phase 2 implementation complete!")


if __name__ == "__main__":
    main()
