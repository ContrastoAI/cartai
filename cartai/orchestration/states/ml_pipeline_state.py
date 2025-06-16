"""ML Pipeline state for cross-domain workflows"""

from typing import Any, List, Dict
from .base_state import BaseState


class MLPipelineState(BaseState):
    """Enhanced state for ML pipeline workflows with cross-domain data"""

    # Core identifiers
    experiment_id: str
    model_name: str
    run_id: str

    # Data quality (Governance)
    data_quality_status: str
    data_quality_score: float

    # Model monitoring (Observability)
    model_metrics: Dict[str, Any]
    system_health: str

    # Drift detection (Cross-domain)
    drift_detected: bool
    drift_alerts: List[Dict[str, Any]]
    drift_score: float

    # Governance decisions
    policy_violations: List[Dict[str, Any]]
    compliance_status: str
    governance_decision: str

    # Cross-domain coordination
    cross_domain_decision: str
    decision_reason: str
    actions_taken: List[str]

    # Workflow metadata
    current_agent: str
    workflow_stage: str
    error_messages: List[str]
