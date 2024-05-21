from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import subprocess
import sys

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins='*')

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('run code')
def handle_code(data):
    code = data['code']
    expected_output = data['expectedOutput']
    correct_code = """def sum_numbers():
    total = 0
    for i in range(1, 101):
        total += i
    return total

print(sum_numbers())"""

    try:
        result = subprocess.run([sys.executable, '-c', code], capture_output=True, text=True, timeout=5)
        stdout = result.stdout.strip()
        stderr = result.stderr.strip()

        if stderr:
            emit('code output', {'error': stderr})
        else:
            emit('code output', {'output': stdout})
            if code.strip() == correct_code.strip():
                emit('test result', {'result': 'Test başarılı: Kod doğru ve çıktı doğru!'})
            elif stdout == expected_output:
                emit('test result', {'result': 'Test başarılı: Doğru çıktı fakat çözüm yanlış geçersiz kod!'})
            else:
                emit('test result', {'result': f'Test başarısız oldu: {expected_output} bekleniyordu, ancak {stdout} çıktı'})
    except subprocess.TimeoutExpired:
        emit('code output', {'error': 'Code execution timed out'})
        emit('test result', {'result': 'Test failed: Code execution timed out'})

if __name__ == '__main__':
    socketio.run(app, debug=True)
