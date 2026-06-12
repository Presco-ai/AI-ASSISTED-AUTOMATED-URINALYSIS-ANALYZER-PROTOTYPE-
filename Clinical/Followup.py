from datetime import datetime, timedelta
from models.clinical import FollowUpPlan
from models.enums import FollowUpPriority, RiskLevel

class FollowUpPlanner:
    def generate_plan(self, diagnosis, patient=None, culture=None):
        plan = FollowUpPlan()
        days_map = {
            FollowUpPriority.IMMEDIATE: 0,
            FollowUpPriority.URGENT: 3,
            FollowUpPriority.SHORT_TERM: 10,
            FollowUpPriority.ROUTINE: 21
        }
        days = days_map.get(diagnosis.urgency, 14)
        plan.recommended_date = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
        plan.tests_to_repeat = ["Urinalysis with microscopy"]
        if diagnosis.requires_culture:
            plan.tests_to_repeat.append("Urine culture and sensitivity")
        if diagnosis.requires_imaging:
            plan.additional_tests.append("Renal ultrasound / CT KUB")
        if diagnosis.severity in [RiskLevel.LOW, RiskLevel.MODERATE]:
            plan.telemedicine_option = True
        plan.patient_instructions = "Complete all medications. Return for follow-up as scheduled."
        return plan
