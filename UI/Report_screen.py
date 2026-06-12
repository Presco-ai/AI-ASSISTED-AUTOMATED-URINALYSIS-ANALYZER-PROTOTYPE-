from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.app import App
import os
import json
import threading
import numpy as np
from clinical.interpretation import EnhancedInterpretationEngine
from reporting.html_generator import PrintManager
from models.doctor import DoctorSignature
from models.patient import Patient
from utils.file_viewer import FileViewer
from .common import RoundedButton

class CombinedReportScreen(BoxLayout):
    def __init__(self, app, **kw):
        super().__init__(**kw)
        self.app = app
        self.current_report = None
        self.orientation = 'vertical'
        self.padding = 15
        self.spacing = 10

        self.add_widget(Label(text='[b]COMPREHENSIVE URINALYSIS REPORT[/b]', markup=True, size_hint_y=0.06,
                              font_size='18sp', color=(0.1,0.4,0.8,1)))
        self.status_label = Label(text='Analyze both microscopy and urinalysis first', size_hint_y=0.05, color=(0.7,0.5,0,1))
        self.add_widget(self.status_label)

        btn_grid = GridLayout(cols=4, spacing=10, size_hint_y=0.08)
        self.generate_btn = RoundedButton(text='Generate', on_press=self.generate, disabled=True, background_color=(0.5,0.5,0.5,1))
        self.preview_btn = RoundedButton(text='Preview', on_press=self.preview, disabled=True, background_color=(0.3,0.6,0.9,1))
        self.pdf_btn = RoundedButton(text='PDF', on_press=self.make_pdf, disabled=True, background_color=(0.8,0.2,0.2,1))
        self.export_btn = RoundedButton(text='Export JSON', on_press=self.export_json, disabled=True, background_color=(0.9,0.5,0.1,1))
        for b in [self.generate_btn, self.preview_btn, self.pdf_btn, self.export_btn]:
            btn_grid.add_widget(b)
        self.add_widget(btn_grid)

        sv = ScrollView(size_hint_y=0.6)
        self.results_layout = GridLayout(cols=1, spacing=5, size_hint_y=None, padding=10)
        self.results_layout.bind(minimum_height=self.results_layout.setter('height'))
        sv.add_widget(self.results_layout)
        self.add_widget(sv)

        Clock.schedule_interval(self._check_ready, 1)

    def _check_ready(self, dt):
        if hasattr(self.app, 'microscopy_screen') and hasattr(self.app, 'strip_screen'):
            if self.app.microscopy_screen.current_image is not None and self.app.strip_screen.current_image is not None:
                self.generate_btn.disabled = False
                self.generate_btn.background_color = (0.2,0.7,0.3,1)
                self.status_label.text = 'Ready - Click Generate'
                self.status_label.color = (0,0.7,0,1)

    def generate(self, inst):
        try:
            mr = getattr(self.app.microscopy_screen, 'current_result', {}) or {}
            sr = getattr(self.app.strip_screen, 'current_result', {}) or {}
            p = getattr(self.app, 'current_patient', None)
            c = getattr(self.app, 'current_culture', None)
            engine = EnhancedInterpretationEngine()
            report = engine.generate_comprehensive_report(mr, sr, p, c)
            self.current_report = report
            self.results_layout.clear_widgets()

            diag = report.get('pathologic_diagnosis', {})
            if diag:
                self._add_label("PATHOLOGIC DIAGNOSIS", "", (0.8,0.1,0.1,1), '13sp')
                self._add_label(f"Diagnosis: {diag.get('diagnosis','N/A')}",
                                f"ICD-10: {diag.get('icd10_code','N/A')} | Confidence: {diag.get('confidence_score',0)}%",
                                (0.2,0.2,0.2,1), '11sp')
                self._add_label(f"Severity: {diag.get('severity','N/A')} | Urgency: {diag.get('urgency','N/A')}",
                                "", (0.9,0.3,0,1), '11sp')
                if diag.get('treatment_plan'):
                    self._add_label("Treatment Plan:", diag['treatment_plan'], (0.1,0.6,0.1,1), '11sp')
                if diag.get('notes'):
                    self._add_label("Clinical Notes:", diag['notes'], (0.5,0.3,0.1,1), '10sp')

            if p:
                info = f"Name: {p.get_full_name()}\nID: {p.patient_id} | Age: {p.get_age_display()} | Sex: {p.sex.value}\n"
                info += f"Clinical History: {p.clinical_history or 'None'}\nAllergies: {p.allergies or 'None'}"
                self._add_label("PATIENT INFORMATION", info, (0.2,0.2,0.2,1))

            micro = report.get('microscopy_results', {})
            if micro:
                text = "URINE MICROSCOPY\n" + "-"*30 + "\n"
                for k,v in micro.items():
                    if v != "None Seen":
                        text += f"  • {k}: {v}\n"
                self._add_label("", text, (0.1,0.1,0.1,1), '10sp')

            ua = report.get('urinalysis_results', {})
            if ua:
                text = "URINALYSIS (COLOR CHART)\n" + "-"*30 + "\n"
                abnormal = 0
                for k,v in sorted(ua.items(), key=lambda x: x[1].get('pad_position',0)):
                    st = "OK" if v.get('is_normal',False) else "ABN"
                    if not v.get('is_normal',False):
                        abnormal += 1
                    text += f"  [{st}] {k}: {v.get('value','N/A')} {v.get('unit','')}\n"
                text += f"\nAbnormal: {abnormal}/{len(ua)}"
                self._add_label("", text, (0.1,0.1,0.1,1), '10sp')

            recs = report.get('clinical_recommendations', [])
            if recs:
                text = "RECOMMENDATIONS\n" + "-"*30 + "\n"
                for i,rec in enumerate(recs,1):
                    text += f"  {i}. [{rec.get('priority','')}] {rec.get('recommendation','')}\n"
                    if rec.get('dosage_info'):
                        text += f"     Dosage: {rec['dosage_info']}\n"
                self._add_label("", text, (0.1,0.2,0.1,1), '10sp')

            fup = report.get('follow_up_plan', {})
            if fup:
                text = "FOLLOW-UP\n" + "-"*30 + "\n"
                text += f"  Date: {fup.get('recommended_date','')}\n"
                text += f"  Tests: {', '.join(fup.get('tests_to_repeat',[]))}\n"
                self._add_label("", text, (0.5,0.1,0.5,1), '10sp')

            self._add_label("SIGNATURE", "Dr. Precious Belema Ibiabuo\nMLT, B.Sc., M.Sc., MD\nConsultant Pathologist\n" + report['report_date'],
                            (0.1,0.2,0.5,1), '11sp')

            for btn in [self.preview_btn, self.pdf_btn, self.export_btn]:
                btn.disabled = False
            self.preview_btn.background_color = (0.3,0.6,0.9,1)
            self.pdf_btn.background_color = (0.8,0.2,0.2,1)
            self.export_btn.background_color = (0.9,0.5,0.1,1)

            # Save to DB
            try:
                self.app.db.save_report(report['report_id'], p.patient_id if p else '', report)
                if fup.get('recommended_date'):
                    self.app.db.save_followup(report['report_id'], p.patient_id if p else '', fup['recommended_date'])
            except Exception as e:
                print(f"DB save error: {e}")

            Popup(title='Report Generated', content=Label(text=f"Report Ready!\nDiagnosis: {diag.get('diagnosis','N/A')}"),
                  size_hint=(0.8,0.5)).open()
        except Exception as e:
            Popup(title='Error', content=Label(text=f'Failed: {str(e)}'), size_hint=(0.8,0.4)).open()

    def preview(self, inst):
        if not self.current_report:
            Popup(title='No Report', content=Label(text='Generate report first.'), size_hint=(0.7,0.3)).open()
            return
        try:
            p = getattr(self.app, 'current_patient', None)
            doctor = DoctorSignature()
            pm = PrintManager()
            html = pm.generate_html(self.current_report, p, doctor)
            preview_dir = os.path.join(os.path.expanduser('~'), 'urinalysis_previews')
            os.makedirs(preview_dir, exist_ok=True)
            fp = os.path.join(preview_dir, f"preview_{self.current_report.get('report_id','temp')}.html")
            if pm.save_html(html, fp):
                FileViewer.open_file(fp)
                Popup(title='Preview', content=Label(text='HTML preview opened!'), size_hint=(0.7,0.3)).open()
            else:
                Popup(title='Error', content=Label(text='Failed to save preview.'), size_hint=(0.7,0.3)).open()
        except Exception as e:
            Popup(title='Error', content=Label(text=f'Preview failed: {str(e)}'), size_hint=(0.8,0.4)).open()

    def make_pdf(self, inst):
        if not self.current_report:
            Popup(title='No Report', content=Label(text='Generate report first.'), size_hint=(0.7,0.3)).open()
            return
        lp = Popup(title='Generating PDF', content=Label(text='Please wait...'), size_hint=(0.6,0.3))
        lp.open()
        def _run():
            try:
                p = getattr(self.app, 'current_patient', Patient())
                doctor = DoctorSignature()
                pm = PrintManager()
                pdf_path = pm.generate_pdf(self.current_report, p, doctor)
                if pdf_path and os.path.exists(pdf_path):
                    Clock.schedule_once(lambda dt: self._pdf_success(pdf_path, lp), 0)
                else:
                    Clock.schedule_once(lambda dt: self._pdf_error(lp), 0)
            except Exception as e:
                Clock.schedule_once(lambda dt: self._pdf_error(lp, str(e)), 0)
        threading.Thread(target=_run, daemon=True).start()

    def _pdf_success(self, path, popup):
        popup.dismiss()
        Popup(title='PDF Generated', content=Label(text=f'PDF ready!\n\n{path}'), size_hint=(0.8,0.5)).open()
        FileViewer.open_file(path)

    def _pdf_error(self, popup, msg=""):
        popup.dismiss()
        Popup(title='PDF Error', content=Label(text=f'PDF failed.\n\n{msg}\nInstall reportlab'), size_hint=(0.8,0.5)).open()

    def export_json(self, inst):
        if not self.current_report:
            Popup(title='No Report', content=Label(text='Generate report first.'), size_hint=(0.7,0.3)).open()
            return
        try:
            export_dir = os.path.join(os.path.expanduser('~'), 'urinalysis_exports')
            os.makedirs(export_dir, exist_ok=True)
            fp = os.path.join(export_dir, f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            def convert(obj):
                if isinstance(obj, dict):
                    return {k: convert(v) for k,v in obj.items()}
                elif isinstance(obj, list):
                    return [convert(i) for i in obj]
                elif isinstance(obj, np.integer):
                    return int(obj)
                elif isinstance(obj, np.floating):
                    return float(obj)
                return obj
            with open(fp, 'w', encoding='utf-8') as f:
                json.dump(convert(self.current_report), f, indent=2, ensure_ascii=False)
            Popup(title='Export', content=Label(text=f'Saved:\n{fp}'), size_hint=(0.8,0.5)).open()
        except Exception as e:
            Popup(title='Error', content=Label(text=str(e)), size_hint=(0.8,0.4)).open()

    def _add_label(self, title, content, color, fs):
        if title:
            self.results_layout.add_widget(Label(text=f'[b]{title}[/b]', markup=True, size_hint_y=None, height=28,
                                                 color=(0.1,0.4,0.8,1), font_size='13sp'))
        if content:
            lbl = Label(text=str(content), size_hint_y=None, color=color, font_size=fs)
            lbl.bind(texture_size=lbl.setter('size'))
            self.results_layout.add_widget(lbl)

from datetime import datetime
