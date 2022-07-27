import serial
import flask

app = flask.Flask(__name__)
arduino = None

@app.route('/', methods=['POST','OPTIONS'])
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

if __name__ == '__main__':
    app.run()