import cv2
import threading
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.image import Image as KivyImage
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.button import Button
from kivy.clock import Clock
from .common import RoundedButton

class AnalysisScreen(BoxLayout):
    def __init__(self, title, analyze_func, **kw):
        super().__init__(**kw)
        self.title = title
        self.analyze_func = analyze_func
        self.current_image = None
        self.current_result = None
        self.orientation = 'vertical'
        self.padding = 15
        self.spacing = 10

        self.add_widget(Label(text=f"[b]{title}[/b]", markup=True, size_hint_y=0.06,
                              font_size='18sp', color=(0.1,0.4,0.8,1)))
        self.ai_status = Label(text="Ready", size_hint_y=0.03, font_size='9sp', color=(0,0.6,0,1))
        self.add_widget(self.ai_status)

        self.img = KivyImage(source='', size_hint_y=0.30)
        self.add_widget(self.img)

        br = BoxLayout(size_hint_y=0.08, spacing=10)
        self.up_btn = RoundedButton(text='Upload Image', on_press=self.show_chooser)
        self.an_btn = RoundedButton(text='Analyze', on_press=self.run_analysis, disabled=True)
        br.add_widget(self.up_btn)
        br.add_widget(self.an_btn)
        self.add_widget(br)

        self.prog = ProgressBar(max=100, size_hint_y=0.04, opacity=0)
        self.add_widget(self.prog)

        sv = ScrollView(size_hint_y=0.42)
        self.res = GridLayout(cols=1, spacing=5, size_hint_y=None, padding=10)
        self.res.bind(minimum_height=self.res.setter('height'))
        sv.add_widget(self.res)
        self.add_widget(sv)

    def show_chooser(self, instance):
        c = BoxLayout(orientation='vertical')
        dp = '/storage/emulated/0/DCIM/Camera' if kivy_platform == 'android' else os.path.expanduser('~')
        fc = FileChooserListView(path=dp, filters=['*.png','*.jpg','*.jpeg','*.bmp'])
        c.add_widget(fc)
        p = Popup(title='Select Image', content=c, size_hint=(0.95,0.9))
        bl = BoxLayout(size_hint_y=0.1)
        bl.add_widget(Button(text='Select', on_press=lambda x: self.load_image(fc.selection, p)))
        bl.add_widget(Button(text='Cancel', on_press=p.dismiss))
        c.add_widget(bl)
        p.open()

    def load_image(self, sel, popup):
        if sel and len(sel) > 0:
            self.img.source = sel[0]
            self.current_image = cv2.imread(sel[0])
            self.an_btn.disabled = False
            popup.dismiss()

    def run_analysis(self, instance):
        if self.current_image is None:
            return
        self.prog.opacity = 1
        self.prog.value = 20
        self.an_btn.disabled = True
        self.an_btn.text = 'Analyzing...'
        def _run():
            try:
                r = self.analyze_func(self.current_image)
                Clock.schedule_once(lambda dt: self._done(r), 0)
            except Exception as e:
                Clock.schedule_once(lambda dt: self._err(str(e)), 0)
        threading.Thread(target=_run, daemon=True).start()

    def _done(self, result):
        self.prog.value = 100
        self.current_result = result
        self.show_results(result)
        self.an_btn.disabled = False
        self.an_btn.text = 'Analyze'
        Clock.schedule_once(lambda dt: setattr(self.prog, 'opacity', 0), 0.5)

    def _err(self, msg):
        self.prog.opacity = 0
        self.an_btn.disabled = False
        self.an_btn.text = 'Analyze'
        Popup(title='Error', content=Label(text=f'Error: {msg}'), size_hint=(0.8,0.3)).open()

    def show_results(self, result):
        self.res.clear_widgets()
        if 'microscopy_results' in result:
            self.res.add_widget(Label(text='[b]URINE MICROSCOPY[/b]', markup=True,
                                      size_hint_y=None, height=28, color=(0.1,0.4,0.8,1), font_size='13sp'))
            for k, v in result['microscopy_results'].items():
                if v != "None Seen":
                    color = (0.9,0.2,0.2,1) if any(x in k for x in ["Pus","Bacteria","Yeast"]) else (0.1,0.1,0.1,1)
                    self.res.add_widget(Label(text=f"  • {k}: {v}", size_hint_y=None, height=22, color=color, font_size='11sp'))
        elif 'results' in result:
            self.res.add_widget(Label(text='[b]URINALYSIS - Color Chart[/b]', markup=True,
                                      size_hint_y=None, height=28, color=(0.1,0.4,0.8,1)))
            for k, v in sorted(result['results'].items(), key=lambda x: x[1].get('pad_position', 0)):
                st = 'OK' if v.get('is_normal', False) else 'ABN'
                cl = (0,0.6,0,1) if v.get('is_normal', False) else (0.9,0.2,0.2,1)
                self.res.add_widget(Label(text=f"  [{st}] {k}: {v.get('value','N/A')} {v.get('unit','')} ({v.get('confidence',0)}%)",
                                          size_hint_y=None, height=22, color=cl, font_size='11sp'))

from kivy.utils import platform as kivy_platform
import os
