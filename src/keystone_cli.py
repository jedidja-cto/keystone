"""Unified Command Line Interface for Keystone."""
import argparse
import sys
import os
import json
from src.database import DatabaseService
from src.lesson_plan_service import LessonPlanService
from src.assessment_service import AssessmentService
from src.assessment_mark_service import AssessmentMarkService
from src.aggregation_service import AggregationService
from src.import_service import ImportService
from src.report_generation_service import ReportGenerationService


def main():
    parser = argparse.ArgumentParser(description="Keystone: Teacher-First Operational Platform")
    parser.add_argument("--db", default="keystone.db", help="Path to SQLite database")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # 1. Foundations Service (Minimal for now)
    foundation_parser = subparsers.add_parser("foundations", help="Foundation data queries")
    foundation_parser.add_argument("--list-students", action="store_true")
    foundation_parser.add_argument("--school", help="School ID")

    # 2. Planning
    plan_parser = subparsers.add_parser("plan", help="Manage lesson plans")
    plan_parser.add_argument("--list", action="store_true")
    plan_parser.add_argument("--teacher", help="Teacher ID")
    plan_parser.add_argument("--class-id", help="Class ID")

    # 3. Import
    import_parser = subparsers.add_parser("import", help="Bulk data import")
    import_parser.add_argument("type", choices=["students", "curriculum"])
    import_parser.add_argument("file", help="Path to CSV file")
    import_parser.add_argument("--school", required=True, help="School ID")
    import_parser.add_argument("--grade", help="Grade ID (for curriculum)")
    import_parser.add_argument("--subject", help="Subject ID (for curriculum)")

    # 4. Reports
    report_parser = subparsers.add_parser("report", help="Generate reports")
    report_parser.add_argument("--student", help="Student ID for single report")
    report_parser.add_argument("--class-id", help="Class ID for batch reporting")
    report_parser.add_argument("--term", required=True, help="Term ID")
    report_parser.add_argument("--output-dir", help="Output directory for batch reports")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    db = DatabaseService(args.db)
    
    try:
        if args.command == "import":
            importer = ImportService(db)
            with open(args.file, 'r') as f:
                csv_data = f.read()
            
            if args.type == "students":
                result = importer.import_students(args.school, csv_data)
                print(f"Imported {result['success_count']} students. Errors: {len(result['errors'])}")
                for err in result['errors']:
                    print(f"  - {err}")
            
            elif args.type == "curriculum":
                if not all([args.grade, args.subject]):
                    print("Error: --grade and --subject are required for curriculum import.")
                    sys.exit(1)
                result = importer.import_curriculum(args.school, args.grade, args.subject, csv_data)
                print(f"Imported {result['units_imported']} units and {result['topics_imported']} topics.")

        elif args.command == "report":
            reporter = ReportGenerationService(db)
            if args.student:
                report = reporter.generate_student_progress_report(args.student, args.term)
                print(json.dumps(report, indent=2))
            elif args.class_id:
                if not args.output_dir:
                    print("Error: --output-dir is required for batch reporting.")
                    sys.exit(1)
                result = reporter.batch_export_reports(args.class_id, args.term, args.output_dir)
                print(f"Exported {result['reports_exported']} reports to {result['directory']}")

        elif args.command == "foundations":
            if args.list_students:
                if not args.school:
                    print("Error: --school is required to list students.")
                    sys.exit(1)
                with db.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT id, first_name, last_name FROM students WHERE school_id=?", (args.school,))
                    for s in cursor.fetchall():
                        print(f"{s['id']}: {s['first_name']} {s['last_name']}")

        elif args.command == "plan":
            planner = LessonPlanService(db)
            if args.list:
                plans = planner.list_lesson_plans(teacher_id=args.teacher, class_id=args.class_id)
                for p in plans:
                    print(f"[{p['status']}] {p['date'] or 'Unscheduled'}: {p['topic']} - {p['instructional_notes'][:50]}...")

    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
