from enum import Enum

class Sex(Enum):
    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Other"

class CultureStatus(Enum):
    PENDING = "Pending"
    SCANTY = "Scanty"
    FEW = "Few"
    MODERATE = "Moderate"
    PROFUSE = "Profuse"
    NEGATIVE = "Negative - No Growth"
    POSITIVE = "Positive - Growth Detected"

class SensitivityResult(Enum):
    SENSITIVE = "S"
    INTERMEDIATE = "I"
    RESISTANT = "R"
    NOT_TESTED = "NT"

class ConnectionType(Enum):
    BLUETOOTH = "Bluetooth"
    WIFI = "WiFi"
    USB = "USB"
    NONE = "None"

class RiskLevel(Enum):
    LOW = "Low Risk"
    MODERATE = "Moderate Risk"
    HIGH = "High Risk"
    CRITICAL = "Critical Risk"
    URGENT = "Urgent - Immediate Attention Required"

class DiagnosisConfidence(Enum):
    DEFINITE = "Definite (95-100%)"
    HIGH = "High Probability (75-94%)"
    MODERATE = "Moderate Probability (50-74%)"
    LOW = "Low Probability (25-49%)"
    UNCERTAIN = "Uncertain (<25%)"

class FollowUpPriority(Enum):
    ROUTINE = "Routine (2-4 weeks)"
    SHORT_TERM = "Short-term (1-2 weeks)"
    URGENT = "Urgent (24-72 hours)"
    IMMEDIATE = "Immediate (Same day)"
    REFERRAL = "Specialist Referral Required"
