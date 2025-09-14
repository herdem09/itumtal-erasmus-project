import speech_recognition as sr
from gtts import gTTS
import google.generativeai as genai
import threading
from queue import Queue
import time
import pygame
import io
import tempfile
import os

genai.configure(api_key="AIzaSyBGv0KCGxRwxY8J5-HuVXuV5lepHl_4WrM")

model = genai.GenerativeModel(
    "gemini-2.0-flash-exp",
    generation_config={
        "temperature": 0.7,
        "top_p": 0.9,
        "top_k": 40,
    },
    system_instruction="Sen yardımcı bir akıllı ev asistanısın. Türkçe ve net cevaplar ver. Eğer mesaj 'teşekkürler', 'sağol', 'baybay', 'tamam', 'görüşürüz' vb. bir şey ise sadece '1' cevabını ver. Eğer mesaj 'sistemi kapat', 'programı kapat', 'tamamen kapat' vb bir şey ise sadece '2' cevabını ver."
)

class VoiceAssistant:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        pygame.mixer.init()
        self.is_active = False
        self.conversation_history = []
        self.listening = True
        self.speech_queue = Queue()
        self.speech_thread = threading.Thread(target=self._speech_worker, daemon=True)
        self.speech_thread.start()
        with self.microphone as source:
            print("🔧 Mikrofon kalibre ediliyor...")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
        print("✅ Sesli AI Asistan hazır! (gTTS ile)")
        print("⚠️  İnternet bağlantısı gereklidir")
        print("💡 'Hey asistan' diyerek aktivasyon yapabilirsiniz")
        print("💡 'Teşekkürler' gibi vedalaşma mesajlarından sonra tekrar 'Hey asistan' demeniz gerekir")
        print("-" * 50)

    def _speech_worker(self):
        while True:
            text = self.speech_queue.get()
            if text is None:
                break
            try:
                self._speak_gtts(text)
            except Exception as e:
                print(f"❌ Konuşma hatası: {e}")
            self.speech_queue.task_done()

    def _speak_gtts(self, text):
        try:
            tts = gTTS(text=text, lang='tr', slow=False)
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
                tts.save(temp_file.name)
                temp_filename = temp_file.name
            pygame.mixer.music.load(temp_filename)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            try:
                os.unlink(temp_filename)
            except:
                pass
        except Exception as e:
            print(f"❌ gTTS hatası: {e}")
            print(f"🔊 Sesli yanıt: {text}")

    def speak(self, text):
        self.speech_queue.put(text)

    def listen(self):
        try:
            with self.microphone as source:
                if not self.is_active:
                    print("🎤 Aktivasyon bekleniyor...")
                else:
                    print("🎤 Dinliyorum...")
                audio = self.recognizer.listen(source, timeout=3, phrase_time_limit=5)
            text = self.recognizer.recognize_google(audio, language="tr-TR")
            return text.lower()
        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            if self.is_active:
                print("❓ Anlamadım, tekrar söyler misiniz?")
            return None
        except sr.RequestError as e:
            print(f"❌ Ses tanıma hatası: {e}")
            return None
        except Exception as e:
            print(f"❌ Beklenmeyen hata: {e}")
            return None

    def get_ai_response(self, user_input):
        try:
            self.conversation_history.append(f"Kullanıcı: {user_input}")
            recent_history = self.conversation_history[-10:]
            context = "\n".join(recent_history)
            response = model.generate_content(context + f"\nKullanıcı: {user_input}")
            ai_response = response.text.strip()
            self.conversation_history.append(f"Asistan: {ai_response}")
            return ai_response
        except Exception as e:
            print(f"❌ AI yanıt hatası: {e}")
            return "Özür dilerim, şu anda yanıt veremiyorum."

    def run(self):
        print("🚀 Asistan başlatılıyor...")
        while self.listening:
            user_input = self.listen()
            if user_input is None:
                continue
            print(f"👤 Sen: {user_input}")
            if not self.is_active:
                if any(trigger in user_input for trigger in ["hey asistan", "hey akıllı ev", "asistan"]):
                    self.is_active = True
                    response = "Merhaba! Size nasıl yardımcı olabilirim?"
                    print(f"🤖 Asistan: {response}")
                    self.speak(response)
                continue
            response = self.get_ai_response(user_input)
            print(f"🤖 Asistan: {response}")
            if response.strip() == "1":
                print("💤 Asistan devre dışı - tekrar aktivasyon bekleniyor")
                self.is_active = False
                self.conversation_history = []
            elif response.strip() == "2":
                print("🛑 Sistem sonlandırılıyor...")
                self.listening = False
                break
            else:
                self.speak(response)

    def stop(self):
        self.listening = False
        self.speech_queue.put(None)
        pygame.mixer.quit()

def main():
    try:
        assistant = VoiceAssistant()
        assistant.run()
    except KeyboardInterrupt:
        print("\n🛑 Program Ctrl+C ile sonlandırıldı")
    except Exception as e:
        print(f"❌ Program hatası: {e}")
    finally:
        print("👋 Program sonlandı")

if __name__ == "__main__":
    main()
