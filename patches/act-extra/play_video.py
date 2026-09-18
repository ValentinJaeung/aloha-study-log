import cv2, sys

path = sys.argv[1]
cap = cv2.VideoCapture(path)
if not cap.isOpened():
    print(f'Cannot open video: {path}')
    sys.exit(1)

fps = cap.get(cv2.CAP_PROP_FPS) or 50
delay = int(1000 / fps)

while True:
    ok, frame = cap.read()
    if not ok:
        break
    cv2.imshow('episode', frame)
    if cv2.waitKey(delay) & 0xFF == ord('q'):   # q 누르면 종료
        break

cap.release()
cv2.destroyAllWindows()
