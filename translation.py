# Optional translation support - graceful fallback if library unavailable
try:
    from googletrans import Translator, LANGUAGES
    translator = Translator()
    TRANSLATION_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    translator = None
    LANGUAGES = {}
    TRANSLATION_AVAILABLE = False
    print("Warning: googletrans not available. Translation features disabled.")

def detect_language(text):
    """Detects the language of the given text."""
    if not TRANSLATION_AVAILABLE:
        return "en"
    try:
        detected = translator.detect(text)
        return detected.lang if detected and detected.lang else "en"
    except Exception as e:
        print("Language detection error:", e)
        return "en"

def translate_text(text, target_language):
    """Translates text to the target language."""
    if not TRANSLATION_AVAILABLE:
        return text
    try:
        translated = translator.translate(text, dest=target_language)
        return translated.text if translated and translated.text else text
    except Exception as e:
        print("Translation error:", e)
        return text

def get_language_name(lang_code):
    """Gets the language name from the language code."""
    common_langs = {
        'en': 'English',
        'hi': 'Hindi',
        'es': 'Spanish',
        'fr': 'French',
        'de': 'German',
        'zh': 'Chinese',
        'ar': 'Arabic',
        'ru': 'Russian',
        'ja': 'Japanese',
        'pt': 'Portuguese'
    }
    
    if not lang_code:
        return "English"
        
    try:
        if TRANSLATION_AVAILABLE and lang_code in LANGUAGES:
            return LANGUAGES[lang_code]
    except Exception as e:
        print("Language name retrieval error:", e)
        
    return common_langs.get(lang_code.lower(), "English")
