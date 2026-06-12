from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.app import App
from models.patient import Patient
from models.enums import Sex
from .common import RoundedButton

class PatientScreen(BoxLayout):
    def __init__(self, db, **kw):
        super().__init__(**kw)
        self.db = db
        self.orientation = 'vertical'
        self.padding = 15
        self.spacing = 10

        self.add_widget(Label(text='[b]Patient Registration[/b]', markup=True, size_hint_y=0.06,
                              font_size='18sp', color=(0.1,0.4,0.8,1)))
        form = GridLayout(cols=2, spacing=10, size_hint_y=None)
        form.bind(minimum_height=form.setter('height'))

        self.surname_input = TextInput(multiline=False)
        self.first_name_input = TextInput(multiline=False)
        self.middle_name_input = TextInput(multiline=False)
        self.age_input = TextInput(multiline=False, input_filter='int')
        self.phone_input = TextInput(multiline=False)
        self.hospital_input = TextInput(multiline=False)
        self.history_input = TextInput(multiline=False)
        self.allergies_input = TextInput(multiline=False)
        self.pregnancy_input = Spinner(text='Not Applicable', values=['Not Applicable','Not Pregnant','Pregnant','First Trimester','Second Trimester','Third Trimester'], size_hint_y=None, height=35)
        self.chronic_input = TextInput(multiline=False, hint_text='e.g., Diabetes, Hypertension')

        self._add_field(form, 'Surname:*', self.surname_input)
        self._add_field(form, 'First Name:', self.first_name_input)
        self._add_field(form, 'Middle Name:', self.middle_name_input)

        form.add_widget(Label(text='Patient ID:', size_hint_y=None, height=35, halign='right'))
        self.pid_label = Label(text='Auto-generated', size_hint_y=None, height=35, color=(0.1,0.4,0.8,1))
        form.add_widget(self.pid_label)

        form.add_widget(Label(text='Culture IDs:', size_hint_y=None, height=35, halign='right'))
        self.culture_ids_label = Label(text='None linked', size_hint_y=None, height=35, color=(0.5,0.5,0.5,1))
        form.add_widget(self.culture_ids_label)

        self._add_field(form, 'Age:', self.age_input)
        form.add_widget(Label(text='Age Unit:', size_hint_y=None, height=35, halign='right'))
        self.age_unit_spinner = Spinner(text='Years', values=['Years','Months','Days'], size_hint_y=None, height=35)
        form.add_widget(self.age_unit_spinner)

        form.add_widget(Label(text='Sex:', size_hint_y=None, height=35, halign='right'))
        self.sex_spinner = Spinner(text='Male', values=['Male','Female','Other'], size_hint_y=None, height=35)
        form.add_widget(self.sex_spinner)

        self._add_field(form, 'Phone:', self.phone_input)
        self._add_field(form, 'Hospital No:', self.hospital_input)
        self._add_field(form, 'Clinical History:', self.history_input)
        self._add_field(form, 'Allergies:', self.allergies_input)

        form.add_widget(Label(text='Pregnancy Status:', size_hint_y=None, height=35, halign='right'))
        form.add_widget(self.pregnancy_input)
        self._add_field(form, 'Chronic Conditions:', self.chronic_input)

        sv = ScrollView(size_hint_y=0.5)
        sv.add_widget(form)
        self.add_widget(sv)

        br = BoxLayout(size_hint_y=0.08, spacing=10)
        br.add_widget(RoundedButton(text='Save', on_press=self.save, background_color=(0.2,0.7,0.3,1)))
        br.add_widget(RoundedButton(text='Clear', on_press=self.clear, background_color=(0.7,0.7,0.7,1)))
        br.add_widget(RoundedButton(text='Search', on_press=self.search, background_color=(0.2,0.6,1,1)))
        br.add_widget(RoundedButton(text='History', on_press=self.view_history, background_color=(0.9,0.5,0.1,1)))
        self.add_widget(br)

        self.status_label = Label(text='', size_hint_y=0.05, color=(0,0.7,0,1))
        self.add_widget(self.status_label)

    def _add_field(self, parent, label_text, widget):
        parent.add_widget(Label(text=label_text, size_hint_y=None, height=35, halign='right'))
        parent.add_widget(widget)

    def save(self, inst):
        surname = self.surname_input.text.strip()
        if not surname:
            self.status_label.text = 'Error: Surname required'
            self.status_label.color = (0.9,0,0,1)
            return
        try:
            sex_map = {'Male': Sex.MALE, 'Female': Sex.FEMALE, 'Other': Sex.OTHER}
            patient = Patient(
                surname=surname,
                first_name=self.first_name_input.text.strip(),
                middle_name=self.middle_name_input.text.strip(),
                age=int(self.age_input.text or 0),
                age_unit=self.age_unit_spinner.text,
                sex=sex_map.get(self.sex_spinner.text, Sex.MALE),
                contact_phone=self.phone_input.text.strip(),
                hospital_number=self.hospital_input.text.strip(),
                clinical_history=self.history_input.text.strip(),
                allergies=self.allergies_input.text.strip(),
                pregnancy_status=self.pregnancy_input.text,
                chronic_conditions=self.chronic_input.text.strip()
            )
            pid = self.db.add_patient(patient)
            self.pid_label.text = pid
            self.culture_ids_label.text = patient.culture_ids or 'None linked'
            App.get_running_app().current_patient = patient
            self.status_label.text = f'Saved: {patient.get_full_name()} ({pid})'
            self.status_label.color = (0,0.7,0,1)
        except Exception as e:
            self.status_label.text = f'Error: {e}'
            self.status_label.color = (0.9,0,0,1)

    def clear(self, inst):
        for w in [self.surname_input, self.first_name_input, self.middle_name_input, self.age_input,
                  self.phone_input, self.hospital_input, self.history_input, self.allergies_input,
                  self.chronic_input]:
            w.text = ''
        self.pregnancy_input.text = 'Not Applicable'
        self.pid_label.text = 'Auto-generated'
        self.culture_ids_label.text = 'None linked'
        self.status_label.text = ''

    def search(self, inst):
        c = BoxLayout(orientation='vertical', spacing=10, padding=10)
        c.add_widget(Label(text='[b]Search Patients[/b]', markup=True, size_hint_y=None, height=30))
        search_input = TextInput(hint_text='Search...', multiline=False, size_hint_y=None, height=45)
        c.add_widget(search_input)
        results_layout = GridLayout(cols=1, spacing=2, size_hint_y=None)
        results_layout.bind(minimum_height=results_layout.setter('height'))
        scroll = ScrollView(size_hint_y=0.6)
        scroll.add_widget(results_layout)
        c.add_widget(scroll)

        def do_search(inst):
            results_layout.clear_widgets()
            for p in self.db.search(search_input.text.strip()):
                btn = Button(text=f"{p.get_full_name()} | {p.patient_id}", size_hint_y=None, height=40,
                             on_press=lambda x, pt=p: self._load_patient(pt, popup))
                results_layout.add_widget(btn)

        c.add_widget(RoundedButton(text='Search', on_press=do_search))
        close_btn = Button(text='Close', size_hint_y=None, height=40)
        c.add_widget(close_btn)
        popup = Popup(title='Search', content=c, size_hint=(0.9,0.8))
        close_btn.bind(on_press=popup.dismiss)
        popup.open()

    def view_history(self, inst):
        app = App.get_running_app()
        p = app.current_patient
        if not p or not p.patient_id:
            Popup(title='No Patient', content=Label(text='Please select a patient first'), size_hint=(0.7,0.3)).open()
            return
        history = self.db.get_patient_history(p.patient_id)
        c = BoxLayout(orientation='vertical', padding=10, spacing=10)
        c.add_widget(Label(text=f'[b]History: {p.get_full_name()}[/b]', markup=True, size_hint_y=None, height=30))
        if history.get('reports'):
            for r in history['reports'][:10]:
                c.add_widget(Label(text=f"{r[0]} | {r[1][:10]} | {r[2] or 'No diagnosis'}", size_hint_y=None, height=25, font_size='10sp'))
        else:
            c.add_widget(Label(text='No reports found'))
        c.add_widget(Button(text='Close', size_hint_y=None, height=40, on_press=lambda x: popup.dismiss()))
        popup = Popup(title='Patient History', content=c, size_hint=(0.95,0.9))
        popup.open()

    def _load_patient(self, patient, popup):
        self.surname_input.text = patient.surname
        self.first_name_input.text = patient.first_name
        self.middle_name_input.text = patient.middle_name
        self.pid_label.text = patient.patient_id
        self.culture_ids_label.text = patient.culture_ids or 'None linked'
        self.age_input.text = str(patient.age)
        self.age_unit_spinner.text = patient.age_unit
        self.sex_spinner.text = patient.sex.value
        self.phone_input.text = patient.contact_phone
        self.hospital_input.text = patient.hospital_number
        self.history_input.text = patient.clinical_history
        self.allergies_input.text = patient.allergies
        self.pregnancy_input.text = patient.pregnancy_status
        self.chronic_input.text = patient.chronic_conditions
        popup.dismiss()
        self.status_label.text = f'Loaded: {patient.get_full_name()}'
        self.status_label.color = (0,0.7,0,1)
        App.get_running_app().current_patient = patient
