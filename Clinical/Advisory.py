from models.clinical import ClinicalAdvice

class ClinicalAdvisorySystem:
    def generate_advice(self, report, patient=None, diagnosis=None):
        advice_list = []
        micro = report.get("microscopy_results", {})
        has_uti = any(x in str(micro.get(k,"")) for k in ["Pus Cells (WBCs)","Bacteria"] for x in ["Numerous","Moderate"])

        if has_uti:
            advice_list.append(ClinicalAdvice(
                category="UTI Prevention",
                advice="Drink 2-3L water daily. Void regularly. Wipe front-to-back. Empty bladder after intercourse.",
                importance="HIGH",
                warning_signs=["Fever >38°C","Flank pain","Vomiting","No improvement in 48-72h"],
                when_to_seek_care="Return if fever, severe pain, or vomiting develop."
            ))
            if patient and patient.is_pregnant():
                advice_list.append(ClinicalAdvice(
                    category="Pregnancy Considerations",
                    advice="UTI in pregnancy requires aggressive treatment. Complete all antibiotics.",
                    importance="CRITICAL",
                    warning_signs=["Fever","Contractions","Decreased fetal movement"],
                    when_to_seek_care="Contact obstetric provider immediately."
                ))
        advice_list.append(ClinicalAdvice(
            category="General Health",
            advice="Maintain healthy diet, exercise, adequate sleep.",
            importance="MODERATE",
            when_to_seek_care="Follow up as scheduled."
        ))
        return advice_list
