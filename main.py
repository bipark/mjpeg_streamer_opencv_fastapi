import uvicorn

from fastapi import FastAPI
from fastapi.responses import StreamingResponse

import cv2

app = FastAPI()

def gen_frames():
    cap = cv2.VideoCapture(0)
    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.get('/')
async def index():
    return StreamingResponse(gen_frames(), media_type='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=7900, log_level="info", reload=True)
