"""Example for Phase 6: Professionalization (CLI and Bulk Import)."""
import os
import subprocess
import shutil
from src.database import DatabaseService

def run_example():
    db_path = "keystone_demo_phase6.db"
    if os.path.exists(db_path):
        os.remove(db_path)
        
    print("=== Phase 6: Professionalization Demo ===")
    
    # 1. Initialize DB and get IDs
    db = DatabaseService(db_path)
    school_id = str(DatabaseService.generate_id())
    grade_id = str(DatabaseService.generate_id())
    teacher_id = str(DatabaseService.generate_id())
    subject_id = str(DatabaseService.generate_id())
    class_id = str(DatabaseService.generate_id())
    term_id = str(DatabaseService.generate_id())
    
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO schools (id, name) VALUES (?, ?)", (school_id, "Keystone Academy"))
        cursor.execute("INSERT INTO grades (id, school_id, name) VALUES (?, ?, ?)", (grade_id, school_id, "Grade 11"))
        cursor.execute("INSERT INTO teachers (id, school_id, first_name, last_name) VALUES (?, ?, ?, ?)", 
                     (teacher_id, school_id, "Sarah", "Connor"))
        cursor.execute("INSERT INTO subjects (id, school_id, name) VALUES (?, ?, ?)", (subject_id, school_id, "Applied Math"))
        cursor.execute("INSERT INTO classes (id, school_id, grade_id, name) VALUES (?, ?, ?, ?)",
                     (class_id, school_id, grade_id, "11-B"))
        cursor.execute("INSERT INTO teacher_classes (teacher_id, class_id) VALUES (?, ?)", (teacher_id, class_id))
        cursor.execute("INSERT INTO class_subjects (class_id, subject_id) VALUES (?, ?)", (class_id, subject_id))
        cursor.execute("INSERT INTO terms (id, school_id, name, start_date, end_date) VALUES (?, ?, ?, ?, ?)",
                     (term_id, school_id, "Fall Term", "2024-09-01", "2024-12-31"))

    # 2. Create CSV files for bulk import
    with open("students_import.csv", "w") as f:
        f.write("first_name,last_name,grade_id\n")
        f.write(f"Alice,Wonderland,{grade_id}\n")
        f.write(f"Bob,Marley,{grade_id}\n")
        f.write(f"Charlie,Brown,{grade_id}\n")
        
    with open("curriculum_import.csv", "w") as f:
        f.write("unit_name,topic_name,topic_order,topic_weeks\n")
        f.write("Calculus,Limits,1,2\n")
        f.write("Calculus,Derivatives,2,3\n")
        f.write("Geometry,Vectors,1,2\n")

    # 3. Use CLI to import data
    print("\n[Step 3] Importing Students via CLI...")
    subprocess.run(["python", "-m", "src.keystone_cli", "--db", db_path, "import", "students", "students_import.csv", "--school", school_id])

    print("\n[Step 4] Importing Curriculum via CLI...")
    subprocess.run(["python", "-m", "src.keystone_cli", "--db", db_path, "import", "curriculum", "curriculum_import.csv", 
                   "--school", school_id, "--grade", grade_id, "--subject", subject_id])

    # Enroll imported students in the class
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM students WHERE school_id=?", (school_id,))
        for s in cursor.fetchall():
            cursor.execute("INSERT INTO student_classes (student_id, class_id) VALUES (?, ?)", (s['id'], class_id))
    print("Enrolled imported students in class 11-B.")

    # 4. Use CLI to list students
    print("\n[Step 5] Listing imported students via CLI foundations command...")
    subprocess.run(["python", "-m", "src.keystone_cli", "--db", db_path, "foundations", "--list-students", "--school", school_id])

    # 5. Use CLI to generate batch reports
    print("\n[Step 6] Generating batch reports for class 11-B...")
    output_dir = "phase6_reports"
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
        
    subprocess.run(["python", "-m", "src.keystone_cli", "--db", db_path, "report", "--class-id", class_id, "--term", term_id, "--output-dir", output_dir])

    if os.path.exists(output_dir):
        print(f"\nSuccess! Reports generated in '{output_dir}':")
        for f in os.listdir(output_dir):
            print(f"  - {f}")

    # Cleanup CSVs
    os.remove("students_import.csv")
    os.remove("curriculum_import.csv")
    
    print("\n=== Phase 6 Demo Complete ===")

if __name__ == "__main__":
    run_example()
