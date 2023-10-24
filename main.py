import base64
import uvicorn

from fastapi import FastAPI
from fastapi.responses import StreamingResponse, JSONResponse

import cv2

app = FastAPI()


@app.middleware("http")
async def middleware(request, call_next):

    ## Check Auth
    try:
        auth = request.headers.get('Authorization')
        scheme, data = (auth or ' ').split(' ', 1)
        if scheme != 'Basic': 
            return False
        username, password = base64.b64decode(data).decode().split(':', 1)
        if username == 'admin' and password == 'masterkey':
            response = call_next(request)
            return response
        else:
            return JSONResponse(status_code=403, content={"message": "Unauthorized"})
        
    except Exception as ex:
        return JSONResponse(status_code=401, content={"message": "Unauthorized"})

def gen_frames():
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

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
