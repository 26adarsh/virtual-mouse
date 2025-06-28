import cv2
import numpy as np
import autopy
import time
import HandTrackingModule as htm

##############################
wCam, hCam = 640, 480  # Webcam resolution
frameR = 100           # Frame reduction (edges margin)
smoothening = 7        # Cursor smoothening factor
##############################

pTime = 0
plocX, plocY = 0, 0     # Previous location
clocX, clocY = 0, 0     # Current location

# Capture webcam
cap = cv2.VideoCapture(0)
cap.set(3, wCam)  # Width
cap.set(4, hCam)  # Height

# Safety check for camera
if not cap.isOpened():
    print("❌ Could not open webcam. Exiting.")
    exit()

# Create hand detector
detector = htm.handDetector(maxHands=1)

# Get screen size
wScr, hScr = autopy.screen.size()
print(f"Screen size: {wScr} x {hScr}")

while True:
    success, img = cap.read()
    if not success or img is None:
        print("❌ Failed to grab frame from webcam.")
        continue

    # Find hand and landmarks
    img = detector.findHands(img)
    lmList, bbox = detector.findPosition(img)

    if len(lmList) != 0:
        # Tip of index and middle fingers
        x1, y1 = lmList[8][1:]
        x2, y2 = lmList[12][1:]

        # Fingers up
        fingers = detector.fingersUp()

        # Move Mode: index finger up only
        if fingers[1] == 1 and fingers[2] == 0:
            # Convert coordinates
            x3 = np.interp(x1, (frameR, wCam - frameR), (0, wScr))
            y3 = np.interp(y1, (frameR, hCam - frameR), (0, hScr))

            # Smoothen values
            clocX = plocX + (x3 - plocX) / smoothening
            clocY = plocY + (y3 - plocY) / smoothening

            # Move mouse
            autopy.mouse.move(wScr - clocX, clocY)
            plocX, plocY = clocX, clocY

            # Optional: show circle at finger
            cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)

        # Click Mode: both index and middle fingers up
        if fingers[1] == 1 and fingers[2] == 1:
            length = np.hypot(x2 - x1, y2 - y1)
            if length < 40:
                cv2.circle(img, ((x1 + x2) // 2, (y1 + y2) // 2), 15, (0, 255, 0), cv2.FILLED)
                autopy.mouse.click()

    # FPS
    cTime = time.time()
    fps = 1 / (cTime - pTime) if cTime != pTime else 0
    pTime = cTime
    cv2.putText(img, f'FPS: {int(fps)}', (20, 50),
                cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)

    # Show window
    cv2.imshow("Virtual Mouse", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()
