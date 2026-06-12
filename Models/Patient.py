from dataclasses import dataclass, field
from datetime import datetime
from .enums import Sex

@dataclass
class Patient:
    surname: str = ""
    first_name: str = ""
    middle_name: str = ""
    patient_id: str = ""
    age: int = 0
    age_unit: str = "Years"
    sex: Sex = Sex.MALE
    date_of_birth: str = ""
    hospital_number: str = ""
    contact_phone: str = ""
    contact_email: str = ""
    address: str = ""
    referring_doctor: str = ""
    referring_hospital: str = ""
    clinical_history: str = ""
    current_medications: str = ""
    allergies: str = ""
    pregnancy_status: str = "Not Applicable"
    chronic_conditions: str = ""
    previous_uti_count: int = 0
    registration_date: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    culture_ids: str = ""
    last_urinalysis_date: str = ""

    def get_full_name(self) -> str:
        parts = [p for p in [self.surname.upper(), self.first_name, self.middle_name] if p]
        return " ".join(parts) if parts else "Unknown"

    def get_age_display(self) -> str:
        return f"{self.age} {self.age_unit}" if self.age > 0 else "Adult"

    def get_age_in_years(self) -> float:
        if self.age_unit == "Years": return float(self.age)
        elif self.age_unit == "Months": return self.age / 12.0
        elif self.age_unit == "Days": return self.age / 365.0
        return 0.0

    def is_pregnant(self) -> bool:
        return self.pregnancy_status in ["Pregnant", "First Trimester", "Second Trimester", "Third Trimester"]

    def add_culture_id(self, cid: str):
        if self.culture_ids:
            ids = self.culture_ids.split(',')
            if cid not in ids:
                ids.append(cid)
            self.culture_ids = ','.join(ids)
        else:
            self.culture_ids = cid
