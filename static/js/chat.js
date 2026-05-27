let socket = null;
let selectedUser = null;
let currentUserAvatar = null;
let currentTab = 'friends';
let allFriends = [];
let allUsers = [];

const emojiData = {
    smile: ['😀', '😃', '😄', '😁', '😆', '😅', '🤣', '😂', '🙂', '😊', '😇', '🥰', '😍', '🤩', '😘', '😗', '😚', '😙', '😋', '😛', '😜', '🤪', '😝', '🤑', '🤗', '🤭', '🤫', '🤔', '🤐', '🤨', '😐', '😑', '😶', '😏', '😒', '🙄', '😬', '🤥', '😌', '😔', '😪', '🤤', '😴', '😷', '🤒', '🤕', '🤢', '🤮', '🤧', '🥵', '🥶', '🥴', '😵', '🤯'],
    love: ['❤️', '🧡', '💛', '💚', '💙', '💜', '🖤', '🤍', '🤎', '💔', '❣️', '💕', '💞', '💓', '💗', '💖', '💘', '💝', '💟', '💋', '💌', '💍', '💎', '💏', '💑', '👩‍❤️‍👨', '👨‍❤️‍👨', '👩‍❤️‍💋‍👨', '👩‍❤️‍💋‍👩', '💑', '💏', '👪'],
    hand: ['👋', '🤚', '🖐️', '✋', '🖖', '👌', '🤌', '🤏', '✌️', '🤞', '🤟', '🤘', '🤙', '👈', '👉', '👆', '🖕', '👇', '☝️', '👍', '👎', '✊', '👊', '🤛', '🤜', '👏', '🙌', '👐', '🤲', '🤝', '🙏'],
    animal: ['🐱', '🐶', '🐭', '🐹', '🐰', '🦊', '🐻', '🐼', '🐨', '🐯', '🦁', '🐮', '🐷', '🐸', '🐵', '🐔', '🐧', '🐦', '🐤', '🦆', '🦅', '🦉', '🦇', '🐺', '🐗', '🐴', '🦄', '🐝', '🐛', '🦋', '🐌', '🐞', '🐜', '🦟', '🦗', '🕷️', '🦂', '🐢', '🐍', '🦎', '🦖', '🦕', '🐙', '🦑', '🦐', '🦞', '🦀', '🐡', '🐠', '🐟', '🐬', '🐳', '🐋', '🦈'],
    food: ['🍔', '🍕', '🍟', '🌭', '🍿', '🧂', '🥓', '🥚', '🍳', '🧇', '🥞', '🧈', '🍞', '🥐', '🥖', '🥨', '🧀', '🥗', '🥙', '🥪', '🌮', '🌯', '🫔', '🥫', '🍝', '🍜', '🍲', '🍛', '🍣', '🍱', '🥟', '🦪', '🍤', '🍙', '🍚', '🍘', '🍥', '🥠', '🥮', '🍢', '🍡', '🍧', '🍨', '🍦', '🥧', '🧁', '🍰', '🎂', '🍮', '🍭', '🍬', '🍫', '🍿', '🍩', '🍪', '🌰', '🥜', '🍯', '🥛', '🍼', '☕', '🫖', '🍵', '🧃', '🥤', '🍶', '🍺', '🍻', '🥂', '🍷', '🥃', '🍸', '🍹'],
    activity: ['⚽', '🏀', '🏈', '⚾', '🥎', '🎾', '🏐', '🏉', '🥏', '🎱', '🪀', '🏓', '🏸', '🏒', '🏑', '🥍', '🏏', '🪃', '🥅', '⛳', '🪁', '🏹', '🎣', '🤿', '🥊', '🥋', '🎽', '🛹', '🛼', '🛷', '⛸️', '🥌', '🎿', '⛷️', '🏂', '🪂', '🏋️', '🤼', '🤸', '🤺', '⛹️', '🤾', '🏌️', '🏇', '🧘']
};

document.addEventListener('DOMContentLoaded', () => {
    loadFriends();
    loadFriendRequestCount();
    loadCurrentUserAvatar();
    initSocket();

    const messageInput = document.getElementById('messageInput');
    const sendBtn = document.getElementById('sendBtn');
    const searchInput = document.getElementById('searchInput');
    const fileInput = document.getElementById('fileInput');
    const avatarInput = document.getElementById('avatarInput');
    const emojiBtn = document.getElementById('emojiBtn');
    const emojiPanel = document.getElementById('emojiPanel');

    sendBtn.addEventListener('click', sendMessage);
    messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    searchInput.addEventListener('input', handleSearch);

    fileInput.addEventListener('change', handleFileSelect);
    
    if (avatarInput) {
        avatarInput.addEventListener('change', handleAvatarSelect);
    }

    emojiBtn.addEventListener('click', toggleEmojiPanel);

    document.addEventListener('click', (e) => {
        if (!emojiPanel.contains(e.target) && e.target !== emojiBtn) {
            emojiPanel.style.display = 'none';
        }
    });

    initEmojiPanel();
});

function loadCurrentUserAvatar() {
    fetch('/api/avatar')
        .then(response => response.json())
        .then(data => {
            if (data.url) {
                currentUserAvatar = data.url;
                updateUserAvatarDisplay(data.url);
            }
        });
}

function updateUserAvatarDisplay(avatarUrl) {
    const userAvatar = document.getElementById('userAvatar');
    if (userAvatar && avatarUrl) {
        userAvatar.innerHTML = `<img src="${avatarUrl}" alt="头像">`;
    }
}

function handleAvatarSelect(e) {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('avatar', file);

    fetch('/api/avatar', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.url) {
            currentUserAvatar = data.url;
            updateUserAvatarDisplay(data.url);
        }
    })
    .catch(error => {
        console.error('Avatar upload error:', error);
    });

    e.target.value = '';
}

function editNickname() {
    document.getElementById('currentNickname').style.display = 'none';
    document.querySelector('.edit-nickname').style.display = 'none';
    document.getElementById('nicknameInput').style.display = 'inline';
    document.getElementById('saveNicknameBtn').style.display = 'inline';
    document.getElementById('cancelNicknameBtn').style.display = 'inline';
    document.getElementById('nicknameInput').focus();
}

function cancelNicknameEdit() {
    document.getElementById('currentNickname').style.display = 'inline';
    document.querySelector('.edit-nickname').style.display = 'inline';
    document.getElementById('nicknameInput').style.display = 'none';
    document.getElementById('saveNicknameBtn').style.display = 'none';
    document.getElementById('cancelNicknameBtn').style.display = 'none';
    document.getElementById('nicknameInput').value = '';
}

function saveNickname() {
    const newNickname = document.getElementById('nicknameInput').value.trim();
    
    if (!newNickname) {
        alert('请输入昵称');
        return;
    }

    fetch('/api/user/nickname', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ nickname: newNickname })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            document.getElementById('currentNickname').textContent = data.nickname;
            cancelNicknameEdit();
            loadFriends();
        } else {
            alert(data.error || '修改失败');
        }
    });
}

function initSocket() {
    socket = io('http://localhost:9999');

    socket.on('connect', () => {
        socket.emit('join');
    });

    socket.on('receive_message', (message) => {
        console.log('Received message:', message);
        if (selectedUser && message.sender_id === selectedUser.id) {
            displayMessage(message);
            scrollToBottom();
        }
    });

    socket.on('friend_request_notification', (data) => {
        console.log('Friend request received:', data);
        alert(`${data.sender_nickname} 发送了好友请求`);
        loadFriendRequestCount();
        if (currentTab === 'requests') {
            loadFriendRequests();
        }
    });

    socket.on('friend_request_response', (data) => {
        if (data.success) {
            alert('好友请求已发送');
        } else {
            alert(data.error || '发送失败');
        }
    });

    socket.on('friend_request_accepted', (data) => {
        alert(`${data.friend_nickname} 接受了你的好友请求`);
        loadFriends();
    });
}

function switchTab(tab) {
    currentTab = tab;
    
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelector(`.tab-btn[onclick="switchTab('${tab}')"]`).classList.add('active');
    
    document.getElementById('userList').style.display = 'none';
    document.getElementById('friendRequests').style.display = 'none';
    document.getElementById('searchResults').style.display = 'none';
    document.getElementById('searchBox').style.display = 'none';

    if (tab === 'friends') {
        document.getElementById('userList').style.display = 'block';
        loadFriends();
    } else if (tab === 'requests') {
        document.getElementById('friendRequests').style.display = 'block';
        loadFriendRequests();
    } else if (tab === 'search') {
        document.getElementById('searchBox').style.display = 'block';
        document.getElementById('searchResults').style.display = 'block';
        document.getElementById('searchInput').value = '';
        document.getElementById('searchEmpty').style.display = 'block';
    }
}

function loadFriends() {
    fetch('/api/friends')
        .then(response => response.json())
        .then(friends => {
            allFriends = friends;
            renderUserList(friends);
        });
}

function loadFriendRequestCount() {
    fetch('/api/friend-requests/count')
        .then(response => response.json())
        .then(data => {
            const requestsTab = document.querySelector('.tab-btn[onclick="switchTab(\'requests\')"]');
            if (requestsTab) {
                const existingBadge = requestsTab.querySelector('.badge');
                if (existingBadge) {
                    requestsTab.removeChild(existingBadge);
                }
                
                if (data.count > 0) {
                    const badge = document.createElement('span');
                    badge.className = 'badge';
                    badge.textContent = data.count;
                    requestsTab.appendChild(badge);
                }
            }
        });
}

function getLastMessage(friendId, callback) {
    fetch(`/api/messages/${friendId}`)
        .then(response => response.json())
        .then(messages => {
            if (messages.length > 0) {
                const lastMsg = messages[messages.length - 1];
                let preview = '';
                if (lastMsg.file_type === 'image') {
                    preview = '[图片]';
                } else if (lastMsg.file_type === 'video') {
                    preview = '[视频]';
                } else {
                    preview = lastMsg.content.substring(0, 20);
                    if (lastMsg.content.length > 20) {
                        preview += '...';
                    }
                }
                callback(preview, lastMsg.timestamp);
            } else {
                callback('', '');
            }
        })
        .catch(() => {
            callback('', '');
        });
}

function loadFriendRequests() {
    fetch('/api/friend-requests')
        .then(response => response.json())
        .then(requests => {
            renderFriendRequests(requests);
        });
}

function handleSearch() {
    const query = document.getElementById('searchInput').value.trim();
    const resultsDiv = document.getElementById('searchResults');
    const emptyDiv = document.getElementById('searchEmpty');

    if (!query) {
        emptyDiv.style.display = 'block';
        resultsDiv.innerHTML = '';
        return;
    }

    emptyDiv.style.display = 'none';
    
    fetch(`/api/search-users?q=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(users => {
            renderSearchResults(users);
        });
}

function renderSearchResults(users) {
    const resultsDiv = document.getElementById('searchResults');
    resultsDiv.innerHTML = '';

    if (users.length === 0) {
        resultsDiv.innerHTML = '<div class="empty-state"><p>未找到匹配的用户</p></div>';
        return;
    }

    users.forEach(user => {
        const userItem = document.createElement('div');
        userItem.className = 'user-item';
        userItem.dataset.userId = user.id;
        
        const avatarHtml = user.avatar 
            ? `<div class="avatar"><img src="${user.avatar}" alt=""></div>`
            : `<div class="avatar">${user.nickname ? user.nickname[0].toUpperCase() : '?'}</div>`;
        
        userItem.innerHTML = `
            ${avatarHtml}
            <div class="info">
                <div class="name">${user.nickname}</div>
                <div class="username">@${user.username}</div>
            </div>
            <button class="add-friend-btn" onclick="sendFriendRequest('${user.id}')">添加好友</button>
        `;
        resultsDiv.appendChild(userItem);
    });
}

function sendFriendRequest(userId) {
    socket.emit('send_friend_request', { receiver_id: userId });
}

function renderFriendRequests(requests) {
    const requestsDiv = document.getElementById('friendRequests');
    const emptyDiv = document.getElementById('requestsEmpty');

    if (requests.length === 0) {
        emptyDiv.style.display = 'block';
        requestsDiv.innerHTML = '<div class="empty-state" id="requestsEmpty"><p>暂无好友请求</p></div>';
        return;
    }

    emptyDiv.style.display = 'none';
    requestsDiv.innerHTML = '';

    requests.forEach(req => {
        const requestItem = document.createElement('div');
        requestItem.className = 'friend-request-item';
        requestItem.dataset.requestId = req.id;
        
        const avatarHtml = req.sender_avatar 
            ? `<div class="avatar"><img src="${req.sender_avatar}" alt=""></div>`
            : `<div class="avatar">${req.sender_nickname ? req.sender_nickname[0].toUpperCase() : '?'}</div>`;
        
        requestItem.innerHTML = `
            ${avatarHtml}
            <div class="request-info">
                <div class="name">${req.sender_nickname}</div>
                <div class="time">${formatTime(req.created_at)}</div>
            </div>
            <div class="request-actions">
                <button class="accept-btn" onclick="acceptFriendRequest('${req.id}')">接受</button>
                <button class="reject-btn" onclick="rejectFriendRequest('${req.id}')">拒绝</button>
            </div>
        `;
        requestsDiv.appendChild(requestItem);
    });
}

function acceptFriendRequest(requestId) {
    fetch(`/api/friend-requests/${requestId}/accept`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('已添加好友');
            loadFriendRequests();
            loadFriendRequestCount();
            loadFriends();
        } else {
            alert(data.error || '操作失败');
        }
    });
}

function rejectFriendRequest(requestId) {
    fetch(`/api/friend-requests/${requestId}/reject`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            loadFriendRequests();
            loadFriendRequestCount();
        } else {
            alert(data.error || '操作失败');
        }
    });
}

function showFriendMenu(user, element) {
    const existingMenu = document.getElementById('friendMenu');
    if (existingMenu) {
        existingMenu.remove();
    }
    
    const menu = document.createElement('div');
    menu.id = 'friendMenu';
    menu.className = 'friend-menu';
    menu.innerHTML = `
        <button class="menu-item delete-friend" onclick="removeFriendFromMenu('${user.id}', '${user.nickname}')">删除好友</button>
        <button class="menu-item cancel" onclick="closeFriendMenu()">取消</button>
    `;
    
    const rect = element.getBoundingClientRect();
    menu.style.left = rect.left + 'px';
    menu.style.top = rect.bottom + 'px';
    
    document.body.appendChild(menu);
    
    document.addEventListener('click', closeFriendMenuOnClick);
}

function closeFriendMenu() {
    const menu = document.getElementById('friendMenu');
    if (menu) {
        menu.remove();
    }
    document.removeEventListener('click', closeFriendMenuOnClick);
}

function closeFriendMenuOnClick(e) {
    const menu = document.getElementById('friendMenu');
    if (menu && !menu.contains(e.target)) {
        closeFriendMenu();
    }
}

function removeFriendFromMenu(userId, nickname) {
    if (!confirm(`确定要删除好友 ${nickname} 吗？`)) {
        closeFriendMenu();
        return;
    }

    fetch(`/api/friends/${userId}`, {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('已删除好友');
            closeFriendMenu();
            loadFriends();
            if (selectedUser && selectedUser.id === userId) {
                selectedUser = null;
                const messagesDiv = document.getElementById('messages');
                messagesDiv.innerHTML = '<div class="empty-state"><div class="empty-icon">💬</div><p>选择一个联系人开始聊天</p></div>';
                document.getElementById('contactName').textContent = '选择一个联系人开始聊天';
                document.getElementById('contactStatus').textContent = '';
                const messageInput = document.getElementById('messageInput');
                const sendBtn = document.getElementById('sendBtn');
                messageInput.disabled = true;
                sendBtn.disabled = true;
            }
        } else {
            alert(data.error || '删除失败');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('删除失败');
    });
}

function removeFriend() {
    if (!selectedUser) return;
    
    if (!confirm(`确定要删除好友 ${selectedUser.nickname} 吗？`)) {
        return;
    }

    fetch(`/api/friends/${selectedUser.id}`, {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('已删除好友');
            selectedUser = null;
            document.getElementById('removeFriendBtn').style.display = 'none';
            const messagesDiv = document.getElementById('messages');
            messagesDiv.innerHTML = '<div class="empty-state"><div class="empty-icon">💬</div><p>选择一个联系人开始聊天</p></div>';
            document.getElementById('contactName').textContent = '选择一个联系人开始聊天';
            document.getElementById('messageInput').disabled = true;
            document.getElementById('sendBtn').disabled = true;
            loadFriends();
        } else {
            alert(data.error || '操作失败');
        }
    });
}

function formatTime(timestamp) {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now - date;
    
    if (diff < 60000) {
        return '刚刚';
    } else if (diff < 3600000) {
        return `${Math.floor(diff / 60000)}分钟前`;
    } else if (diff < 86400000) {
        return `${Math.floor(diff / 3600000)}小时前`;
    } else {
        return `${date.getMonth() + 1}/${date.getDate()}`;
    }
}

function getCurrentUserId() {
    const userInfo = document.querySelector('.user-info');
    return userInfo ? userInfo.dataset.userId : null;
}

function renderUserList(users) {
    const userList = document.getElementById('userList');
    userList.innerHTML = '';
    window.allUsers = users;

    if (users.length === 0) {
        userList.innerHTML = '<div class="empty-state"><p>暂无好友</p><p style="font-size:12px;color:#999">点击"添加好友"搜索并添加好友</p></div>';
        return;
    }

    users.forEach(user => {
        const userItem = document.createElement('div');
        userItem.className = 'user-item';
        userItem.dataset.userId = user.id;
        
        const avatarHtml = user.avatar 
            ? `<div class="avatar"><img src="${user.avatar}" alt=""></div>`
            : `<div class="avatar">${user.nickname ? user.nickname[0].toUpperCase() : '?'}</div>`;
        
        userItem.innerHTML = `
            ${avatarHtml}
            <div class="info">
                <div class="name">${user.nickname}</div>
                <div class="last-message" id="lastMsg-${user.id}"></div>
            </div>
        `;
        userItem.addEventListener('click', () => selectUser(user));
        
        let longPressTimer = null;
        userItem.addEventListener('mousedown', () => {
            longPressTimer = setTimeout(() => {
                showFriendMenu(user, userItem);
            }, 500);
        });
        userItem.addEventListener('mouseup', () => {
            clearTimeout(longPressTimer);
        });
        userItem.addEventListener('mouseleave', () => {
            clearTimeout(longPressTimer);
        });
        
        userItem.addEventListener('touchstart', () => {
            longPressTimer = setTimeout(() => {
                showFriendMenu(user, userItem);
            }, 500);
        });
        userItem.addEventListener('touchend', () => {
            clearTimeout(longPressTimer);
        });
        
        userList.appendChild(userItem);
        
        getLastMessage(user.id, (preview, timestamp) => {
            const lastMsgDiv = document.getElementById(`lastMsg-${user.id}`);
            if (lastMsgDiv) {
                if (preview) {
                    lastMsgDiv.textContent = preview;
                    lastMsgDiv.style.display = 'block';
                } else {
                    lastMsgDiv.style.display = 'none';
                }
            }
        });
    });
}

function filterUsers() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const userItems = document.querySelectorAll('.user-item');

    userItems.forEach(item => {
        const name = item.querySelector('.name').textContent.toLowerCase();
        item.style.display = name.includes(searchTerm) ? 'flex' : 'none';
    });
}

function selectUser(user) {
    selectedUser = user;

    document.querySelectorAll('.user-item').forEach(item => {
        item.classList.remove('active');
    });
    document.querySelector(`[data-user-id="${user.id}"]`)?.classList.add('active');

    const contactAvatar = document.getElementById('contactAvatar');
    if (user.avatar) {
        contactAvatar.innerHTML = `<img src="${user.avatar}" alt="">`;
    } else {
        contactAvatar.textContent = user.nickname ? user.nickname[0].toUpperCase() : '?';
    }
    document.getElementById('contactName').textContent = user.nickname;
    document.getElementById('contactStatus').textContent = '好友';
    document.getElementById('contactStatus').className = 'status online';

    const messageInput = document.getElementById('messageInput');
    const sendBtn = document.getElementById('sendBtn');
    messageInput.disabled = false;
    sendBtn.disabled = false;

    const messagesDiv = document.getElementById('messages');
    messagesDiv.innerHTML = '';

    loadMessages(user.id);
}

function loadMessages(receiverId) {
    fetch(`/api/messages/${receiverId}`)
        .then(response => response.json())
        .then(messages => {
            const messagesDiv = document.getElementById('messages');
            messagesDiv.innerHTML = '';

            messages.forEach(message => {
                displayMessage(message);
            });
            scrollToBottom();
        });
}

function displayMessage(message) {
    console.log('Displaying message:', message);
    const messagesDiv = document.getElementById('messages');
    const isSent = message.sender_id === getCurrentUserId();

    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isSent ? 'sent' : 'received'}`;

    const timestamp = new Date(message.timestamp);
    const timeStr = `${timestamp.getHours().toString().padStart(2, '0')}:${timestamp.getMinutes().toString().padStart(2, '0')}`;

    let mediaContent = '';
    if (message.file_url) {
        if (message.file_type === 'image') {
            mediaContent = `<a href="${message.file_url}" target="_blank"><img src="${message.file_url}" alt="图片" class="message-media message-image"></a>`;
        } else if (message.file_type === 'video') {
            mediaContent = `<video src="${message.file_url}" controls class="message-media message-video"></video>`;
        }
    }

    const textContent = message.content ? `<div class="message-text">${escapeHtml(message.content)}</div>` : '';

    const senderAvatar = message.sender_avatar;
    const senderNickname = message.sender_nickname || '未知用户';
    const avatarHtml = senderAvatar 
        ? `<div class="msg-avatar"><img src="${senderAvatar}" alt="${senderNickname}"></div>`
        : `<div class="msg-avatar">${senderNickname[0].toUpperCase()}</div>`;

    messageDiv.innerHTML = `
        ${avatarHtml}
        <div class="content">
            ${!isSent ? `<div class="sender-name">${senderNickname}</div>` : ''}
            ${mediaContent}
            ${textContent}
            <div class="time">${timeStr}</div>
        </div>
    `;

    messagesDiv.appendChild(messageDiv);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function sendMessage() {
    const messageInput = document.getElementById('messageInput');
    const content = messageInput.value.trim();

    if (!content || !selectedUser) return;

    const currentNickname = document.getElementById('currentNickname').textContent;
    socket.emit('send_message', {
        receiver_id: selectedUser.id,
        content: content,
        file_type: null,
        file_url: null,
        sender_nickname: currentNickname,
        sender_avatar: currentUserAvatar
    });

    messageInput.value = '';
    
    setTimeout(() => {
        if (selectedUser) {
            loadMessages(selectedUser.id);
            scrollToBottom();
        }
    }, 100);
}

function handleFileSelect(e) {
    const file = e.target.files[0];
    if (!file || !selectedUser) return;

    const formData = new FormData();
    formData.append('file', file);

    const uploadBtn = document.querySelector('.file-upload-btn');
    uploadBtn.classList.add('uploading');
    uploadBtn.innerHTML = '<span class="upload-spinner"></span>';

    fetch('/api/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        uploadBtn.classList.remove('uploading');
        uploadBtn.innerHTML = `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"></path>
        </svg>`;

        if (data.url) {
            const currentNickname = document.getElementById('currentNickname').textContent;
            socket.emit('send_message', {
                receiver_id: selectedUser.id,
                content: '',
                file_type: data.type,
                file_url: data.url,
                sender_nickname: currentNickname,
                sender_avatar: currentUserAvatar
            });
            
            setTimeout(() => {
                if (selectedUser) {
                    loadMessages(selectedUser.id);
                    scrollToBottom();
                }
            }, 100);
        }
    })
    .catch(error => {
        uploadBtn.classList.remove('uploading');
        uploadBtn.innerHTML = `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"></path>
        </svg>`;
        console.error('Upload error:', error);
    });

    e.target.value = '';
}

function scrollToBottom() {
    const messagesDiv = document.getElementById('messages');
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function initEmojiPanel() {
    const emojiTabs = document.querySelectorAll('.emoji-tab');
    emojiTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            emojiTabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            renderEmojiList(tab.dataset.category);
        });
    });
    
    renderEmojiList('smile');
}

function renderEmojiList(category) {
    const emojiList = document.getElementById('emojiList');
    emojiList.innerHTML = '';
    
    const emojis = emojiData[category] || [];
    emojis.forEach(emoji => {
        const emojiItem = document.createElement('div');
        emojiItem.className = 'emoji-item';
        emojiItem.textContent = emoji;
        emojiItem.addEventListener('click', () => {
            insertEmoji(emoji);
        });
        emojiList.appendChild(emojiItem);
    });
}

function toggleEmojiPanel() {
    const emojiPanel = document.getElementById('emojiPanel');
    emojiPanel.style.display = emojiPanel.style.display === 'none' ? 'block' : 'none';
}

function insertEmoji(emoji) {
    const messageInput = document.getElementById('messageInput');
    const startPos = messageInput.selectionStart;
    const endPos = messageInput.selectionEnd;
    const text = messageInput.value;
    
    messageInput.value = text.substring(0, startPos) + emoji + text.substring(endPos);
    messageInput.selectionStart = messageInput.selectionEnd = startPos + emoji.length;
    messageInput.focus();
}