from models.clinical import ClinicalRecommendation

class ClinicalRecommendationsEngine:
    def generate_recommendations(self, report, patient=None, culture=None):
        recs = []
        micro = report.get("microscopy_results", {})
        strip = report.get("urinalysis_results", {})
        has_uti = any(x in str(micro.get(k,"")) for k in ["Pus Cells (WBCs)","Bacteria"] for x in ["Numerous","Moderate"])
        has_protein = any(not v.get("is_normal",True) for k,v in strip.items() if "Protein" in k)
        has_glucose = any(not v.get("is_normal",True) for k,v in strip.items() if "Glucose" in k)
        has_blood = any(not v.get("is_normal",True) for k,v in strip.items() if "Blood" in k)

        if has_uti:
            recs.append(ClinicalRecommendation(
                category="Antimicrobial Therapy",
                recommendation="Nitrofurantoin 100mg BID x 5 days or Fosfomycin 3g single dose",
                priority="HIGH", evidence_level="Level I (RCTs)",
                rationale="IDSA guidelines for uncomplicated UTI.",
                dosage_info="Nitrofurantoin 100mg BID OR Fosfomycin 3g once",
                duration="5 days (Nitrofurantoin) or Single dose (Fosfomycin)",
                contraindications=["eGFR <30","Pregnancy near term","G6PD deficiency"],
                monitoring_required=["Symptom improvement 48-72h","Culture results"]
            ))
            recs.append(ClinicalRecommendation(
                category="Hydration",
                recommendation="Increase fluid intake to 2-3 liters daily",
                priority="MODERATE", rationale="Helps flush bacteria."
            ))
        if has_protein:
            recs.append(ClinicalRecommendation(
                category="Renal Evaluation",
                recommendation="Quantify proteinuria with UPCR",
                priority="MODERATE",
                monitoring_required=["UPCR","eGFR","Blood pressure"]
            ))
        if has_glucose:
            recs.append(ClinicalRecommendation(
                category="Diabetes Management",
                recommendation="Check HbA1c and optimize glycemic control",
                priority="HIGH",
                monitoring_required=["HbA1c","Fasting glucose"]
            ))
        if has_blood:
            recs.append(ClinicalRecommendation(
                category="Hematuria Workup",
                recommendation="Microscopic confirmation and imaging",
                priority="MODERATE"
            ))
        return recs
