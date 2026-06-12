from dataclasses import dataclass, field
from typing import List

@dataclass
class ClinicalRecommendation:
    category: str = ""
    recommendation: str = ""
    priority: str = ""
    evidence_level: str = ""
    rationale: str = ""
    contraindications: List[str] = field(default_factory=list)
    dosage_info: str = ""
    duration: str = ""
    monitoring_required: List[str] = field(default_factory=list)

@dataclass
class ClinicalAdvice:
    category: str = ""
    advice: str = ""
    importance: str = ""
    warning_signs: List[str] = field(default_factory=list)
    when_to_seek_care: str = ""

@dataclass
class FollowUpPlan:
    priority: FollowUpPriority = FollowUpPriority.ROUTINE
    recommended_date: str = ""
    tests_to_repeat: List[str] = field(default_factory=list)
    additional_tests: List[str] = field(default_factory=list)
    referral_needed: bool = False
    referral_specialty: str = ""
    patient_instructions: str = ""
    telemedicine_option: bool = False
