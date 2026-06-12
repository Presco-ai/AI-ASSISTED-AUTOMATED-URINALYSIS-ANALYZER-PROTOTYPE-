from datetime import datetime
from models.doctor import DoctorSignature
from models.patient import Patient

class PrintManager:
    def __init__(self):
        self.pdf_gen = None  # will be set lazily if needed

    def generate_html(self, report, patient=None, doctor=None, culture=None):
        dt = datetime.now().strftime("%d/%m/%Y")
        dn = doctor.name if doctor else "Dr. Precious Belema Ibiabuo"
        h = doctor.hospital if doctor else "University Teaching Hospital"

        html = f"""<!DOCTYPE html>
        <html><head><meta charset="UTF-8"><title>Urinalysis Report</title>
        <style>
        body{{font-family:Arial,Helvetica,sans-serif;font-size:10pt;padding:15px;max-width:800px;margin:0 auto;color:#333}}
        .header{{text-align:center;border-bottom:3px solid #1a237e;padding-bottom:10px;margin-bottom:20px}}
        .hospital{{font-size:16pt;font-weight:bold;color:#1a237e}}
        .section-title{{font-weight:bold;color:#1a237e;border-bottom:2px solid #1a237e;padding-bottom:5px;margin:20px 0 10px 0;font-size:13pt}}
        .diagnosis-box{{background:#ffebee;border:2px solid #d32f2f;padding:15px;margin:10px 0;border-radius:5px}}
        .normal{{color:#2e7d32;font-weight:bold}}.abnormal{{color:#d32f2f;font-weight:bold}}
        table{{width:100%;border-collapse:collapse;margin:10px 0}}
        th{{background:#333;color:white;padding:8px;text-align:left}}td{{padding:8px;border:1px solid #ddd}}
        .warning-box{{background:#fff3e0;border:1px solid #ff9800;padding:10px;margin:10px 0;border-radius:3px}}
        .signature{{margin-top:40px;border-top:2px solid #1a237e;padding-top:15px}}
        .footer{{font-size:8pt;color:#999;text-align:center;margin-top:20px}}
        </style></head><body>
        <div class="header">
            <div class="hospital">{h.upper()}</div>
            <div>Department of Pathology & Laboratory Medicine</div>
            <div style="font-size:14pt;color:#1a237e;margin-top:5px">COMPREHENSIVE URINALYSIS REPORT</div>
        </div>"""

        if patient:
            html += f"""
            <div class="section-title">PATIENT INFORMATION</div>
            <table>"""
            html += f"<tr><td style='width:25%'><b>Name:</b></td><td>{patient.get_full_name()}</td></tr>"
            html += f"<tr><td><b>ID:</b></td><td>{patient.patient_id}</td></tr>"
            html += f"<tr><td><b>Age/Sex:</b></td><td>{patient.get_age_display()}/{patient.sex.value}</td></tr>"
            html += f"<tr><td><b>Clinical History:</b></td><td>{patient.clinical_history or 'None'}</td></tr>"
            html += "</table>"

        diag = report.get('pathologic_diagnosis', {})
        if diag:
            html += f"""
            <div class="section-title">PATHOLOGIC DIAGNOSIS</div>
            <div class="diagnosis-box">
            <p><b>Primary Diagnosis:</b> {diag.get('diagnosis','N/A')} (ICD-10: {diag.get('icd10_code','N/A')})</p>
            <p><b>Confidence:</b> {diag.get('confidence','N/A')} ({diag.get('confidence_score',0)}%)</p>
            <p><b>Severity:</b> {diag.get('severity','N/A')} | <b>Urgency:</b> {diag.get('urgency','N/A')}</p>"""
            if diag.get('treatment_plan'):
                html += f"<p><b>Treatment:</b> {diag['treatment_plan']}</p>"
            html += "</div>"

        ua = report.get('urinalysis_results', {})
        if ua:
            html += '<div class="section-title">URINALYSIS (COLOR CHART)</div><table><tr><th>Parameter</th><th>Result</th><th>Status</th></tr>'
            for k, v in sorted(ua.items(), key=lambda x: x[1].get('pad_position', 0)):
                is_normal = v.get('is_normal', False)
                status_class = 'normal' if is_normal else 'abnormal'
                status_text = 'Normal' if is_normal else 'ABNORMAL'
                html += f"<tr><td>{k}</td><td>{v.get('value','N/A')} {v.get('unit','')}</td><td class='{status_class}'>{status_text}</td></tr>"
            html += "</table>"

        micro = report.get('microscopy_results', {})
        if micro:
            html += '<div class="section-title">URINE MICROSCOPY</div><table><tr><th>Parameter</th><th>Finding</th></tr>'
            for k, v in micro.items():
                if v != "None Seen":
                    html += f"<tr><td>{k}</td><td>{v}</td></tr>"
            html += "</table>"

        recs = report.get('clinical_recommendations', [])
        if recs:
            html += '<div class="section-title">CLINICAL RECOMMENDATIONS</div>'
            for i, rec in enumerate(recs, 1):
                html += f'<div class="warning-box"><p><b>{i}. [{rec.get("priority","N/A")}] {rec.get("category","")}</b></p><p>{rec.get("recommendation","N/A")}</p>'
                if rec.get('dosage_info'):
                    html += f'<p><b>Dosage:</b> {rec["dosage_info"]} | <b>Duration:</b> {rec.get("duration","N/A")}</p>'
                html += '</div>'

        fup = report.get('follow_up_plan', {})
        if fup:
            html += f'<div class="section-title">FOLLOW-UP</div><p><b>Recommended Date:</b> {fup.get("recommended_date","N/A")}</p>'
            html += f'<p><b>Tests to Repeat:</b> {", ".join(fup.get("tests_to_repeat",[]))}</p>'
            if fup.get('additional_tests'):
                html += f'<p><b>Additional Tests:</b> {", ".join(fup["additional_tests"])}</p>'

        html += f"""
        <div class="signature">
            <b>Signed:</b><br>{dn}<br>{doctor.credentials if doctor else 'MLT, B.Sc., M.Sc., MD'}<br>Date: {dt}
        </div>
        <div class="footer">Report ID: {report.get('report_id','N/A')} | AI Urinalysis Pro v3.0</div>
        </body></html>"""
        return html

    def save_html(self, html, path):
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(html)
            return True
        except:
            return False

    def generate_pdf(self, report, patient=None, doctor=None, culture=None):
        from reporting.pdf_generator import PDFReportGenerator
        if not patient:
            patient = Patient()
        if not doctor:
            doctor = DoctorSignature()
        gen = PDFReportGenerator()
        return gen.generate(report, patient, doctor, culture)
