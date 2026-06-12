from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from .analysis_screen import AnalysisScreen
from .common import RoundedButton

class StripScreen(AnalysisScreen):
    def __init__(self, analyzer, **kw):
        super().__init__('Urinalysis (Color Chart)', analyzer.analyze, **kw)
        self.analyzer = analyzer

    def show_results(self, result):
        self.res.clear_widgets()
        self.res.add_widget(Label(text='[b]URINALYSIS - Color Chart[/b]', markup=True,
                                  size_hint_y=None, height=28, color=(0.1,0.4,0.8,1)))
        self.res.add_widget(RoundedButton(text='Edit Parameters', size_hint_y=None, height=40, on_press=self.edit_params))
        for k, v in sorted(result['results'].items(), key=lambda x: x[1].get('pad_position', 0)):
            st = 'OK' if v.get('is_normal', False) else 'ABN'
            cl = (0,0.6,0,1) if v.get('is_normal', False) else (0.9,0.2,0.2,1)
            self.res.add_widget(Label(text=f"  [{st}] {k}: {v.get('value','N/A')} {v.get('unit','')} ({v.get('confidence',0)}%)",
                                      size_hint_y=None, height=22, color=cl, font_size='11sp'))

    def edit_params(self, instance=None):
        c = BoxLayout(orientation='vertical', spacing=10, padding=10)
        c.add_widget(Label(text='[b]Edit Strip Parameters[/b]', markup=True, size_hint_y=None, height=30))
        pl = GridLayout(cols=2, spacing=5, size_hint_y=None)
        pl.bind(minimum_height=pl.setter('height'))
        inputs = {}
        for name, cfg in self.analyzer.active_params.items():
            pl.add_widget(Label(text=name, size_hint_y=None, height=35, font_size='10sp'))
            pi = TextInput(text=str(cfg.get('pad_position', 1)), multiline=False, size_hint_y=None, height=35, input_filter='int')
            pl.add_widget(pi)
            inputs[name] = pi
        sv = ScrollView(size_hint_y=0.5)
        sv.add_widget(pl)
        c.add_widget(sv)
        br = BoxLayout(size_hint_y=0.08, spacing=10)
        def apply(inst):
            new = {}
            for name, inp in inputs.items():
                nc = dict(self.analyzer.active_params.get(name, {}))
                try:
                    nc['pad_position'] = int(inp.text or 1)
                except:
                    pass
                new[name] = nc
            if new:
                self.analyzer.set_config(new)
            popup.dismiss()
        br.add_widget(RoundedButton(text='Apply', on_press=apply, background_color=(0.2,0.7,0.3,1)))
        br.add_widget(RoundedButton(text='Reset', on_press=lambda x: (self.analyzer.reset(), popup.dismiss()), background_color=(0.9,0.5,0.1,1)))
        br.add_widget(Button(text='Cancel', on_press=lambda x: popup.dismiss()))
        c.add_widget(br)
        popup = Popup(title='Edit Strip', content=c, size_hint=(0.95,0.9))
        popup.open()
