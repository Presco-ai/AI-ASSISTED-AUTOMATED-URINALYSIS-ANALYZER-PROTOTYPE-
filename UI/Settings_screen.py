from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.switch import Switch
from kivy.core.window import Window
from analyzers.roboflow_ai import ROBOFLOW_AVAILABLE
from reporting.pdf_generator import REPORTLAB_AVAILABLE

class SettingsScreen(BoxLayout):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.orientation = 'vertical'
        self.padding = 15
        self.spacing = 10

        self.add_widget(Label(text='[b]Settings[/b]', markup=True, size_hint_y=0.08,
                              font_size='18sp', color=(0.1,0.4,0.8,1)))

        dark_row = BoxLayout(size_hint_y=None, height=50, spacing=10)
        dark_row.add_widget(Label(text='Dark Mode:', size_hint_x=0.4))
        self.dark_switch = Switch(active=False)
        self.dark_switch.bind(active=self.toggle_dark)
        dark_row.add_widget(self.dark_switch)
        self.add_widget(dark_row)

        ai_text = f'AI Model: {"Roboflow AI" if ROBOFLOW_AVAILABLE else "Simulated"}'
        pdf_text = f'PDF Support: {"Available" if REPORTLAB_AVAILABLE else "Not Available - Install reportlab"}'
        self.add_widget(Label(text=ai_text, size_hint_y=None, height=30, font_size='10sp', color=(0.5,0.5,0.5,1)))
        self.add_widget(Label(text=pdf_text, size_hint_y=None, height=30, font_size='10sp',
                              color=(0.7,0.5,0,1) if not REPORTLAB_AVAILABLE else (0,0.5,0,1)))

    def toggle_dark(self, inst, val):
        Window.clearcolor = (0.15,0.15,0.15,1) if val else (0.95,0.95,0.97,1)
