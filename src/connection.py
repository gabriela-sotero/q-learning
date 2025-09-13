import socket
import ast

def connect(port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('127.0.0.1', port))
        print('Connection established.')
        return s
    except:
        print('Connection failed.')
        return 0

def get_state_reward(sock, action):
    sock.send(str(action).encode())
    data_received = False

    while not data_received:
        raw = sock.recv(1024).decode().strip()

        try:
            data = ast.literal_eval(raw)
                        # 🩹 Corrige campos em português, se necessário
            if 'estado' in data:
                data['state'] = data.pop('estado')
            if 'recompensa' in data:
                data['reward'] = data.pop('recompensa')
            data_received = True
        except:
            data_received = False
            
    return data['state'], data['reward']

