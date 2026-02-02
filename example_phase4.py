"""
Phase 4 Example: Qualitative Observations

This example demonstrates Phase 4 functionality:
- Creating qualitative observations (Academic, Social, Behavioral)
- Filtering and listing observations
- Intensity tracking (Positive, Neutral, Concern)
- Privacy and internal-use principles
"""
import uuid
from src import (
    DatabaseService,
    QualitativeObservationService,
)

def main():
    print("=== Phase 4 Qualitative Observations Example ===\n")
    
    # Initialize services
    db = DatabaseService(":memory:")
    obs_service = QualitativeObservationService(db)
    
    # Create foundational data
    school_id = str(uuid.uuid4())
    grade_id = str(uuid.uuid4())
    student_id = str(uuid.uuid4())
    teacher_id = str(uuid.uuid4())
    subject_id = str(uuid.uuid4())
    class_id = str(uuid.uuid4())
    
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO schools (id, name) VALUES (?, ?)", (school_id, "Keystone Academy"))
        cursor.execute("INSERT INTO grades (id, school_id, name, ordinal) VALUES (?, ?, ?, ?)",
                      (grade_id, school_id, "Grade 10", 10))
        cursor.execute("INSERT INTO students (id, school_id, first_name, last_name, enrollment_status) VALUES (?, ?, ?, ?, ?)",
                      (student_id, school_id, "Alex", "Smith", "active"))
        cursor.execute("INSERT INTO teachers (id, school_id, first_name, last_name) VALUES (?, ?, ?, ?)",
                      (teacher_id, school_id, "John", "Doe"))
        cursor.execute("INSERT INTO subjects (id, school_id, name) VALUES (?, ?, ?)",
                      (subject_id, school_id, "Science"))
        cursor.execute("INSERT INTO classes (id, school_id, grade_id, name) VALUES (?, ?, ?, ?)",
                      (class_id, school_id, grade_id, "Science 10-1"))

    print(f"✓ Context: Teacher John Doe observing student Alex Smith in Science 10-1")
    
    # Create observations
    print("\n1. Capturing qualitative observations...")
    
    obs1_id = obs_service.create_observation(
        student_id=student_id,
        teacher_id=teacher_id,
        date="2024-03-10",
        category="Academic",
        observation_text="Demonstrated exceptional understanding of photosynthesis during today's lab.",
        intensity="positive",
        class_id=class_id,
        subject_id=subject_id
    )
    
    obs2_id = obs_service.create_observation(
        student_id=student_id,
        teacher_id=teacher_id,
        date="2024-03-12",
        category="Social",
        observation_text="Helped a peer troubleshoot their equipment without being asked.",
        intensity="positive"
    )
    
    obs3_id = obs_service.create_observation(
        student_id=student_id,
        teacher_id=teacher_id,
        date="2024-03-15",
        category="Behavioral",
        observation_text="Struggled to focus during the lectures; distracted by a mobile device.",
        intensity="concern"
    )
    
    print(f"   ✓ Created 3 observations (Academic, Social, Behavioral)")
    
    # List observations
    print("\n2. Retrieving and filtering observations...")
    
    all_obs = obs_service.list_observations(student_id=student_id)
    print(f"   ✓ All observations for Alex ({len(all_obs)} total):")
    for o in all_obs:
        print(f"     [{o['date']}] {o['category']} ({o['intensity'] or 'neutral'}): {o['observation_text']}")
        
    # Filter by category
    academic_obs = obs_service.list_observations(student_id=student_id, category="Academic")
    print(f"\n   ✓ Academic-only filter: {len(academic_obs)} result(s)")
    
    # Filter by date
    recent_obs = obs_service.list_observations(student_id=student_id, start_date="2024-03-11")
    print(f"   ✓ Observations since 2024-03-11: {len(recent_obs)} result(s)")
    
    # Update an observation
    print("\n3. Updating observations...")
    obs_service.update_observation(obs3_id, observation_text="Improved focus after a brief redirection.")
    updated_obs = obs_service.get_observation(obs3_id)
    print(f"   ✓ Updated observation text: {updated_obs['observation_text']}")
    
    # Privacy principles
    print("\n4. Privacy & Internal Use Principles...")
    print("   ✓ Observations are internal to the teacher's planning assistant.")
    print("   ✓ Data is categorical and time-bound, serving as professional memory.")
    print("   ✓ No raw text is exposed to students or parents in Phase 4.")
    
    print("\n=== Phase 4 Example Complete ===")

if __name__ == "__main__":
    main()
