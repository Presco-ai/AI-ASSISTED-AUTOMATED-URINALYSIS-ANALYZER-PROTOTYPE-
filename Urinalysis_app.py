import os
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelHeader
from kivy.graphics import Color, Rectangle
from kivy.utils import platform as kivy_platform
from kivy.clock import Clock

from database.db_manager import DatabaseManager
from analyzers.color_chart import ColorChartStripAnalyzer
from analyzers.roboflow_ai import RoboflowAnalyzer
from ui.patient_screen import PatientScreen
from ui.analysis_screen import AnalysisScreen
from ui.strip_screen import StripScreen
from ui.culture_screen import CultureScreen
from ui.report_screen import CombinedReportScreen
from ui.esp32_screen import ESP32PairingScreen
from ui.print_screen import BluetoothPrintScreen
from ui.settings_screen import SettingsScreen
from utils.esp32_interface import ESP32Interface

class UrinalysisApp(App):
    def build(self):
        db_path = os.path.join(os.path.expanduser('~'), "urinalysis.db")
        self.title = 'AI Urinalysis Pro v3.0 - Comprehensive Clinical Edition'
        Window.clearcolor = (0.95, 0.95, 0.97, 1)
        Window.size = (420, 720)

        self.db = DatabaseManager(db_path)
        self.roboflow_analyzer = RoboflowAnalyzer()
        self.color_chart_analyzer = ColorChartStripAnalyzer()
        self.current_patient = None
        self.current_culture = None

        root = BoxLayout(orientation='vertical')
        top = BoxLayout(size_hint_y=0.08, padding=10)
        with top.canvas.before:
            Color(0.1, 0.4, 0.8, 1)
            self.rect = Rectangle(pos=top.pos, size=top.size)
        top.bind(pos=self._update_rect, size=self._update_rect)
        top.add_widget(Label(text='AI Urinalysis Pro v3.0 - Comprehensive', color=(1,1,1,1), font_size='14sp'))
        root.add_widget(top)

        self.tabs = TabbedPanel(size_hint_y=0.92, do_default_tab=False, tab_width=85)

        self.patient_screen = PatientScreen(self.db)
        self.microscopy_screen = AnalysisScreen('Microscopy (AI)', self.roboflow_analyzer.analyze)
        self.strip_screen = StripScreen(self.color_chart_analyzer)
        self.culture_screen = CultureScreen(self)
        self.report_screen = CombinedReportScreen(self)
        self.esp32_screen = ESP32PairingScreen(ESP32Interface())
        self.bluetooth_screen = BluetoothPrintScreen(self)
        self.settings_screen = SettingsScreen()

        for t, s in [
            ('Patient', self.patient_screen),
            ('Micro AI', self.microscopy_screen),
            ('Strip', self.strip_screen),
            ('Culture', self.culture_screen),
            ('Report', self.report_screen),
            ('ESP32', self.esp32_screen),
            ('Print', self.bluetooth_screen),
            ('Settings', self.settings_screen)
        ]:
            th = TabbedPanelHeader(text=t)
            th.content = s
            self.tabs.add_widget(th)

        root.add_widget(self.tabs)
        return root

    def _update_rect(self, inst, val):
        self.rect.pos = inst.pos
        self.rect.size = inst.size

# needed for circular import of Label in ui files
from kivy.uix.label import Label
