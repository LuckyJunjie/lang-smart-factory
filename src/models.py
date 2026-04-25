"""
LangFlow Factory - Data Models
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"

class WorkflowStep(Enum):
    TRIGGER = "trigger"
    ANALYSIS = "analysis"
    ARCHITECTURE = "architecture"
    DETAIL_DESIGN = "detail_design"
    DISPATCH = "dispatch"
    IMPLEMENTATION = "implementation"
    TESTING = "testing"
    GAMEPLAY_EVAL = "gameplay_eval"
    ACCEPTANCE = "acceptance"
    RELEASE = "release"

class RequirementType(Enum):
    FEATURE = "feature"
    BUG = "bug"
    ENHANCEMENT = "enhancement"
    RESEARCH = "research"
    ASSET = "asset"

class Priority(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class Requirement:
    id: str
    title: str
    description: str = ""
    req_type: str = "feature"
    priority: str = "medium"
    acceptance_criteria: List[str] = field(default_factory=list)
    status: str = "pending"
    dependencies: List[str] = field(default_factory=list)
    estimated_complexity: str = "medium"

@dataclass
class Task:
    id: str
    title: str
    description: str = ""
    estimated_hours: int = 0
    assigned_role: str = "developer"
    related_files: List[str] = field(default_factory=list)
    test_plan: List[str] = field(default_factory=list)
    status: str = "pending"
    depends_on: List[str] = field(default_factory=list)
    acceptance_criteria: List[str] = field(default_factory=list)

@dataclass
class ExecutionRecord:
    task_id: str
    worker: str
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    status: str = "running"
    output: str = ""
    error: str = ""
    commit_id: Optional[str] = None

@dataclass
class ArchitectureDoc:
    modules: List[Dict] = field(default_factory=list)
    tech_stack: Dict = field(default_factory=dict)
    integration_points: List[str] = field(default_factory=list)
    task_breakdown_plan: List[str] = field(default_factory=list)

@dataclass
class ExecutionResult:
    task_id: str
    status: str  # success, failed, blocked
    commit_id: Optional[str] = None
    test_results: Dict = field(default_factory=dict)
    artifacts: List[str] = field(default_factory=list)
    token_usage: Dict = field(default_factory=dict)

@dataclass
class TestReport:
    task_id: str
    passed: int = 0
    failed: int = 0
    logs: str = ""
    screenshots: List[str] = field(default_factory=list)

@dataclass
class GameEvalReport:
    task_id: str
    fun_rating: int = 3  # 1-5
    control_feel: str = "unknown"
    visual_feedback_quality: str = "unknown"
    difficulty_balance: str = "unknown"
    suggestions: List[str] = field(default_factory=list)
    bugs: List[str] = field(default_factory=list)
