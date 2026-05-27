import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_from_directory
from flask_socketio import SocketIO, emit, join_room, leave_room
import sqlite3
import hashlib
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.config['SECRET_KEY'] = 'secret_key_here_12345'
app.config['UPLOAD_FOLDER'] = '../uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'webm', 'mov'}

socketio = SocketIO(app, cors_allowed_origins="*")

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def init_db():
    conn = sqlite3.connect('chat.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id TEXT PRIMARY KEY, username TEXT UNIQUE, password TEXT, nickname TEXT, status TEXT DEFAULT 'pending', created_at TEXT, chat_enabled INTEGER DEFAULT 1, upload_enabled INTEGER DEFAULT 1)''')
    c.execute('''CREATE TABLE IF NOT EXISTS messages
                 (id TEXT PRIMARY KEY, sender_id TEXT, receiver_id TEXT, content TEXT, timestamp TEXT, file_type TEXT, file_url TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS admins
                 (id TEXT PRIMARY KEY, username TEXT UNIQUE, password TEXT, created_at TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS friend_requests
                 (id TEXT PRIMARY KEY, sender_id TEXT, receiver_id TEXT, status TEXT DEFAULT 'pending', created_at TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS friendships
                 (id TEXT PRIMARY KEY, user1_id TEXT, user2_id TEXT, created_at TEXT)''')
    
    try:
        c.execute("ALTER TABLE messages ADD COLUMN file_type TEXT")
    except:
        pass
    try:
        c.execute("ALTER TABLE messages ADD COLUMN file_url TEXT")
    except:
        pass
    
    try:
        c.execute("ALTER TABLE users ADD COLUMN status TEXT DEFAULT 'pending'")
    except:
        pass
    try:
        c.execute("ALTER TABLE users ADD COLUMN created_at TEXT")
    except:
        pass
    try:
        c.execute("ALTER TABLE users ADD COLUMN chat_enabled INTEGER DEFAULT 1")
    except:
        pass
    try:
        c.execute("ALTER TABLE users ADD COLUMN upload_enabled INTEGER DEFAULT 1")
    except:
        pass
    try:
        c.execute("ALTER TABLE users ADD COLUMN avatar TEXT")
    except:
        pass
    
    c.execute('SELECT * FROM admins WHERE username = ?', ('admin',))
    if not c.fetchone():
        admin_id = str(uuid.uuid4())
        admin_pwd = hashlib.sha256('admin123'.encode()).hexdigest()
        c.execute('INSERT INTO admins (id, username, password, created_at) VALUES (?, ?, ?, ?)',
                  (admin_id, 'admin', admin_pwd, datetime.now().isoformat()))
        conn.commit()
    
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_user(username):
    conn = sqlite3.connect('chat.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = c.fetchone()
    conn.close()
    if user:
        return {
            'id': user[0], 
            'username': user[1], 
            'password': user[2], 
            'nickname': user[3],
            'status': user[4] if len(user) > 4 else 'pending',
            'created_at': user[5] if len(user) > 5 else None,
            'chat_enabled': user[6] if len(user) > 6 else 1,
            'upload_enabled': user[7] if len(user) > 7 else 1,
            'avatar': user[8] if len(user) > 8 else None
        }
    return None

def get_user_by_id(user_id):
    conn = sqlite3.connect('chat.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = c.fetchone()
    conn.close()
    if user:
        return {
            'id': user[0], 
            'username': user[1], 
            'password': user[2], 
            'nickname': user[3],
            'status': user[4] if len(user) > 4 else 'pending',
            'created_at': user[5] if len(user) > 5 else None,
            'chat_enabled': user[6] if len(user) > 6 else 1,
            'upload_enabled': user[7] if len(user) > 7 else 1,
            'avatar': user[8] if len(user) > 8 else None
        }
    return None

def save_message(sender_id, receiver_id, content, file_type=None, file_url=None):
    conn = sqlite3.connect('chat.db')
    c = conn.cursor()
    msg_id = str(uuid.uuid4())
    timestamp = datetime.now().isoformat()
    c.execute('INSERT INTO messages (id, sender_id, receiver_id, content, file_type, file_url, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?)',
              (msg_id, sender_id, receiver_id, content, file_type, file_url, timestamp))
    conn.commit()
    conn.close()
    return msg_id, timestamp

def get_messages(user1_id, user2_id):
    conn = sqlite3.connect('chat.db')
    c = conn.cursor()
    c.execute('''SELECT * FROM messages WHERE
                 (sender_id = ? AND receiver_id = ?) OR (sender_id = ? AND receiver_id = ?)
                 ORDER BY timestamp ASC''', (user1_id, user2_id, user2_id, user1_id))
    messages = []
    for row in c.fetchall():
        sender = get_user_by_id(row[1])
        receiver = get_user_by_id(row[2])
        messages.append({
            'id': row[0],
            'sender_id': row[1],
            'receiver_id': row[2],
            'content': row[3],
            'timestamp': row[4],
            'file_type': row[5] if len(row) > 5 else None,
            'file_url': row[6] if len(row) > 6 else None,
            'sender_avatar': sender.get('avatar') if sender else None,
            'sender_nickname': sender.get('nickname') if sender else None,
            'receiver_avatar': receiver.get('avatar') if receiver else None,
            'receiver_nickname': receiver.get('nickname') if receiver else None
        })
    conn.close()
    return messages

def get_all_users():
    conn = sqlite3.connect('chat.db')
    c = conn.cursor()
    c.execute('SELECT id, username, nickname, avatar FROM users')
    users = []
    for row in c.fetchall():
        users.append({
            'id': row[0], 
            'username': row[1], 
            'nickname': row[2],
            'avatar': row[3] if len(row) > 3 else None
        })
    conn.close()
    return users

def get_friends(user_id):
    conn = sqlite3.connect('chat.db')
    c = conn.cursor()
    c.execute('''SELECT u.id, u.username, u.nickname, u.avatar FROM friendships f
                 JOIN users u ON (f.user1_id = u.id OR f.user2_id = u.id)
                 WHERE (f.user1_id = ? OR f.user2_id = ?) AND u.id != ?''', 
              (user_id, user_id, user_id))
    friends = []
    for row in c.fetchall():
        friends.append({
            'id': row[0],
            'username': row[1],
            'nickname': row[2],
            'avatar': row[3] if len(row) > 3 else None
        })
    conn.close()
    return friends

def get_friend_requests(user_id):
    conn = sqlite3.connect('chat.db')
    c = conn.cursor()
    c.execute('''SELECT fr.id, fr.sender_id, u.username, u.nickname, u.avatar, fr.created_at 
                 FROM friend_requests fr
                 JOIN users u ON fr.sender_id = u.id
                 WHERE fr.receiver_id = ? AND fr.status = 'pending'
                 ORDER BY fr.created_at DESC''', (user_id,))
    requests = []
    for row in c.fetchall():
        requests.append({
            'id': row[0],
            'sender_id': row[1],
            'sender_username': row[2],
            'sender_nickname': row[3],
            'sender_avatar': row[4] if len(row) > 4 else None,
            'created_at': row[5]
        })
    conn.close()
    return requests

def is_friend(user1_id, user2_id):
    conn = sqlite3.connect('chat.db')
    c = conn.cursor()
    c.execute('''SELECT * FROM friendships 
                 WHERE (user1_id = ? AND user2_id = ?) OR (user1_id = ? AND user2_id = ?)''',
              (user1_id, user2_id, user2_id, user1_id))
    result = c.fetchone()
    conn.close()
    return result is not None

def has_pending_request(sender_id, receiver_id):
    conn = sqlite3.connect('chat.db')
    c = conn.cursor()
    c.execute('''SELECT * FROM friend_requests 
                 WHERE sender_id = ? AND receiver_id = ? AND status = 'pending' ''',
              (sender_id, receiver_id))
    result = c.fetchone()
    conn.close()
    return result is not None

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = get_user_by_id(session['user_id'])
    if not user:
        return redirect(url_for('login'))
    return render_template('chat.html', user=user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_pwd = hash_password(password)
        user = get_user(username)
        if user and user['password'] == hashed_pwd:
            session['user_id'] = user['id']
            return redirect(url_for('index'))
        return render_template('login.html', error='用户名或密码错误')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        nickname = request.form['nickname']

        if get_user(username):
            return render_template('register.html', error='用户名已存在')

        user_id = str(uuid.uuid4())
        hashed_pwd = hash_password(password)
        created_at = datetime.now().isoformat()

        conn = sqlite3.connect('chat.db')
        c = conn.cursor()
        c.execute('INSERT INTO users (id, username, password, nickname, status, created_at, chat_enabled, upload_enabled) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                  (user_id, username, hashed_pwd, nickname, 'pending', created_at, 1, 1))
        conn.commit()
        conn.close()

        session['user_id'] = user_id
        return redirect(url_for('index'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)

        file_url = f"/uploads/{unique_filename}"

        file_type = 'image' if filename.lower().endswith(('png', 'jpg', 'jpeg', 'gif', 'webp')) else 'video'

        return jsonify({
            'url': file_url,
            'type': file_type,
            'filename': unique_filename
        })
    
    return jsonify({'error': 'File type not allowed'}), 400

@app.route('/api/avatar', methods=['POST'])
def upload_avatar():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    if 'avatar' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['avatar']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
    
    if ext not in allowed_extensions:
        return jsonify({'error': 'File type not allowed'}), 400
    
    filename = secure_filename(file.filename)
    unique_filename = f"avatar_{uuid.uuid4().hex}_{filename}"
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
    file.save(file_path)
    
    avatar_url = f"/uploads/{unique_filename}"
    
    conn = sqlite3.connect('chat.db')
    c = conn.cursor()
    c.execute('UPDATE users SET avatar = ? WHERE id = ?', (avatar_url, session['user_id']))
    conn.commit()
    conn.close()
    
    return jsonify({'url': avatar_url})

@app.route('/api/avatar', methods=['GET'])
def get_avatar():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user = get_user_by_id(session['user_id'])
    if user and user.get('avatar'):
        return jsonify({'url': user['avatar']})
    
    return jsonify({'url': None})

@app.route('/api/users/<user_id>/avatar', methods=['GET'])
def get_user_avatar(user_id):
    user = get_user_by_id(user_id)
    if user and user.get('avatar'):
        return jsonify({'url': user['avatar']})
    return jsonify({'url': None})

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/api/users')
def api_users():
    if 'user_id' not in session:
        return jsonify([])
    users = get_all_users()
    current_user_id = session['user_id']
    users = [u for u in users if u['id'] != current_user_id]
    return jsonify(users)

@app.route('/api/user/nickname', methods=['PUT'])
def update_nickname():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    new_nickname = data.get('nickname')
    
    if not new_nickname or len(new_nickname.strip()) == 0:
        return jsonify({'error': '昵称不能为空'}), 400
    
    conn = sqlite3.connect('chat.db')
    c = conn.cursor()
    c.execute('UPDATE users SET nickname = ? WHERE id = ?', (new_nickname.strip(), session['user_id']))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'nickname': new_nickname.strip()})

@socketio.on('join')
def handle_join():
    if 'user_id' in session:
        user_id = session['user_id']
        join_room(user_id)
        print(f'User {user_id} joined room')

@socketio.on('leave')
def handle_leave():
    if 'user_id' in session:
        leave_room(session['user_id'])

@socketio.on('send_message')
def handle_send_message(data):
    if 'user_id' not in session:
        print('ERROR: user_id not in session')
        return

    sender_id = session['user_id']
    receiver_id = data['receiver_id']
    content = data.get('content', '')
    file_type = data.get('file_type')
    file_url = data.get('file_url')

    print(f'Sending message from {sender_id} to {receiver_id}: {content}')

    msg_id, timestamp = save_message(sender_id, receiver_id, content, file_type, file_url)
    
    sender = get_user_by_id(sender_id)
    sender_nickname = sender.get('nickname') if sender else None
    sender_avatar = sender.get('avatar') if sender else None

    message_data = {
        'id': msg_id,
        'sender_id': sender_id,
        'receiver_id': receiver_id,
        'content': content,
        'file_type': file_type,
        'file_url': file_url,
        'timestamp': timestamp,
        'sender_nickname': sender_nickname,
        'sender_avatar': sender_avatar
    }

    emit('receive_message', message_data, room=receiver_id)
    emit('receive_message', message_data, room=sender_id)
    print(f'Message emitted to rooms: {receiver_id} and {sender_id}')

@socketio.on('send_friend_request')
def handle_friend_request(data):
    if 'user_id' not in session:
        return
    
    sender_id = session['user_id']
    receiver_id = data.get('receiver_id')
    
    if is_friend(sender_id, receiver_id):
        emit('friend_request_response', {'success': False, 'error': '已经是好友'})
        return
    
    if has_pending_request(sender_id, receiver_id):
        emit('friend_request_response', {'success': False, 'error': '请求已发送'})
        return
    
    request_id = str(uuid.uuid4())
    conn = sqlite3.connect('chat.db')
    c = conn.cursor()
    c.execute('INSERT INTO friend_requests (id, sender_id, receiver_id, status, created_at) VALUES (?, ?, ?, ?, ?)',
              (request_id, sender_id, receiver_id, 'pending', datetime.now().isoformat()))
    conn.commit()
    conn.close()
    
    sender = get_user_by_id(sender_id)
    emit('friend_request_response', {'success': True, 'sender_nickname': sender.get('nickname')})
    emit('friend_request_notification', {
        'request_id': request_id,
        'sender_id': sender_id,
        'sender_nickname': sender.get('nickname'),
        'sender_avatar': sender.get('avatar')
    }, room=receiver_id)

@app.route('/api/friends')
def api_get_friends():
    if 'user_id' not in session:
        return jsonify([])
    friends = get_friends(session['user_id'])
    return jsonify(friends)

@app.route('/api/friend-requests')
def api_get_friend_requests():
    if 'user_id' not in session:
        return jsonify([])
    requests = get_friend_requests(session['user_id'])
    return jsonify(requests)

@app.route('/api/friend-requests/count')
def api_get_friend_request_count():
    if 'user_id' not in session:
        return jsonify({'count': 0})
    requests = get_friend_requests(session['user_id'])
    return jsonify({'count': len(requests)})

@app.route('/api/friend-requests/<request_id>/accept', methods=['POST'])
def api_accept_friend_request(request_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = sqlite3.connect('chat.db')
    c = conn.cursor()
    c.execute('SELECT * FROM friend_requests WHERE id = ? AND receiver_id = ? AND status = ?',
              (request_id, session['user_id'], 'pending'))
    request_data = c.fetchone()
    
    if not request_data:
        conn.close()
        return jsonify({'success': False, 'error': '请求不存在或已处理'})
    
    sender_id = request_data[1]
    friendship_id = str(uuid.uuid4())
    
    c.execute('INSERT INTO friendships (id, user1_id, user2_id, created_at) VALUES (?, ?, ?, ?)',
              (friendship_id, session['user_id'], sender_id, datetime.now().isoformat()))
    c.execute('UPDATE friend_requests SET status = ? WHERE id = ?', ('accepted', request_id))
    conn.commit()
    conn.close()
    
    receiver = get_user_by_id(session['user_id'])
    emit('friend_request_accepted', {
        'friend_id': session['user_id'],
        'friend_nickname': receiver.get('nickname'),
        'friend_avatar': receiver.get('avatar')
    }, room=sender_id)
    
    return jsonify({'success': True})

@app.route('/api/friend-requests/<request_id>/reject', methods=['POST'])
def api_reject_friend_request(request_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = sqlite3.connect('chat.db')
    c = conn.cursor()
    c.execute('SELECT * FROM friend_requests WHERE id = ? AND receiver_id = ? AND status = ?',
              (request_id, session['user_id'], 'pending'))
    request_data = c.fetchone()
    
    if not request_data:
        conn.close()
        return jsonify({'success': False, 'error': '请求不存在或已处理'})
    
    c.execute('UPDATE friend_requests SET status = ? WHERE id = ?', ('rejected', request_id))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/api/friends/<friend_id>', methods=['DELETE'])
def api_remove_friend(friend_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = sqlite3.connect('chat.db')
    c = conn.cursor()
    c.execute('DELETE FROM friendships WHERE (user1_id = ? AND user2_id = ?) OR (user1_id = ? AND user2_id = ?)',
              (session['user_id'], friend_id, friend_id, session['user_id']))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/api/search-users')
def api_search_users():
    if 'user_id' not in session:
        return jsonify([])
    
    query = request.args.get('q', '')
    if not query:
        return jsonify([])
    
    conn = sqlite3.connect('chat.db')
    c = conn.cursor()
    c.execute('SELECT id, username, nickname, avatar FROM users WHERE username LIKE ? OR nickname LIKE ?',
              (f'%{query}%', f'%{query}%'))
    users = []
    for row in c.fetchall():
        if row[0] != session['user_id']:
            users.append({
                'id': row[0],
                'username': row[1],
                'nickname': row[2],
                'avatar': row[3] if len(row) > 3 else None
            })
    conn.close()
    return jsonify(users)

@app.route('/api/messages/<receiver_id>')
def api_messages(receiver_id):
    if 'user_id' not in session:
        return jsonify([])
    try:
        messages = get_messages(session['user_id'], receiver_id)
        return jsonify(messages)
    except Exception as e:
        print(f'Error getting messages: {e}')
        return jsonify({'error': str(e)}), 500

# 管理后台路由
def get_admin(username):
    conn = sqlite3.connect('chat.db')
    c = conn.cursor()
    c.execute('SELECT * FROM admins WHERE username = ?', (username,))
    admin = c.fetchone()
    conn.close()
    if admin:
        return {'id': admin[0], 'username': admin[1], 'password': admin[2], 'created_at': admin[3]}
    return None

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        admin = get_admin(username)
        if admin and admin['password'] == hashlib.sha256(password.encode()).hexdigest():
            session['admin_id'] = admin['id']
            session['admin_username'] = admin['username']
            return redirect(url_for('admin_dashboard'))
        
        return render_template('admin_login.html', error='用户名或密码错误')
    
    if 'admin_id' in session:
        return redirect(url_for('admin_dashboard'))
    
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_id', None)
    session.pop('admin_username', None)
    return redirect(url_for('admin_login'))

@app.route('/admin')
def admin_dashboard():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    return render_template('admin.html', admin_username=session.get('admin_username'))

@app.route('/api/admin/users')
def admin_get_users():
    if 'admin_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    conn = sqlite3.connect('chat.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users ORDER BY created_at DESC')
    users = []
    for row in c.fetchall():
        users.append({
            'id': row[0],
            'username': row[1],
            'password': row[2],
            'nickname': row[3],
            'status': row[4] if len(row) > 4 else 'pending',
            'created_at': row[5] if len(row) > 5 else None,
            'chat_enabled': row[6] if len(row) > 6 else 1,
            'upload_enabled': row[7] if len(row) > 7 else 1,
            'avatar': row[8] if len(row) > 8 else None
        })
    conn.close()
    return jsonify(users)

@app.route('/api/admin/users/<user_id>')
def admin_get_user(user_id):
    if 'admin_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    user = get_user_by_id(user_id)
    if user:
        return jsonify(user)
    return jsonify({'error': 'User not found'}), 404

@app.route('/api/admin/users/<user_id>', methods=['PUT'])
def admin_update_user(user_id):
    if 'admin_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.get_json()
    conn = sqlite3.connect('chat.db')
    c = conn.cursor()
    
    updates = []
    params = []
    
    if 'nickname' in data:
        updates.append('nickname = ?')
        params.append(data['nickname'])
    if 'status' in data:
        updates.append('status = ?')
        params.append(data['status'])
    if 'chat_enabled' in data:
        updates.append('chat_enabled = ?')
        params.append(1 if data['chat_enabled'] else 0)
    if 'upload_enabled' in data:
        updates.append('upload_enabled = ?')
        params.append(1 if data['upload_enabled'] else 0)
    
    params.append(user_id)
    
    if updates:
        c.execute(f'UPDATE users SET {", ".join(updates)} WHERE id = ?', params)
        conn.commit()
    
    conn.close()
    return jsonify({'success': True})

@app.route('/api/admin/users/<user_id>', methods=['DELETE'])
def admin_delete_user(user_id):
    if 'admin_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    conn = sqlite3.connect('chat.db')
    c = conn.cursor()
    c.execute('DELETE FROM users WHERE id = ?', (user_id,))
    c.execute('DELETE FROM messages WHERE sender_id = ? OR receiver_id = ?', (user_id, user_id))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/admin/users/<user_id>/permissions', methods=['PUT'])
def admin_update_permissions(user_id):
    if 'admin_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.get_json()
    conn = sqlite3.connect('chat.db')
    c = conn.cursor()
    c.execute('UPDATE users SET chat_enabled = ?, upload_enabled = ? WHERE id = ?',
              (1 if data.get('chat_enabled') else 0, 1 if data.get('upload_enabled') else 0, user_id))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/admin/messages')
def admin_get_messages():
    if 'admin_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    conn = sqlite3.connect('chat.db')
    c = conn.cursor()
    c.execute('SELECT * FROM messages ORDER BY timestamp DESC LIMIT 100')
    messages = []
    for row in c.fetchall():
        messages.append({
            'id': row[0],
            'sender_id': row[1],
            'receiver_id': row[2],
            'content': row[3],
            'timestamp': row[4],
            'file_type': row[5] if len(row) > 5 else None,
            'file_url': row[6] if len(row) > 6 else None
        })
    conn.close()
    return jsonify(messages)

@app.route('/api/admin/messages/<msg_id>', methods=['DELETE'])
def admin_delete_message(msg_id):
    if 'admin_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    conn = sqlite3.connect('chat.db')
    c = conn.cursor()
    c.execute('DELETE FROM messages WHERE id = ?', (msg_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/admin/settings', methods=['PUT'])
def admin_update_settings():
    if 'admin_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.get_json()
    conn = sqlite3.connect('chat.db')
    c = conn.cursor()
    
    try:
        c.execute('CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)')
        
        settings = ['default_user_status', 'max_file_size', 'allowed_image_types', 'allowed_video_types']
        for key in settings:
            if key in data:
                c.execute('INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)', (key, str(data[key])))
        
        conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/admin/change-password', methods=['POST'])
def admin_change_password():
    if 'admin_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    current_password = data.get('currentPassword')
    new_password = data.get('newPassword')
    
    if not current_password or not new_password:
        return jsonify({'error': '请填写所有字段'}), 400
    
    if len(new_password) < 6:
        return jsonify({'error': '新密码长度至少为6位'}), 400
    
    admin = get_admin(session.get('admin_username'))
    if not admin:
        return jsonify({'error': '管理员不存在'}), 404
    
    if admin['password'] != hashlib.sha256(current_password.encode()).hexdigest():
        return jsonify({'error': '当前密码不正确'}), 400
    
    conn = sqlite3.connect('chat.db')
    c = conn.cursor()
    c.execute('UPDATE admins SET password = ? WHERE id = ?',
              (hashlib.sha256(new_password.encode()).hexdigest(), admin['id']))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

if __name__ == '__main__':
    init_db()
    socketio.run(app, debug=True, host='0.0.0.0', port=9999)