"""Voice: text-to-speech (gTTS) and speech-to-text (Google Web Speech via SpeechRecognition). Both need internet."""
from io import BytesIO
CODES = {"English": ("en", "en-IN"), "Hindi": ("hi", "hi-IN"), "Gujarati": ("gu", "gu-IN")}

def speak(text, language):
    try:
        from gtts import gTTS
        buf = BytesIO(); gTTS(text, lang=CODES[language][0]).write_to_fp(buf)
        return buf.getvalue()
    except Exception:
        return None

def transcribe(audio_file, language):
    try:
        import speech_recognition as sr
        r = sr.Recognizer()
        with sr.AudioFile(audio_file) as src:
            data = r.record(src)
        return r.recognize_google(data, language=CODES[language][1])
    except Exception:
        return None
