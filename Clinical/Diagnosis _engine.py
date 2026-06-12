from models.enums import DiagnosisConfidence, RiskLevel, FollowUpPriority
from models.diagnosis import PathologicDiagnosis

class PathologicDiagnosisEngine:
    def generate_diagnosis(self, report, patient=None, culture=None):
        micro = report.get("microscopy_results", {})
        strip = report.get("urinalysis_results", {})

        has_pyuria = any(x in str(micro.get("Pus Cells (WBCs)","")) for x in ["Numerous","Moderate"])
        has_bacteria = any(x in str(micro.get("Bacteria","")) for x in ["Numerous","Moderate"])
        has_yeast = micro.get("Candida Yeast Cells","") not in ["","None Seen","Negative"]
        has_nitrite = any(not v.get("is_normal",True) for k,v in strip.items() if "Nitrite" in k)
        has_leuko = any(not v.get("is_normal",True) for k,v in strip.items() if "Leukocytes" in k)
        has_blood = any(not v.get("is_normal",True) for k,v in strip.items() if "Blood" in k)
        has_protein = any(not v.get("is_normal",True) for k,v in strip.items() if "Protein" in k)
        has_glucose = any(not v.get("is_normal",True) for k,v in strip.items() if "Glucose" in k)
        has_ketones = any(not v.get("is_normal",True) for k,v in strip.items() if "Ketones" in k)

        pregnancy_note = ""
        if patient and patient.is_pregnant():
            pregnancy_note = " | PREGNANT - Avoid fluoroquinolones and tetracyclines"
        diabetes_note = ""
        if patient and "diabetes" in (patient.chronic_conditions or "").lower():
            diabetes_note = " | DIABETIC - Optimize glycemic control"

        # UTI
        if has_pyuria and has_bacteria and (has_nitrite or has_leuko):
            evidence = ["Pyuria detected","Bacteriuria present"]
            if has_nitrite: evidence.append("Nitrite positive - gram-negative bacteriuria")
            if has_leuko: evidence.append("Leukocyte esterase positive")
            if has_blood: evidence.append("Hematuria present")
            treatment = "Nitrofurantoin 100mg BID x 5 days OR Fosfomycin 3g single dose"
            if patient and patient.is_pregnant():
                treatment = "Cefuroxime 250mg BID x 7 days (pregnancy-safe)"
            return PathologicDiagnosis(
                diagnosis="Acute Cystitis (Urinary Tract Infection)", icd10_code="N30.0",
                confidence=DiagnosisConfidence.HIGH, confidence_score=88.0,
                supporting_evidence=evidence,
                differential_diagnoses=[("Acute Pyelonephritis",15.0),("Urethritis",10.0)],
                severity=RiskLevel.MODERATE, requires_culture=True,
                urgency=FollowUpPriority.SHORT_TERM,
                notes=f"Start empiric antibiotics.{pregnancy_note}{diabetes_note}",
                treatment_plan=treatment
            )
        # Candiduria
        if has_yeast:
            return PathologicDiagnosis(
                diagnosis="Candiduria (Fungal UTI)", icd10_code="B37.4",
                confidence=DiagnosisConfidence.HIGH, confidence_score=85.0,
                supporting_evidence=["Yeast cells detected on microscopy"],
                severity=RiskLevel.LOW, requires_culture=True,
                urgency=FollowUpPriority.SHORT_TERM,
                notes="Confirm with fungal culture. Treat with Fluconazole 200mg x 7-14 days if symptomatic.",
                treatment_plan="Fluconazole 200mg daily x 7-14 days"
            )
        # DKA risk
        if has_glucose and has_ketones:
            return PathologicDiagnosis(
                diagnosis="Glycosuria with Ketonuria - Rule out DKA", icd10_code="R81",
                confidence=DiagnosisConfidence.MODERATE, confidence_score=70.0,
                supporting_evidence=["Glucose in urine","Ketones in urine"],
                severity=RiskLevel.HIGH, urgency=FollowUpPriority.URGENT,
                notes="Check blood glucose and ketones immediately. Refer to ER if elevated.",
                treatment_plan="Check blood glucose STAT. If >250mg/dL with ketones, refer to Emergency Department."
            )
        # Hematuria
        if has_blood and not has_pyuria:
            return PathologicDiagnosis(
                diagnosis="Hematuria - Requires Investigation", icd10_code="R31",
                confidence=DiagnosisConfidence.MODERATE, confidence_score=65.0,
                supporting_evidence=["Blood detected on dipstick","No significant pyuria"],
                severity=RiskLevel.MODERATE, requires_imaging=True,
                urgency=FollowUpPriority.SHORT_TERM,
                notes="Microscopic confirmation required. Consider CT KUB and urology referral.",
                treatment_plan="Renal ultrasound + CT KUB. Urology referral if persistent."
            )
        # Proteinuria
        if has_protein and not has_pyuria:
            return PathologicDiagnosis(
                diagnosis="Proteinuria - Evaluate for Renal Disease", icd10_code="R80.9",
                confidence=DiagnosisConfidence.MODERATE, confidence_score=60.0,
                supporting_evidence=["Protein detected on dipstick"],
                severity=RiskLevel.MODERATE,
                urgency=FollowUpPriority.ROUTINE,
                notes="Quantify with UPCR. Check eGFR, serum albumin. Nephrology referral if persistent.",
                treatment_plan="UPCR quantification. ACEi/ARB if diabetic or hypertensive. Monitor renal function."
            )
        # Normal
        return PathologicDiagnosis(
            diagnosis="Normal Urinalysis", icd10_code="Z00.0",
            confidence=DiagnosisConfidence.HIGH, confidence_score=90.0,
            supporting_evidence=["All parameters within normal limits"],
            severity=RiskLevel.LOW, urgency=FollowUpPriority.ROUTINE,
            notes="No significant abnormalities detected."
        )
