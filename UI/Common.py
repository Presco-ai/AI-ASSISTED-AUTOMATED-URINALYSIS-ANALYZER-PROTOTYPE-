from kivy.uix.button import Button

class RoundedButton(Button):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.background_normal = ''
        self.background_color = (0.2, 0.6, 1, 1)
