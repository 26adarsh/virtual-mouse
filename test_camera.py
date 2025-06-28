import cv2

cap = cv2.VideoCapture(0)  # Try 0, 1, or 2

while True:
    success, frame = cap.read()
    if not success:
        print("❌ Failed to read from webcam")
        break

    cv2.imshow("Webcam Test", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
