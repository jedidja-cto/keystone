"""Draft planning service for Phase 2 premeditated planning."""
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from src.database import DatabaseService
from src.curriculum_service import CurriculumService
from src.calendar_service import CalendarService
from src.pacing_calculation_service import PacingCalculationService
from src.lesson_plan_service import LessonPlanService


class DraftPlanningService:
    """Service for generating and managing draft planning proposals.
    
    All draft plans are in-memory only (non-persistent).
    No lesson plans are created without explicit teacher confirmation.
    """
    
    def __init__(
        self,
        db_service: DatabaseService,
        curriculum_service: CurriculumService,
        calendar_service: CalendarService,
        pacing_service: PacingCalculationService,
        lesson_plan_service: LessonPlanService
    ):
        """Initialize draft planning service.
        
        Args:
            db_service: Database service instance
            curriculum_service: Curriculum service instance
            calendar_service: Calendar service instance
            pacing_service: Pacing calculation service instance
            lesson_plan_service: Lesson plan service instance (Phase 1)
        """
        self.db = db_service
        self.curriculum_service = curriculum_service
        self.calendar_service = calendar_service
        self.pacing_service = pacing_service
        self.lesson_plan_service = lesson_plan_service
        
        # In-memory storage for draft plans
        self._draft_plans: Dict[str, Dict[str, Any]] = {}
        
        # In-memory storage for confirmation tokens
        self._confirmation_tokens: Dict[str, str] = {}
    
    def generate_draft_plan(
        self,
        teacher_id: str,
        class_id: str,
        subject_id: str,
        start_date: str,
        end_date: str
    ) -> Dict[str, Any]:
        """Generate a draft planning proposal.
        
        This is a non-destructive operation. No database writes occur.
        All outputs are proposals that teachers can accept, modify, or discard.
        
        Args:
            teacher_id: ID of the teacher
            class_id: ID of the class
            subject_id: ID of the subject
            start_date: Planning window start date (ISO 8601)
            end_date: Planning window end date (ISO 8601)
            
        Returns:
            Draft plan dictionary (in-memory only)
        """
        # Get school_id and grade_id from class
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT school_id, grade_id FROM classes WHERE id = ?
            """, (class_id,))
            class_row = cursor.fetchone()
            
            if not class_row:
                raise ValueError(f"Class {class_id} not found")
            
            school_id = class_row["school_id"]
            grade_id = class_row["grade_id"]
        
        # Read curriculum structure (read-only)
        curriculum_structure = self.curriculum_service.get_curriculum_structure(
            school_id, grade_id, subject_id
        )
        
        # Calculate planning window (read-only calendar access)
        planning_window = self.calendar_service.get_planning_window(
            school_id, start_date, end_date
        )
        
        # Read existing lesson plans (read-only)
        existing_plans_context = self._get_existing_plans_context(
            class_id, subject_id, start_date, end_date
        )
        
        # Read existing assessments (read-only)
        existing_assessments_context = self._get_existing_assessments_context(
            class_id, subject_id, start_date, end_date
        )
        
        # Calculate pacing suggestions
        pacing_suggestions = self.pacing_service.calculate_pacing(
            curriculum_structure, planning_window
        )
        
        # Detect risk signals (informational only, no enforcement)
        risk_signals = []
        risk_signals.extend(
            self.pacing_service.detect_compression_risk(
                curriculum_structure,
                planning_window["available_weeks"]
            )
        )
        risk_signals.extend(
            self.pacing_service.detect_gaps(
                pacing_suggestions,
                planning_window["available_weeks"]
            )
        )
        risk_signals.extend(
            self.pacing_service.detect_overload(pacing_suggestions)
        )
        
        # Create draft plan (in-memory only)
        session_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        draft_plan = {
            "session_id": session_id,
            "teacher_id": teacher_id,
            "class_id": class_id,
            "subject_id": subject_id,
            "school_id": school_id,
            "grade_id": grade_id,
            "planning_window": planning_window,
            "pacing_suggestions": pacing_suggestions,
            "risk_signals": risk_signals,
            "existing_plans_context": existing_plans_context,
            "existing_assessments_context": existing_assessments_context,
            "created_at": timestamp,
            "modified_at": timestamp
        }
        
        # Store in memory
        self._draft_plans[session_id] = draft_plan
        
        return draft_plan
    
    def modify_draft_plan(
        self,
        session_id: str,
        modifications: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Modify a draft plan.
        
        Teachers can reorder topics, adjust pacing, or change dates.
        All modifications are in-memory only.
        
        Args:
            session_id: Draft plan session ID
            modifications: Dictionary of modifications to apply
            
        Returns:
            Updated draft plan dictionary
        """
        if session_id not in self._draft_plans:
            raise ValueError(f"Draft plan {session_id} not found")
        
        draft_plan = self._draft_plans[session_id]
        
        # Apply modifications (simplified - real implementation would be more sophisticated)
        if "pacing_suggestions" in modifications:
            draft_plan["pacing_suggestions"] = modifications["pacing_suggestions"]
        
        if "planning_window" in modifications:
            # Recalculate if dates changed
            if "start_date" in modifications["planning_window"] or "end_date" in modifications["planning_window"]:
                new_start = modifications["planning_window"].get("start_date", draft_plan["planning_window"]["start_date"])
                new_end = modifications["planning_window"].get("end_date", draft_plan["planning_window"]["end_date"])
                
                draft_plan["planning_window"] = self.calendar_service.get_planning_window(
                    draft_plan["school_id"], new_start, new_end
                )
        
        # Update timestamp
        draft_plan["modified_at"] = datetime.utcnow().isoformat()
        
        return draft_plan
    
    def reorder_topics(
        self,
        session_id: str,
        new_order: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Reorder topics within a draft plan.
        
        Teachers can change the sequence without modifying curriculum structure.
        
        Args:
            session_id: Draft plan session ID
            new_order: New ordering of topics
            
        Returns:
            Updated draft plan dictionary
        """
        if session_id not in self._draft_plans:
            raise ValueError(f"Draft plan {session_id} not found")
        
        draft_plan = self._draft_plans[session_id]
        draft_plan["pacing_suggestions"] = new_order
        draft_plan["modified_at"] = datetime.utcnow().isoformat()
        
        return draft_plan
    
    def discard_draft_plan(self, session_id: str) -> bool:
        """Discard a draft plan.
        
        Removes draft from memory. No database operations.
        
        Args:
            session_id: Draft plan session ID
            
        Returns:
            True if successful
        """
        if session_id in self._draft_plans:
            del self._draft_plans[session_id]
            
            # Clean up confirmation token if exists
            if session_id in self._confirmation_tokens:
                del self._confirmation_tokens[session_id]
            
            return True
        return False
    
    def generate_confirmation_token(self, session_id: str) -> str:
        """Generate a confirmation token for accepting a draft plan.
        
        Args:
            session_id: Draft plan session ID
            
        Returns:
            Confirmation token
        """
        if session_id not in self._draft_plans:
            raise ValueError(f"Draft plan {session_id} not found")
        
        token = str(uuid.uuid4())
        self._confirmation_tokens[session_id] = token
        return token
    
    def accept_draft_plan(
        self,
        session_id: str,
        confirmation_token: str
    ) -> List[str]:
        """Accept a draft plan and create lesson plans.
        
        Requires explicit confirmation token to prevent accidental creation.
        Creates lesson plans via Phase 1 LessonPlanService.
        
        Important:
        - Lesson plans are created with status="draft" (not finalized)
        - No instructional content is generated (only topic names and dates)
        - Dates are coarse (week-level ranges, not day-locked)
        - Teachers are expected to review/edit each lesson plan after creation
        - This is a bulk scaffolding operation, not a final planning step
        
        Args:
            session_id: Draft plan session ID
            confirmation_token: Confirmation token from generate_confirmation_token()
            
        Returns:
            List of created lesson plan IDs
        """
        # Validate session exists
        if session_id not in self._draft_plans:
            raise ValueError(f"Draft plan {session_id} not found")
        
        # Validate confirmation token
        if session_id not in self._confirmation_tokens:
            raise ValueError("No confirmation token generated for this session")
        
        if self._confirmation_tokens[session_id] != confirmation_token:
            raise ValueError("Invalid confirmation token")
        
        # Retrieve draft plan
        draft_plan = self._draft_plans[session_id]
        
        # Create lesson plans via Phase 1 service
        lesson_plan_ids = []
        
        for week in draft_plan["pacing_suggestions"]:
            for topic in week["topics"]:
                # Call Phase 1 LessonPlanService (respects phase isolation)
                lp_id = self.lesson_plan_service.create_lesson_plan(
                    teacher_id=draft_plan["teacher_id"],
                    class_id=draft_plan["class_id"],
                    subject_id=draft_plan["subject_id"],
                    status="draft",  # Created as draft, not finalized
                    instructional_notes=None,  # No content generated
                    topic=topic["topic_name"],
                    start_date=week["week_start_date"],
                    end_date=week["week_end_date"]
                )
                lesson_plan_ids.append(lp_id)
        
        # Remove draft from memory
        del self._draft_plans[session_id]
        del self._confirmation_tokens[session_id]
        
        return lesson_plan_ids
    
    def get_draft_plan(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get a draft plan by session ID.
        
        Args:
            session_id: Draft plan session ID
            
        Returns:
            Draft plan dictionary or None if not found
        """
        return self._draft_plans.get(session_id)
    
    def list_draft_plans(self, teacher_id: str) -> List[Dict[str, Any]]:
        """List all draft plans for a teacher.
        
        Args:
            teacher_id: ID of the teacher
            
        Returns:
            List of draft plan dictionaries
        """
        return [
            draft for draft in self._draft_plans.values()
            if draft["teacher_id"] == teacher_id
        ]
    
    def _get_existing_plans_context(
        self,
        class_id: str,
        subject_id: str,
        start_date: str,
        end_date: str
    ) -> List[Dict[str, Any]]:
        """Get existing lesson plans for context (read-only).
        
        Args:
            class_id: ID of the class
            subject_id: ID of the subject
            start_date: Start date
            end_date: End date
            
        Returns:
            List of existing lesson plan summaries
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, start_date, end_date, topic, status
                FROM lesson_plans
                WHERE class_id = ? AND subject_id = ?
                  AND ((start_date >= ? AND start_date <= ?)
                       OR (end_date >= ? AND end_date <= ?))
                ORDER BY start_date
            """, (class_id, subject_id, start_date, end_date, start_date, end_date))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def _get_existing_assessments_context(
        self,
        class_id: str,
        subject_id: str,
        start_date: str,
        end_date: str
    ) -> List[Dict[str, Any]]:
        """Get existing assessments for context (read-only).
        
        Args:
            class_id: ID of the class
            subject_id: ID of the subject
            start_date: Start date
            end_date: End date
            
        Returns:
            List of existing assessment summaries
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, date, name
                FROM assessments
                WHERE class_id = ? AND subject_id = ?
                  AND date >= ? AND date <= ?
                ORDER BY date
            """, (class_id, subject_id, start_date, end_date))
            
            return [dict(row) for row in cursor.fetchall()]
