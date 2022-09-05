import serial
import flask
import cv2


app = flask.Flask(__name__, static_url_path='', static_folder='front_end')
arduino = None
rtsp_url = 'rtsp://user:pass@192.168.0.0'


def video_feed():
    cap = cv2.VideoCapture(rtsp_url)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    while True:
        ret, frame = cap.read()
        result, encimg = cv2.imencode('.jpg', frame)
        b = encimg.tobytes()
        m = f'--frame\r\nContent-Type: image/jpeg\r\nContent-Length: {len(b)}\r\n\r\n'
        yield (m.encode() + b)


@app.route('/api', methods=['POST','OPTIONS'])
def root_post():
    if flask.request.method == 'POST': # CORS preflight
        global arduino
        print(flask.request.json)

        if not arduino:
            arduino = serial.Serial(port='/dev/ttyUSB0', baudrate=9600, timeout=.1)
            pass

        payload = [0,80,0]
        payload[0] = flask.request.json['modulo']
        payload[1] = flask.request.json['direcao']
        payload[2] = flask.request.json['sentido']
        if arduino:
            arduino.write(bytearray(payload))

        response = flask.make_response()
        response.status_code = 200
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response
    else:
        response = flask.make_response()
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "Content-Type")
        response.headers.add('Access-Control-Allow-Methods', "POST")
        return response


@app.route('/video')
def video():
    return flask.Response(video_feed(), mimetype='multipart/x-mixed-replace; boundary=--frame')


if __name__ == '__main__':
    app.run()