"""Pacing calculation service for draft planning."""
from datetime import datetime, timedelta
from typing import List, Dict, Any


class PacingCalculationService:
    """Service for calculating pacing suggestions and detecting risks."""
    
    # Configurable heuristics (not enforced limits)
    MAX_TOPICS_PER_WEEK = 2
    
    def __init__(self):
        """Initialize pacing calculation service."""
        pass
    
    def calculate_pacing(
        self,
        curriculum_structure: Dict[str, Any],
        planning_window: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Calculate pacing suggestions for curriculum topics.
        
        Distributes topics across available weeks using heuristic defaults.
        Teachers may override any pacing suggestion.
        
        Args:
            curriculum_structure: Curriculum hierarchy with units and topics
            planning_window: Planning window with available weeks and dates
            
        Returns:
            List of weekly pacing suggestions
        """
        units = curriculum_structure.get("units", [])
        available_weeks = planning_window["available_weeks"]
        teaching_days = planning_window["teaching_days"]
        
        if not teaching_days:
            return []
        
        # Calculate week boundaries
        week_boundaries = self._calculate_week_boundaries(
            teaching_days,
            available_weeks
        )
        
        # Distribute topics across weeks
        pacing_suggestions = []
        current_week = 1
        
        for unit in units:
            for topic in unit.get("topics", []):
                if current_week > available_weeks:
                    # Curriculum exceeds available time
                    break
                
                week_info = week_boundaries.get(current_week, {})
                
                pacing_suggestions.append({
                    "week_number": current_week,
                    "week_start_date": week_info.get("start_date"),
                    "week_end_date": week_info.get("end_date"),
                    "unit_id": unit["id"],
                    "unit_name": unit["name"],
                    "topics": [{
                        "topic_id": topic["id"],
                        "topic_name": topic["name"],
                        "estimated_weeks": topic.get("estimated_weeks", 1)
                    }]
                })
                
                # Advance weeks based on estimated duration
                estimated_weeks = topic.get("estimated_weeks", 1)
                current_week += estimated_weeks
        
        return pacing_suggestions
    
    def detect_compression_risk(
        self,
        curriculum_structure: Dict[str, Any],
        available_weeks: int
    ) -> List[Dict[str, Any]]:
        """Detect if curriculum scope exceeds available time.
        
        Args:
            curriculum_structure: Curriculum hierarchy with units and topics
            available_weeks: Number of available weeks
            
        Returns:
            List of compression risk signals (informational only)
        """
        risks = []
        
        # Calculate total estimated weeks needed
        total_weeks_needed = 0
        for unit in curriculum_structure.get("units", []):
            for topic in unit.get("topics", []):
                total_weeks_needed += topic.get("estimated_weeks", 1)
        
        if total_weeks_needed > available_weeks:
            risks.append({
                "type": "compression",
                "severity": "warning",
                "message": f"Curriculum requires {total_weeks_needed} weeks but only {available_weeks} available",
                "affected_weeks": list(range(available_weeks + 1, total_weeks_needed + 1)),
                "weeks_needed": total_weeks_needed,
                "weeks_available": available_weeks
            })
        
        return risks
    
    def detect_gaps(
        self,
        pacing_suggestions: List[Dict[str, Any]],
        available_weeks: int
    ) -> List[Dict[str, Any]]:
        """Detect weeks with no planned content.
        
        Args:
            pacing_suggestions: List of pacing suggestions
            available_weeks: Number of available weeks
            
        Returns:
            List of gap risk signals (informational only)
        """
        risks = []
        
        # Identify planned weeks
        planned_weeks = set()
        for suggestion in pacing_suggestions:
            planned_weeks.add(suggestion["week_number"])
        
        # Find gap weeks
        all_weeks = set(range(1, available_weeks + 1))
        gap_weeks = all_weeks - planned_weeks
        
        if gap_weeks:
            risks.append({
                "type": "gap",
                "severity": "info",
                "message": f"Weeks {sorted(gap_weeks)} have no planned content",
                "affected_weeks": sorted(gap_weeks)
            })
        
        return risks
    
    def detect_overload(
        self,
        pacing_suggestions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Detect weeks with too many topics (heuristic check).
        
        Args:
            pacing_suggestions: List of pacing suggestions
            
        Returns:
            List of overload risk signals (informational only)
        """
        risks = []
        
        # Count topics per week
        topics_per_week = {}
        for suggestion in pacing_suggestions:
            week = suggestion["week_number"]
            topic_count = len(suggestion["topics"])
            topics_per_week[week] = topics_per_week.get(week, 0) + topic_count
        
        # Flag weeks exceeding heuristic threshold
        for week, count in topics_per_week.items():
            if count > self.MAX_TOPICS_PER_WEEK:
                risks.append({
                    "type": "overload",
                    "severity": "info",
                    "message": f"Week {week} has {count} topics (consider spreading)",
                    "affected_weeks": [week],
                    "topic_count": count
                })
        
        return risks
    
    def _calculate_week_boundaries(
        self,
        teaching_days: List[str],
        available_weeks: int
    ) -> Dict[int, Dict[str, str]]:
        """Calculate start and end dates for each week.
        
        Args:
            teaching_days: List of teaching day dates
            available_weeks: Number of available weeks
            
        Returns:
            Dictionary mapping week number to start/end dates
        """
        if not teaching_days:
            return {}
        
        week_boundaries = {}
        days_per_week = len(teaching_days) // available_weeks if available_weeks > 0 else len(teaching_days)
        
        for week_num in range(1, available_weeks + 1):
            start_idx = (week_num - 1) * days_per_week
            end_idx = min(week_num * days_per_week - 1, len(teaching_days) - 1)
            
            if start_idx < len(teaching_days):
                week_boundaries[week_num] = {
                    "start_date": teaching_days[start_idx],
                    "end_date": teaching_days[end_idx]
                }
        
        return week_boundaries
