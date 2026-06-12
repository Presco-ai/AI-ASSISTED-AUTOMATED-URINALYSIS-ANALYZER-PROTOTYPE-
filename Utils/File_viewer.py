import subprocess
import webbrowser
import os
from kivy.utils import platform as kivy_platform

ANDROID_AVAILABLE = False
if kivy_platform == 'android':
    try:
        from jnius import autoclass
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        Intent = autoclass('android.content.Intent')
        Uri = autoclass('android.net.Uri')
        ANDROID_AVAILABLE = True
    except:
        pass

class FileViewer:
    @staticmethod
    def get_available_pdf_viewers():
        viewers = ["System Default"]
        if kivy_platform == 'android':
            viewers.extend(["Google PDF Viewer", "Adobe Acrobat"])
        return viewers

    @staticmethod
    def open_file(filepath, viewer=None):
        try:
            if kivy_platform == 'android':
                FileViewer._open_android(filepath)
            elif kivy_platform == 'win':
                os.startfile(filepath)
            elif kivy_platform == 'linux':
                subprocess.Popen(['xdg-open', filepath])
            else:
                webbrowser.open(filepath)
        except Exception as e:
            print(f"Error opening file: {e}")

    @staticmethod
    def _open_android(filepath):
        try:
            if ANDROID_AVAILABLE:
                context = PythonActivity.mActivity
                uri = Uri.fromFile(java.io.File(filepath))
                intent = Intent(Intent.ACTION_VIEW)
                intent.setDataAndType(uri, "application/pdf")
                intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
                context.startActivity(intent)
        except Exception as e:
            print(f"Android open error: {e}")
