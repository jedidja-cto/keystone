# Phase 6: Operational Trial & Professionalization Requirements

## Purpose
Phase 6 transitions Keystone from a collection of logic services into a professional tool that can be used by teachers in a real-world setting. It focuses on solving the "cold start" problem (getting data into the system) and providing a unified way to interact with the platform.

## Core Features

### 1. Bulk Data Import
- **CSV Support**: Teachers must be able to import large datasets using standard spreadsheets.
- **Atomic Foundations**: Support CSV import for:
    - Student Rosters (Name, Grade, ID)
    - Curriculum Structure (Units, Topics, Sequence)
    - Content Mappings (Topic -> Textbook references)
- **Validation**: Strict validation of CSV formats with helpful error reporting for malformed data.

### 2. Keystone CLI (Unified Interface)
- **Single Entry Point**: A `keystone.py` or similar command runner.
- **Command Categories**:
    - `foundations`: Manage students, classes, and teachers.
    - `plan`: View and manage lesson plans.
    - `agg`: Calculate averages and performance summaries.
    - `report`: Generate individual or batch parent reports.
    - `import`: Run bulk data import tasks.

### 3. Batch Report Generation
- **Class-wide Exports**: Command to generate reports for every student in a class for a given term in a single execution.
- **Output Formats**: Support for formatted text files (printable) or structured JSON batches.

## Success Criteria
- **Minutes instead of Lines**: A full class roster can be localized in under 2 minutes using CSV import.
- **Logic Unified**: No need to write Python scripts to perform standard operations.
- **Resiliency**: Partial CSV imports should fail gracefully without corrupting the database.

## Constitutional Guardrails (Phase 6)
- **Teacher-Only**: The CLI remains a local, teacher-controlled tool.
- **Non-Coercive**: Import errors should suggest fixes, not demand them.
- **Minimal Dependencies**: Maintain the "Standard Library Only" philosophy where possible (using `csv` module over `pandas`).
