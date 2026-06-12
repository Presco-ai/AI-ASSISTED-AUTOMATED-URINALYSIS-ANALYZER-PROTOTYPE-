from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from .common import RoundedButton

class ESP32PairingScreen(BoxLayout):
    def __init__(self, esp32, **kw):
        super().__init__(**kw)
        self.esp32 = esp32
        self.orientation = 'vertical'
        self.padding = 15
        self.spacing = 10

        self.add_widget(Label(text='[b]ESP32 Device Control[/b]', markup=True, size_hint_y=0.08,
                              font_size='18sp', color=(0.1,0.4,0.8,1)))
        self.status_label = Label(text='Status: Not Connected', color=(0.9,0,0,1), font_size='14sp')
        self.add_widget(self.status_label)

        cfg_grid = GridLayout(cols=2, spacing=10, size_hint_y=None, height=120)
        cfg_grid.add_widget(Label(text='Device Name:', size_hint_y=None, height=35))
        self.name_input = TextInput(text='ESP32-CAM Microscope', multiline=False, size_hint_y=None, height=35)
        cfg_grid.add_widget(self.name_input)

        cfg_grid.add_widget(Label(text='Connection:', size_hint_y=None, height=35))
        self.conn_spinner = Spinner(text='Bluetooth', values=['Bluetooth','WiFi'], size_hint_y=None, height=35)
        cfg_grid.add_widget(self.conn_spinner)

        cfg_grid.add_widget(Label(text='Address:', size_hint_y=None, height=35))
        self.address_input = TextInput(text='00:11:22:33:44:55', multiline=False, size_hint_y=None, height=35)
        cfg_grid.add_widget(self.address_input)
        self.add_widget(cfg_grid)

        btn_grid = GridLayout(cols=2, spacing=10, size_hint_y=None, height=50)
        self.connect_btn = RoundedButton(text='Connect', on_press=self.connect, background_color=(0.2,0.7,0.3,1))
        self.disconnect_btn = RoundedButton(text='Disconnect', on_press=self.disconnect, background_color=(0.9,0.3,0.3,1), disabled=True)
        btn_grid.add_widget(self.connect_btn)
        btn_grid.add_widget(self.disconnect_btn)
        self.add_widget(btn_grid)

    def connect(self, inst):
        if self.conn_spinner.text == 'Bluetooth':
            self.esp32.connect_bluetooth(self.address_input.text.strip())
        self.status_label.text = 'Status: Connected'
        self.status_label.color = (0,0.7,0,1)
        self.connect_btn.disabled = True
        self.disconnect_btn.disabled = False

    def disconnect(self, inst):
        self.esp32.disconnect()
        self.status_label.text = 'Status: Not Connected'
        self.status_label.color = (0.9,0,0,1)
        self.connect_btn.disabled = False
        self.disconnect_btn.disabled = True
