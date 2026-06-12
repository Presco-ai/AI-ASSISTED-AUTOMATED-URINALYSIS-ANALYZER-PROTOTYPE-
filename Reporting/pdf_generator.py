import os
REPORTLAB_AVAILABLE = False
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors as rl_colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    from reportlab.lib.enums import TA_CENTER
    REPORTLAB_AVAILABLE = True
except ImportError:
    pass

class PDFReportGenerator:
    def __init__(self):
        self.available = REPORTLAB_AVAILABLE

    def generate(self, report, patient, doctor, culture=None, path=None):
        if not self.available:
            return None
        if not path:
            path = os.path.join(os.path.expanduser('~'), f"Urinalysis_Report_{report.get('report_id','unknown')}.pdf")
        try:
            doc = SimpleDocTemplate(path, pagesize=A4, rightMargin=15*mm, leftMargin=15*mm,
                                    topMargin=15*mm, bottomMargin=15*mm)
            styles = getSampleStyleSheet()
            elements = []

            elements.append(Paragraph(doctor.hospital.upper(),
                ParagraphStyle('H', parent=styles['Heading1'], fontSize=16,
                               textColor=rl_colors.HexColor('#1a237e'), alignment=TA_CENTER)))
            elements.append(Paragraph("COMPREHENSIVE URINALYSIS REPORT",
                ParagraphStyle('T', parent=styles['Heading2'], fontSize=14,
                               alignment=TA_CENTER, textColor=rl_colors.HexColor('#1a237e'))))
            elements.append(HRFlowable(width="100%", thickness=1.5, color=rl_colors.HexColor('#1a237e')))
            elements.append(Spacer(1, 5*mm))

            if patient and patient.patient_id:
                pd = [
                    [Paragraph("<b>Name:</b>", styles['Normal']), Paragraph(patient.get_full_name(), styles['Normal'])],
                    [Paragraph("<b>ID:</b>", styles['Normal']), Paragraph(patient.patient_id, styles['Normal'])],
                    [Paragraph("<b>Age/Sex:</b>", styles['Normal']), Paragraph(f"{patient.get_age_display()}/{patient.sex.value}", styles['Normal'])],
                ]
                pt = Table(pd, colWidths=[50*mm, 125*mm])
                pt.setStyle(TableStyle([('BACKGROUND',(0,0),(0,-1), rl_colors.HexColor('#f5f5f5')),
                                        ('GRID',(0,0),(-1,-1),0.5, rl_colors.HexColor('#cccccc'))]))
                elements.append(pt)
                elements.append(Spacer(1, 5*mm))

            diag = report.get('pathologic_diagnosis', {})
            if diag:
                elements.append(Paragraph("PATHOLOGIC DIAGNOSIS",
                    ParagraphStyle('PD', parent=styles['Heading3'], fontSize=13,
                                   textColor=rl_colors.HexColor('#d32f2f'))))
                elements.append(Paragraph(f"<b>Diagnosis:</b> {diag.get('diagnosis','N/A')} (ICD-10: {diag.get('icd10_code','N/A')})", styles['Normal']))
                elements.append(Paragraph(f"<b>Confidence:</b> {diag.get('confidence','N/A')} ({diag.get('confidence_score',0)}%)", styles['Normal']))
                if diag.get('treatment_plan'):
                    elements.append(Paragraph(f"<b>Treatment:</b> {diag['treatment_plan']}", styles['Normal']))
                elements.append(Spacer(1, 5*mm))

            imp = report.get('impression', '')
            if imp:
                elements.append(Paragraph("COMPREHENSIVE RESULTS",
                    ParagraphStyle('S4', parent=styles['Heading3'], fontSize=12, textColor=rl_colors.red)))
                for line in imp.split('\n'):
                    if line.strip():
                        elements.append(Paragraph(line, ParagraphStyle('Imp', parent=styles['Normal'], fontSize=8)))

            elements.append(Spacer(1, 10*mm))
            elements.append(Paragraph(f"<b>Electronically Signed By:</b><br/>{doctor.name}<br/>{doctor.credentials}<br/>{doctor.title}<br/>License: {doctor.license_number}", styles['Normal']))
            doc.build(elements)
            return path
        except Exception as e:
            print(f"PDF Error: {e}")
            return None
