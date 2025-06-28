import cv2
import numpy as np
import autopy
import time
import threading
import pyautogui
import speech_recognition as sr
import HandTrackingModule as htm
import pygetwindow as gw
import psutil
import os

# --- Settings ---
wCam, hCam = 640, 480
frameR = 100
smoothening = 7
MIC_INDEX = 2  # Update this to match your microphone index

# --- Initialization ---
pTime = 0
plocX, plocY = 0, 0
clocX, clocY = 0, 0
stop_threads = False
y_scroll_history = []

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

if not cap.isOpened():
    print("❌ Could not open webcam. Exiting.")
    exit()

detector = htm.handDetector(maxHands=1)
wScr, hScr = autopy.screen.size()
recognizer = sr.Recognizer()

# --- Voice Command Function ---
def voice_command_listener():
    global stop_threads
    with sr.Microphone(device_index=MIC_INDEX) as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.3)
        print("🔊 Voice listener running...")
        while not stop_threads:
            try:
                print("🎤 Listening...")
                audio = recognizer.listen(source, timeout=3, phrase_time_limit=3)
                command = recognizer.recognize_google(audio).lower()
                print(f"🗣️ You said: {command}")

                if 'stop listening' in command:
                    print("🛑 Voice module stopped.")
                    stop_threads = True
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
                elif 'exit app' in command:
                    print("🪟 Minimizing current app...")
                    try:
                        active_window = gw.getActiveWindow()
                        if active_window:
                            active_window.minimize()
                    except Exception as e:
                        print(f"⚠️ Error minimizing app: {e}")
                else:
                    print("🤷 Command not recognized.")
            except sr.WaitTimeoutError:
                print("⏱️ Timeout.")
            except sr.UnknownValueError:
                print("🤷 Couldn’t understand.")
            except sr.RequestError as e:
                print(f"⚠️ API Error: {e}")
            except Exception as e:
                print(f"🎙️ Mic error: {e}")

# --- Gesture Control Function ---
def gesture_control():
    global pTime, plocX, plocY, clocX, clocY, stop_threads

    while not stop_threads:
        success, img = cap.read()
        if not success or img is None:
            print("❌ Failed to read frame.")
            continue

        img = detector.findHands(img)
        lmList, _ = detector.findPosition(img)

        if lmList:
            x1, y1 = lmList[8][1:]
            x2, y2 = lmList[12][1:]
            fingers = detector.fingersUp()

            # Move mode
            if fingers[1] == 1 and fingers[2] == 0:
                x3 = np.interp(x1, (frameR, wCam - frameR), (0, wScr))
                y3 = np.interp(y1, (frameR, hCam - frameR), (0, hScr))
                clocX = plocX + (x3 - plocX) / smoothening
                clocY = plocY + (y3 - plocY) / smoothening
                autopy.mouse.move(wScr - clocX, clocY)
                plocX, plocY = clocX, clocY
                cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)

            # Click mode
            if fingers[1] == 1 and fingers[2] == 1:
                length = np.hypot(x2 - x1, y2 - y1)
                if length < 40:
                    cv2.circle(img, ((x1 + x2) // 2, (y1 + y2) // 2), 15, (0, 255, 0), cv2.FILLED)
                    autopy.mouse.click()

            # Two-finger vertical gesture (scrolling)
            if fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 0:
                y_scroll_history.append(y1)
                if len(y_scroll_history) > 5:
                    delta = y_scroll_history[-1] - y_scroll_history[0]

                    if delta < -50:  # Scroll up
                        print("🔼 Gesture: Scroll Up → Show Desktop")
                        pyautogui.hotkey('win', 'd')
                        y_scroll_history.clear()

                    elif delta > 50:  # Scroll down
                        print("🔽 Gesture: Scroll Down → Force Close App")
                        try:
                            active_window = gw.getActiveWindow()
                            if active_window:
                                window_title = active_window.title
                                print(f"🧠 Active Window: {window_title}")
                                pid = active_window._hWnd
                                for proc in psutil.process_iter(['pid', 'name']):
                                    try:
                                        if proc.name().lower() in window_title.lower():
                                            proc.kill()
                                            print("💥 App force-closed.")
                                            break
                                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                                        continue
                                else:
                                    pyautogui.hotkey('alt', 'f4')
                        except Exception as e:
                            print(f"⚠️ Error closing app: {e}")
                        y_scroll_history.clear()

        # FPS
        cTime = time.time()
        fps = 1 / (cTime - pTime) if cTime != pTime else 0
        pTime = cTime
        cv2.putText(img, f'FPS: {int(fps)}', (20, 50),
                    cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)

        cv2.imshow("Hybrid Virtual Mouse", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            stop_threads = True
            break

    cap.release()
    cv2.destroyAllWindows()

# --- Main ---
if __name__ == "__main__":
    voice_thread = threading.Thread(target=voice_command_listener)
    voice_thread.start()

    gesture_control()

    voice_thread.join()
    print("🟢 Hybrid control stopped gracefully.")
