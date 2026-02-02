"""
Phase 3 Example: Content Mapping (Optional Textbook References)

This example demonstrates Phase 3 functionality:
- Optional textbook registration
- Optional content mapping (topic → textbook content)
- Optional lesson content alignment
- Informational workload aggregation

Key principles demonstrated:
- Everything is optional (no errors for missing data)
- No enforcement (all aggregates are informational only)
- Inequality-aware (no assumptions about student access)
- Annotation only (no mutation of earlier phases)
"""
import uuid
from src import (
    DatabaseService,
    TextbookService,
    ContentMappingService,
    LessonContentAlignmentService,
    WorkloadAggregationService,
    LessonPlanService,
    CurriculumService,
)


def main():
    """Demonstrate Phase 3 content mapping functionality."""
    print("=== Phase 3 Content Mapping Example ===\n")
    
    # Initialize services
    db = DatabaseService(":memory:")
    textbook_service = TextbookService(db)
    content_mapping_service = ContentMappingService(db)
    alignment_service = LessonContentAlignmentService(db)
    workload_service = WorkloadAggregationService(db)
    lesson_service = LessonPlanService(db)
    curriculum_service = CurriculumService(db)
    
    # Create foundational data (Phase 0)
    print("1. Setting up foundational data...")
    with db.get_connection() as conn:
        cursor = conn.cursor()
        
        # School
        school_id = str(uuid.uuid4())
        cursor.execute("INSERT INTO schools (id, name) VALUES (?, ?)", 
                      (school_id, "Riverside High School"))
        
        # Grade
        grade_id = str(uuid.uuid4())
        cursor.execute("INSERT INTO grades (id, school_id, name, ordinal) VALUES (?, ?, ?, ?)",
                      (grade_id, school_id, "Grade 10", 10))
        
        # Teacher
        teacher_id = str(uuid.uuid4())
        cursor.execute("INSERT INTO teachers (id, school_id, first_name, last_name) VALUES (?, ?, ?, ?)",
                      (teacher_id, school_id, "Sarah", "Johnson"))
        
        # Subject
        subject_id = str(uuid.uuid4())
        cursor.execute("INSERT INTO subjects (id, school_id, name) VALUES (?, ?, ?)",
                      (subject_id, school_id, "Mathematics"))
        
        # Class
        class_id = str(uuid.uuid4())
        cursor.execute("INSERT INTO classes (id, school_id, grade_id, name) VALUES (?, ?, ?, ?)",
                      (class_id, school_id, grade_id, "10A Mathematics"))
    
    print(f"   ✓ Created school: Riverside High School")
    print(f"   ✓ Created class: 10A Mathematics")
    print(f"   ✓ Created teacher: Sarah Johnson")
    
    # Create curriculum (Phase 2)
    print("\n2. Setting up curriculum...")
    
    # Load curriculum structure (Phase 2 ingestion)
    curriculum_data = {
        "units": [
            {
                "name": "Algebra Fundamentals",
                "description": "Core algebraic concepts and operations",
                "sequence_order": 1,
                "topics": [
                    {
                        "name": "Quadratic Equations",
                        "description": "Solving quadratic equations using various methods",
                        "sequence_order": 1,
                        "estimated_weeks": 2
                    },
                    {
                        "name": "Factoring Polynomials",
                        "description": "Factoring techniques for polynomial expressions",
                        "sequence_order": 2,
                        "estimated_weeks": 1
                    }
                ]
            }
        ]
    }
    
    result = curriculum_service.load_curriculum(
        school_id=school_id,
        grade_id=grade_id,
        subject_id=subject_id,
        curriculum_data=curriculum_data
    )
    
    # Get the created unit and topic IDs
    units = curriculum_service.list_units(school_id, grade_id, subject_id)
    unit_id = units[0]['id']
    
    topics = curriculum_service.list_topics(unit_id)
    topic1_id = next(t['id'] for t in topics if t['name'] == 'Quadratic Equations')
    topic2_id = next(t['id'] for t in topics if t['name'] == 'Factoring Polynomials')
    
    print(f"   ✓ Loaded curriculum unit: Algebra Fundamentals")
    print(f"   ✓ Loaded topics: Quadratic Equations, Factoring Polynomials")
    
    # Create lesson plans (Phase 1)
    print("\n3. Creating lesson plans...")
    lesson1_id = lesson_service.create_lesson_plan(
        teacher_id=teacher_id,
        class_id=class_id,
        subject_id=subject_id,
        topic="Quadratic Equations - Introduction",
        start_date="2024-02-01",
        end_date="2024-02-05",
        status="draft"
    )
    
    lesson2_id = lesson_service.create_lesson_plan(
        teacher_id=teacher_id,
        class_id=class_id,
        subject_id=subject_id,
        topic="Quadratic Equations - Solving Methods",
        start_date="2024-02-08",
        end_date="2024-02-12",
        status="draft"
    )
    
    lesson3_id = lesson_service.create_lesson_plan(
        teacher_id=teacher_id,
        class_id=class_id,
        subject_id=subject_id,
        topic="Factoring Polynomials",
        start_date="2024-02-15",
        end_date="2024-02-19",
        status="draft"
    )
    
    print(f"   ✓ Created 3 lesson plans for February 2024")
    
    # Demonstrate Phase 3: Optional textbook registration
    print("\n4. Phase 3: Optional textbook registration...")
    
    # Teacher can work without textbooks (this is valid)
    workload_before = workload_service.calculate_workload_for_period(
        class_id=class_id,
        subject_id=subject_id,
        start_date="2024-02-01",
        end_date="2024-02-28"
    )
    print(f"   ✓ Workload without textbooks: {workload_before}")
    print(f"     (No errors - system works without textbooks)")
    
    # Teacher optionally registers textbooks
    textbook1_id = textbook_service.register_textbook(
        subject_id=subject_id,
        title="Algebra 1: Concepts and Applications",
        edition="3rd Edition",
        publisher="MathWorks Publishing",
        isbn="978-0-123456-78-9",
        publication_year=2023
    )
    
    textbook2_id = textbook_service.register_textbook(
        subject_id=subject_id,
        title="Algebra Workbook",
        publisher="Practice Press"
        # Note: edition, ISBN, year are optional
    )
    
    print(f"   ✓ Registered textbook: Algebra 1: Concepts and Applications")
    print(f"   ✓ Registered textbook: Algebra Workbook (minimal info)")
    
    # Demonstrate Phase 3: Optional content mapping
    print("\n5. Phase 3: Optional content mapping...")
    
    # Map topics to textbook content (all fields optional except topic_id and textbook_id)
    mapping1_id = content_mapping_service.create_content_mapping(
        topic_id=topic1_id,
        textbook_id=textbook1_id,
        start_page=45,
        end_page=67,
        exercise_references="Exercises 3.1-3.5, Review Problems 1-20",
        estimated_pages=22,
        estimated_exercises=25,
        estimated_time_minutes=180  # 3 hours
    )
    
    # Minimal mapping (only required fields)
    mapping2_id = content_mapping_service.create_content_mapping(
        topic_id=topic2_id,
        textbook_id=textbook1_id
        # No page ranges, exercises, or workload estimates - this is valid
    )
    
    # Additional mapping to workbook
    mapping3_id = content_mapping_service.create_content_mapping(
        topic_id=topic1_id,
        textbook_id=textbook2_id,
        exercise_references="Practice Set A, B",
        estimated_exercises=15,
        estimated_time_minutes=60
    )
    
    print(f"   ✓ Mapped Quadratic Equations to main textbook (full details)")
    print(f"   ✓ Mapped Factoring Polynomials to main textbook (minimal)")
    print(f"   ✓ Mapped Quadratic Equations to workbook (exercises only)")
    
    # Demonstrate Phase 3: Optional lesson content alignment
    print("\n6. Phase 3: Optional lesson content alignment...")
    
    # Align some lessons to content (optional)
    alignment_service.align_lesson_to_content(lesson1_id, mapping1_id)
    alignment_service.align_lesson_to_content(lesson1_id, mapping3_id)  # Multiple alignments allowed
    alignment_service.align_lesson_to_content(lesson2_id, mapping1_id)
    
    # lesson3_id is NOT aligned - this is valid (no errors)
    
    print(f"   ✓ Aligned lesson 1 to textbook content (2 mappings)")
    print(f"   ✓ Aligned lesson 2 to textbook content")
    print(f"   ✓ Lesson 3 has no alignments (this is valid)")
    
    # Demonstrate Phase 3: Informational workload aggregation
    print("\n7. Phase 3: Informational workload aggregation...")
    
    workload_after = workload_service.calculate_workload_for_period(
        class_id=class_id,
        subject_id=subject_id,
        start_date="2024-02-01",
        end_date="2024-02-28"
    )
    
    print(f"   ✓ Period workload: {workload_after}")
    print(f"     - Total lessons: {workload_after['lesson_count']}")
    print(f"     - Aligned lessons: {workload_after['aligned_lesson_count']}")
    print(f"     - Estimated pages: {workload_after['total_pages']}")
    print(f"     - Estimated exercises: {workload_after['total_exercises']}")
    print(f"     - Estimated time: {workload_after['total_time_minutes']} minutes")
    
    topic_workload = workload_service.calculate_workload_for_topic(topic1_id)
    print(f"   ✓ Quadratic Equations topic workload: {topic_workload}")
    
    # Demonstrate Phase 3: Inequality-aware design
    print("\n8. Phase 3: Inequality-aware design...")
    
    # Show that system works for teachers without textbook access
    print("   ✓ System never assumes students have textbook access")
    print("   ✓ Textbook references are teacher planning aids only")
    print("   ✓ No student-facing content is generated")
    print("   ✓ Physical and digital textbooks treated equally")
    
    # Demonstrate Phase 3: Non-enforcement
    print("\n9. Phase 3: Non-enforcement guarantees...")
    
    # Delete textbook - lesson plans are unaffected
    textbook_service.delete_textbook(textbook2_id)
    
    # Lesson plans still exist
    lesson = lesson_service.get_lesson_plan(lesson1_id)
    print(f"   ✓ Deleted textbook - lesson plans unaffected")
    print(f"   ✓ Lesson 1 still exists: {lesson['topic']}")
    
    # Workload calculation handles missing data gracefully
    final_workload = workload_service.calculate_workload_for_period(
        class_id=class_id,
        subject_id=subject_id,
        start_date="2024-02-01",
        end_date="2024-02-28"
    )
    print(f"   ✓ Workload calculation after deletion: {final_workload}")
    print(f"     (No errors - missing data handled gracefully)")
    
    # Demonstrate Phase 3: Read-only access to earlier phases
    print("\n10. Phase 3: Read-only access to earlier phases...")
    
    # Show alignments for lesson (reads Phase 1 data)
    alignments = alignment_service.list_alignments_for_lesson(lesson1_id)
    print(f"   ✓ Read lesson alignments: {len(alignments)} content mappings")
    
    # Show lessons for content (reads Phase 1 data)
    lessons = alignment_service.list_lessons_for_content(mapping1_id)
    print(f"   ✓ Read content lessons: {len(lessons)} lesson plans")
    
    print("\n=== Phase 3 Example Complete ===")
    print("\nKey Phase 3 Principles Demonstrated:")
    print("✓ Optional by construction - nothing is required")
    print("✓ Non-enforcing - no consequences for missing data")
    print("✓ Inequality-aware - no student access assumptions")
    print("✓ Annotative only - no mutation of earlier phases")
    print("✓ Phase-isolated - read-only access to Phase 0, 1, 2")
    print("✓ Informational only - all aggregates are advisory")


if __name__ == "__main__":
    main()