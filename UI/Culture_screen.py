from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.app import App
from models.culture import CultureResult
from models.enums import CultureStatus, SensitivityResult
from utils.id_generator import PatientIDGenerator
from .common import RoundedButton

class CultureScreen(BoxLayout):
    def __init__(self, app, **kw):
        super().__init__(**kw)
        self.app = app
        self.orientation = 'vertical'
        self.padding = 15
        self.spacing = 10

        self.add_widget(Label(text='[b]Culture & Sensitivity Entry[/b]', markup=True, size_hint_y=0.06,
                              font_size='18sp', color=(0.1,0.4,0.8,1)))

        # Patient info line
        patient_line = GridLayout(cols=2, spacing=10, size_hint_y=None, height=40)
        patient_line.add_widget(Label(text='Patient:', size_hint_y=None, height=35, bold=True))
        self.patient_label = Label(text='No patient selected', size_hint_y=None, height=35, color=(0.9,0,0,1))
        patient_line.add_widget(self.patient_label)
        self.add_widget(patient_line)

        # Form fields
        form = GridLayout(cols=2, spacing=10, size_hint_y=None, height=200)
        form.add_widget(Label(text='Culture ID:', size_hint_y=None, height=35))
        self.culture_id_input = TextInput(multiline=False, size_hint_y=None, height=35, hint_text='Auto-generated')
        form.add_widget(self.culture_id_input)

        form.add_widget(Label(text='Organism:', size_hint_y=None, height=35))
        self.organism_input = TextInput(multiline=False, size_hint_y=None, height=35, hint_text='e.g., E. coli')
        form.add_widget(self.organism_input)

        form.add_widget(Label(text='Growth:', size_hint_y=None, height=35))
        self.growth_spinner = Spinner(text='Pending', values=['Pending','Scanty','Few','Moderate','Profuse','No Growth'], size_hint_y=None, height=35)
        form.add_widget(self.growth_spinner)

        form.add_widget(Label(text='Status:', size_hint_y=None, height=35))
        self.status_spinner = Spinner(text='Pending', values=['Pending','Negative','Positive'], size_hint_y=None, height=35)
        form.add_widget(self.status_spinner)

        form.add_widget(Label(text='Gram Type:', size_hint_y=None, height=35))
        self.gram_spinner = Spinner(text='Gram-negative', values=['Gram-negative','Gram-positive'], size_hint_y=None, height=35)
        form.add_widget(self.gram_spinner)

        scroll_form = ScrollView(size_hint_y=0.2)
        scroll_form.add_widget(form)
        self.add_widget(scroll_form)

        # Antibiotic panels
        self.add_widget(Label(text='[b]Antimicrobial Sensitivity[/b]', markup=True, size_hint_y=None, height=25, color=(0.1,0.4,0.8,1)))

        # Gram-positive panel
        self.gp_inputs = {}
        gp_grid = GridLayout(cols=4, spacing=5, size_hint_y=None)
        gp_grid.bind(minimum_height=gp_grid.setter('height'))
        for abx in CultureResult.get_gram_positive_antibiotics():
            gp_grid.add_widget(Label(text=abx, size_hint_y=None, height=30, font_size='9sp'))
            sp = Spinner(text='NT', values=['NT','S','I','R'], size_hint_y=None, height=30, font_size='9sp')
            gp_grid.add_widget(sp)
            self.gp_inputs[abx] = sp
        gp_scroll = ScrollView(size_hint_y=0.12)
        gp_scroll.add_widget(gp_grid)
        self.add_widget(gp_scroll)

        # Gram-negative panel
        self.gn_inputs = {}
        gn_grid = GridLayout(cols=4, spacing=5, size_hint_y=None)
        gn_grid.bind(minimum_height=gn_grid.setter('height'))
        for abx in CultureResult.get_gram_negative_antibiotics():
            gn_grid.add_widget(Label(text=abx, size_hint_y=None, height=30, font_size='9sp'))
            sp = Spinner(text='NT', values=['NT','S','I','R'], size_hint_y=None, height=30, font_size='9sp')
            gn_grid.add_widget(sp)
            self.gn_inputs[abx] = sp
        gn_scroll = ScrollView(size_hint_y=0.12)
        gn_scroll.add_widget(gn_grid)
        self.add_widget(gn_scroll)

        # Buttons
        btn_row = BoxLayout(size_hint_y=0.08, spacing=10)
        btn_row.add_widget(RoundedButton(text='Save', on_press=self.save, background_color=(0.2,0.7,0.3,1)))
        btn_row.add_widget(RoundedButton(text='Clear', on_press=self.clear, background_color=(0.7,0.7,0.7,1)))
        self.add_widget(btn_row)

        self.status_label = Label(text='Select patient first', size_hint_y=0.05, color=(0.7,0.5,0,1))
        self.add_widget(self.status_label)

        Clock.schedule_interval(self._update_patient_label, 2)

    def _update_patient_label(self, dt):
        p = self.app.current_patient
        if p and p.patient_id:
            self.patient_label.text = f"{p.get_full_name()} ({p.patient_id})"
            self.patient_label.color = (0,0.7,0,1)

    def save(self, inst):
        p = self.app.current_patient
        if not p or not p.patient_id:
            self.status_label.text = 'Error: Select a patient first'
            self.status_label.color = (0.9,0,0,1)
            return
        ig = PatientIDGenerator()
        cid = self.culture_id_input.text.strip() or ig.generate_culture_id(p.patient_id)

        sens_map = {'S': SensitivityResult.SENSITIVE, 'I': SensitivityResult.INTERMEDIATE,
                    'R': SensitivityResult.RESISTANT, 'NT': SensitivityResult.NOT_TESTED}
        sensitivity = {}
        for abx, spinner in {**self.gp_inputs, **self.gn_inputs}.items():
            sensitivity[abx] = sens_map.get(spinner.text, SensitivityResult.NOT_TESTED)

        status_map = {'Pending': CultureStatus.PENDING, 'Negative': CultureStatus.NEGATIVE,
                      'Positive': CultureStatus.POSITIVE}
        culture = CultureResult(
            culture_id=cid,
            patient_id=p.patient_id,
            sample_id=ig.generate_sample_id(p.patient_id),
            collection_date=datetime.now().strftime('%Y-%m-%d'),
            report_date=datetime.now().strftime('%Y-%m-%d'),
            culture_status=status_map.get(self.status_spinner.text, CultureStatus.PENDING),
            organism_identified=self.organism_input.text.strip(),
            colony_count_level=self.growth_spinner.text,
            gram_type=self.gram_spinner.text,
            sensitivity_panel=sensitivity
        )
        self.app.current_culture = culture
        self.culture_id_input.text = cid
        p.add_culture_id(cid)

        from dataclasses import asdict
        self.app.db.save_culture(cid, p.patient_id, culture.sample_id, asdict(culture), culture.culture_status.value)
        self.app.db.add_patient(p)

        self.status_label.text = f'Culture {cid} saved'
        self.status_label.color = (0,0.7,0,1)

    def clear(self, inst):
        self.culture_id_input.text = ''
        self.organism_input.text = ''
        self.growth_spinner.text = 'Pending'
        self.status_spinner.text = 'Pending'
        self.gram_spinner.text = 'Gram-negative'
        for inp in list(self.gp_inputs.values()) + list(self.gn_inputs.values()):
            inp.text = 'NT'
        self.status_label.text = 'Select patient first'

from datetime import datetime
