from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from .common import RoundedButton

class BluetoothPrintScreen(BoxLayout):
    def __init__(self, app, **kw):
        super().__init__(**kw)
        self.app = app
        self.orientation = 'vertical'
        self.padding = 15
        self.spacing = 10

        self.add_widget(Label(text='[b]Bluetooth Printer[/b]', markup=True, size_hint_y=0.06,
                              font_size='18sp', color=(0.1,0.4,0.8,1)))
        self.status_label = Label(text='Not Connected', color=(0.9,0,0,1))
        self.add_widget(self.status_label)

        btn_row = BoxLayout(size_hint_y=0.08, spacing=10)
        btn_row.add_widget(RoundedButton(text='Discover', on_press=self.discover))
        btn_row.add_widget(RoundedButton(text='Connect', on_press=self.connect))
        self.add_widget(btn_row)

    def discover(self, inst):
        Popup(title='Info', content=Label(text='Bluetooth discovery requires pybluez'), size_hint=(0.7,0.3)).open()

    def connect(self, inst):
        self.status_label.text = 'Connected'
        self.status_label.color = (0,0.7,0,1)
