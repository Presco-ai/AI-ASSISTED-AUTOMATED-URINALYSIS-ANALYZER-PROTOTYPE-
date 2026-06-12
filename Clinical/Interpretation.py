from datetime import datetime
from .diagnosis_engine import PathologicDiagnosisEngine
from .recommendations import ClinicalRecommendationsEngine
from .advisory import ClinicalAdvisorySystem
from .followup import FollowUpPlanner

class EnhancedInterpretationEngine:
    def __init__(self):
        self.diagnosis_engine = PathologicDiagnosisEngine()
        self.recommendations_engine = ClinicalRecommendationsEngine()
        self.advisory_system = ClinicalAdvisorySystem()
        self.followup_planner = FollowUpPlanner()

    def generate_comprehensive_report(self, micro, strip, patient=None, culture=None):
        microscopy = micro.get("microscopy_results", {}) if micro else {}
        urinalysis = strip.get("results", {}) if strip else {}

        diagnosis = self.diagnosis_engine.generate_diagnosis(
            {"microscopy_results": microscopy, "urinalysis_results": urinalysis},
            patient, culture
        )
        recommendations = self.recommendations_engine.generate_recommendations(
            {"microscopy_results": microscopy, "urinalysis_results": urinalysis},
            patient, culture
        )
        advice = self.advisory_system.generate_advice(
            {"microscopy_results": microscopy, "urinalysis_results": urinalysis},
            patient, diagnosis
        )
        followup = self.followup_planner.generate_plan(diagnosis, patient, culture)

        # Build impression text
        lines = [
            "="*60, "COMPREHENSIVE URINALYSIS REPORT", "="*60,
            f"Date: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
            "", f"PRIMARY DIAGNOSIS: {diagnosis.diagnosis}",
            f"ICD-10 CODE: {diagnosis.icd10_code}",
            f"CONFIDENCE: {diagnosis.confidence.value} ({diagnosis.confidence_score}%)",
            f"SEVERITY: {diagnosis.severity.value}",
            f"URGENCY: {diagnosis.urgency.value}",
            "", "SUPPORTING EVIDENCE:",
        ]
        for ev in diagnosis.supporting_evidence:
            lines.append(f"  • {ev}")
        if diagnosis.treatment_plan:
            lines.extend(["", f"RECOMMENDED TREATMENT: {diagnosis.treatment_plan}"])
        if diagnosis.notes:
            lines.extend(["", f"CLINICAL NOTES: {diagnosis.notes}"])

        lines.extend(["", "-"*60, "MICROSCOPY FINDINGS:"])
        for k,v in microscopy.items():
            if v != "None Seen":
                lines.append(f"  • {k}: {v}")
        lines.extend(["", "-"*60, "URINALYSIS (COLOR CHART):"])
        abnormal_count = 0
        for k,v in sorted(urinalysis.items(), key=lambda x: x[1].get('pad_position',0)):
            status = "✓" if v.get('is_normal',False) else "✗ ABNORMAL"
            if not v.get('is_normal',False):
                abnormal_count += 1
            lines.append(f"  [{status}] {k}: {v.get('value','N/A')} {v.get('unit','')}")
        lines.append(f"  Total Abnormal Parameters: {abnormal_count}/{len(urinalysis)}")

        lines.extend(["", "-"*60, "CLINICAL RECOMMENDATIONS:"])
        for i,rec in enumerate(recommendations,1):
            lines.append(f"  {i}. [{rec.priority}] {rec.recommendation}")
            if rec.dosage_info:
                lines.append(f"     Dosage: {rec.dosage_info}")
        lines.extend(["", "-"*60, "PATIENT ADVICE:"])
        for i,adv in enumerate(advice,1):
            lines.append(f"  {i}. [{adv.importance}] {adv.advice}")
        lines.extend(["", "-"*60, f"FOLLOW-UP: {followup.priority.value}"])
        lines.append(f"  Recommended Date: {followup.recommended_date}")
        lines.append(f"  Tests to Repeat: {', '.join(followup.tests_to_repeat)}")
        lines.append("="*60)

        rid = f"RPT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        return {
            "report_id": rid,
            "report_date": datetime.now().strftime("%Y-%m-%d"),
            "report_time": datetime.now().strftime("%H:%M:%S"),
            "risk_level": diagnosis.severity.value,
            "microscopy_results": microscopy,
            "urinalysis_results": urinalysis,
            "impression": "\n".join(lines),
            "pathologic_diagnosis": {
                "diagnosis": diagnosis.diagnosis,
                "icd10_code": diagnosis.icd10_code,
                "confidence": diagnosis.confidence.value,
                "confidence_score": diagnosis.confidence_score,
                "severity": diagnosis.severity.value,
                "urgency": diagnosis.urgency.value,
                "requires_culture": diagnosis.requires_culture,
                "notes": diagnosis.notes,
                "treatment_plan": diagnosis.treatment_plan
            },
            "clinical_recommendations": [
                {"category": r.category, "recommendation": r.recommendation,
                 "priority": r.priority, "dosage_info": r.dosage_info, "duration": r.duration}
                for r in recommendations
            ],
            "clinical_advice": [
                {"category": a.category, "advice": a.advice, "importance": a.importance,
                 "warning_signs": a.warning_signs, "when_to_seek_care": a.when_to_seek_care}
                for a in advice
            ],
            "follow_up_plan": {
                "priority": followup.priority.value,
                "recommended_date": followup.recommended_date,
                "tests_to_repeat": followup.tests_to_repeat,
                "additional_tests": followup.additional_tests,
                "telemedicine_option": followup.telemedicine_option
            },
            "culture_status": culture.culture_status.value if culture else "PENDING",
            "ai_model": micro.get("ai_model", "Standard AI"),
            "patient_info": patient.get_full_name() if patient else ""
        }
