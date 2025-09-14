import speech_recognition as sr
from gtts import gTTS
import pyglet
import tempfile
import os
import google.generativeai as genai
import time


class VoiceAIAssistant:
    def __init__(self, api_key):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.5-flash")

        self.is_listening = False

    def speak(self, text):
        tts = gTTS(text=text, lang='tr')
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
            tts.save(f.name)
            temp_file = f.name

        music = pyglet.media.load(temp_file, streaming=False)
        player = pyglet.media.Player()
        player.queue(music)
        player.play()

        while player.playing:
            pyglet.app.platform_event_loop.dispatch_posted_events()
            time.sleep(0.1)

        os.remove(temp_file)

    def listen_for_speech(self):
        try:
            with self.microphone as source:
                if not self.is_listening:
                    self.recognizer.adjust_for_ambient_noise(source)
                    self.is_listening = True

                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)

            text = self.recognizer.recognize_google(audio, language='tr-TR')
            return text

        except (sr.WaitTimeoutError, sr.UnknownValueError, sr.RequestError):
            return None

    def get_ai_response(self, question):
        try:
            response = self.model.generate_content(question)
            return response.text.strip()
        except Exception as e:
            return f"Üzgünüm, AI servisi şu anda kullanılamıyor: {str(e)}"

    def run(self):


        while True:
            try:
                speech_text = self.listen_for_speech()
                if speech_text:
                    if any(word in speech_text.lower() for word in ['kapat', 'çık', 'dur', 'bitir']):
                        break

                    response = self.get_ai_response(speech_text)
                    self.speak(response)

                time.sleep(0.5)

            except KeyboardInterrupt:
                break
            except Exception:
                continue


def main():
    api_key = "AIzaSyBGv0KCGxRwxY8J5-HuVXuV5lepHl_4WrM"
    if not api_key:
        return

    assistant = VoiceAIAssistant(api_key)
    assistant.run()


if __name__ == "__main__":
    main()
