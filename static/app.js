// 全局状态
let currentSessionId = '';
let isProcessing = false;

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    currentSessionId = generateSessionId();
    
    // 绑定事件
    document.getElementById('sendButton').addEventListener('click', sendMessage);
    document.getElementById('userInput').addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    // 配置marked
    marked.setOptions({
        breaks: true,
        gfm: true,
        highlight: function(code, lang) {
            if (lang && hljs.getLanguage(lang)) {
                return hljs.highlight(code, { language: lang }).value;
            }
            return hljs.highlightAuto(code).value;
        }
    });
});

// 生成会话ID
function generateSessionId() {
    return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

// 设置输入框内容
function setInput(text) {
    document.getElementById('userInput').value = text;
    document.getElementById('userInput').focus();
}

// 发送消息
async function sendMessage() {
    if (isProcessing) return;
    
    const input = document.getElementById('userInput');
    const message = input.value.trim();
    
    if (!message) return;
    
    // 显示用户消息
    addMessage(message, 'user');
    
    // 清空输入框
    input.value = '';
    
    // 更新状态
    setProcessingState(true);
    updateStatus('正在处理...', 'busy');
    
    try {
        // 调用后端API
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                session_id: currentSessionId
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // 显示AI响应
        if (data.response) {
            addMessage(data.response, 'assistant', data.current_agent);
        }
        
        // 更新Agent信息
        if (data.current_agent) {
            updateAgentInfo(data.current_agent);
        }
        
        // 更新状态
        if (data.status === 'completed') {
            updateStatus('完成', 'success');
        } else if (data.status === 'booking') {
            updateStatus('正在预订...', 'busy');
        } else if (data.status === 'planning') {
            updateStatus('正在规划...', 'busy');
        } else {
            updateStatus('就绪', 'success');
        }
        
    } catch (error) {
        console.error('Error:', error);
        addMessage(`❌ 发生错误：${error.message}`, 'assistant');
        updateStatus('错误', 'error');
    } finally {
        setProcessingState(false);
    }
}

// 添加消息到聊天界面
function addMessage(content, type, agentName = '') {
    const chatContainer = document.getElementById('chatContainer');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}-message`;
    
    // 转换Markdown
    const htmlContent = marked.parse(content);
    
    let agentLabel = '';
    if (agentName) {
        agentLabel = `<div class="agent-label">${getAgentDisplayName(agentName)}</div>`;
    }
    
    messageDiv.innerHTML = `
        ${agentLabel}
        <div class="message-content">${htmlContent}</div>
    `;
    
    chatContainer.appendChild(messageDiv);
    
    // 滚动到底部
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// 获取Agent显示名称
function getAgentDisplayName(agentName) {
    const agentNames = {
        'itinerary_agent': '🗺️ 行程Agent',
        'booking_agent': '💳 预订Agent',
        'coordinator': '🎯 协调器',
        'user': '👤 用户'
    };
    return agentNames[agentName] || agentName;
}

// 设置处理状态
function setProcessingState(processing) {
    isProcessing = processing;
    const button = document.getElementById('sendButton');
    const spinner = button.querySelector('.loading-spinner');
    const buttonText = button.querySelector('.button-text');
    
    if (processing) {
        button.disabled = true;
        spinner.classList.remove('hidden');
        buttonText.textContent = '发送中';
    } else {
        button.disabled = false;
        spinner.classList.add('hidden');
        buttonText.textContent = '发送';
    }
}

// 更新状态指示器
function updateStatus(text, type) {
    const statusText = document.getElementById('statusText');
    const statusDot = document.getElementById('statusDot');
    
    statusText.textContent = text;
    
    statusDot.classList.remove('busy', 'error');
    if (type === 'busy') {
        statusDot.classList.add('busy');
    } else if (type === 'error') {
        statusDot.classList.add('error');
    }
}

// 更新Agent信息
function updateAgentInfo(agentName) {
    const badge = document.getElementById('currentAgent');
    badge.textContent = getAgentDisplayName(agentName);
}

// 重置会话
function resetSession() {
    currentSessionId = generateSessionId();
    const chatContainer = document.getElementById('chatContainer');
    
    // 保留系统消息，清除其他消息
    const messages = chatContainer.querySelectorAll('.message');
    messages.forEach((msg, index) => {
        if (index > 0) { // 保留第一条系统消息
            msg.remove();
        }
    });
    
    updateStatus('就绪', 'success');
    updateAgentInfo('等待输入');
}

// 显示错误消息
function showError(message) {
    const chatContainer = document.getElementById('chatContainer');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message assistant-message';
    messageDiv.innerHTML = `
        <div class="message-content" style="color: var(--error-color);">
            ❌ ${message}
        </div>
    `;
    chatContainer.appendChild(messageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// 导出函数供HTML调用
window.setInput = setInput;
window.resetSession = resetSession;
