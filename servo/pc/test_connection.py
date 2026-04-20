import socket

def test_connection():
    print('Testing socket connection...')
    try:
        s = socket.socket()
        s.connect(('192.168.3.151', 83))
        print('Connection successful!')
        s.close()
    except Exception as e:
        print('Connection failed:', e)

if __name__ == '__main__':
    test_connection()
