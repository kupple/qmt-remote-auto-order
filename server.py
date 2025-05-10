from flask import Flask, request
from flask_socketio import SocketIO, send, join_room, leave_room
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# 存储客户端 sid 与 MAC 地址的映射
client_mac_mapping = {}


@socketio.on('connect')
def handle_connect():
    print('Client connected.')


@socketio.on('join_with_mac')
def handle_join_with_mac(mac_address):
    # 绑定 MAC 地址与客户端 sid
    client_mac_mapping[request.sid] = mac_address
    # 加入以 MAC 地址命名的房间
    join_room(mac_address)
    # 发送确认消息给客户端
    send({'status': 'success', 'client_id': mac_address, 'message': f'Joined room with MAC: {mac_address}'})
    print(f'Client with sid {request.sid} joined room with MAC: {mac_address}')


@socketio.on('disconnect')
def handle_disconnect():
    mac_address = client_mac_mapping.pop(request.sid, None)
    if mac_address:
        leave_room(mac_address)
    print('Client disconnected.')


@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.get_json()
    message = data.get('message')
    client_id = data.get('client_id')
    if message and client_id:
        socketio.send(message, to=client_id)
        return {'status': 'success'}, 200
    return {'status': 'error', 'message': 'No message or client_id provided'}, 400


if __name__ == '__main__':
    socketio.run(app, debug=True)
    