import os
import importlib.util
from gi.repository import GLib

def load_translation() -> dict:
    locale = GLib.get_language_names()[0]
    lang_code = locale.split('_')[0]
    path = os.path.join(os.path.dirname(__file__), 'translations', f'{lang_code}.py')
    if not os.path.exists(path):
        lang_code = 'en'  # fallback на англійську
        path = os.path.join(os.path.dirname(__file__), 'translations', f'{lang_code}.py')

    spec = importlib.util.spec_from_file_location(f"translations.{lang_code}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.translations
