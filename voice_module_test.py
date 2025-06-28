import pyautogui
import speech_recognition as sr

MIC_INDEX = 2  # Set your mic index here (Realme Buds)

recognizer = sr.Recognizer()

def listen_command():
    with sr.Microphone(device_index=MIC_INDEX) as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.3)
        print("🔊 Voice listener running... Say 'stop listening' to exit.")
        while True:
            print("🎤 Listening (fast mode)...")
            try:
                audio = recognizer.listen(source, timeout=3, phrase_time_limit=3)
                command = recognizer.recognize_google(audio).lower()
                print(f"🗣️ You said: {command}")

                if 'stop listening' in command:
                    print("🛑 Voice module stopped.")
                    break
                elif 'click here' in command:
                    pyautogui.click()
                elif 'scroll down' in command:
                    pyautogui.scroll(-300)
                elif 'scroll up' in command:
                    pyautogui.scroll(300)
                elif 'open browser' in command:
                    pyautogui.hotkey('win', 'r')
                    pyautogui.write('chrome\n')
                else:
                    print("🤷 Command not recognized.")
            except sr.WaitTimeoutError:
                print("⏱️ Timed out waiting for speech.")
            except sr.UnknownValueError:
                print("🤷 Couldn't understand.")
            except sr.RequestError as e:
                print(f"⚠️ Could not request results; {e}")

if __name__ == "__main__":
    listen_command()
