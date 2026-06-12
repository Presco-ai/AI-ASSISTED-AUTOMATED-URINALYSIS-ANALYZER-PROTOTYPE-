from dataclasses import dataclass, field
from typing import List, Tuple
from .enums import DiagnosisConfidence, RiskLevel, FollowUpPriority

@dataclass
class PathologicDiagnosis:
    diagnosis: str = ""
    icd10_code: str = ""
    confidence: DiagnosisConfidence = DiagnosisConfidence.UNCERTAIN
    confidence_score: float = 0.0
    supporting_evidence: List[str] = field(default_factory=list)
    differential_diagnoses: List[Tuple[str, float]] = field(default_factory=list)
    severity: RiskLevel = RiskLevel.LOW
    requires_culture: bool = False
    requires_imaging: bool = False
    requires_referral: bool = False
    specialist_type: str = ""
    urgency: FollowUpPriority = FollowUpPriority.ROUTINE
    notes: str = ""
    treatment_plan: str = ""
