import os
import requests
from bs4 import BeautifulSoup
import urllib.parse
from flask import Flask, render_template_string, request, jsonify
from groq import Groq

app = Flask(__name__)

# Điền Groq API Key của bạn vào đây (Hoặc đặt biến môi trường GROQ_API_KEY)
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "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")
client = Groq(api_key=GROQ_API_KEY)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Trợ Lý AI RAG Cloud 24/7</title>
    <style>
        body { font-family: sans-serif; background: #121212; color: #e0e0e0; margin: 0; padding: 15px; display: flex; flex-direction: column; height: 92vh; }
        h2 { text-align: center; color: #4CAF50; }
        #chat-box { flex: 1; overflow-y: auto; border: 1px solid #333; padding: 12px; border-radius: 8px; background: #1e1e1e; margin-bottom: 12px; }
        .message { margin-bottom: 12px; line-height: 1.4; }
        .user { color: #64B5F6; font-weight: bold; }
        .ai { color: #81C784; }
        .input-group { display: flex; gap: 8px; }
        input { flex: 1; padding: 10px; border-radius: 5px; border: 1px solid #444; background: #2c2c2c; color: white; font-size: 16px; }
        button { padding: 10px 18px; background: #4CAF50; color: white; border: none; border-radius: 5px; font-size: 16px; cursor: pointer; }
    </style>
</head>
<body>
    <h2>🤖 Trợ Lý RAG Cloud 24/7</h2>
    <div id="chat-box">
        <div class="message"><span class="ai">AI:</span> Chào bạn! Hệ thống RAG Cloud đã sẵn sàng phục vụ 24/7.</div>
    </div>
    <div class="input-group">
        <input type="text" id="query" placeholder="Nhập câu hỏi..." onkeypress="if(event.key === 'Enter') sendQuery()">
        <button onclick="sendQuery()">Gửi</button>
    </div>

    <script>
        async function sendQuery() {
            const inputField = document.getElementById('query');
            const chatBox = document.getElementById('chat-box');
            const query = inputField.value.trim();
            if (!query) return;

            chatBox.innerHTML += `<div class="message"><span class="user">Bạn:</span> ${query}</div>`;
            inputField.value = '';
            chatBox.scrollTop = chatBox.scrollHeight;

            const loadingId = 'loading-' + Date.now();
            chatBox.innerHTML += `<div class="message" id="${loadingId}"><span class="ai">AI:</span> 🔍 Đang tìm kiếm và xử lý...</div>`;
            chatBox.scrollTop = chatBox.scrollHeight;

            try {
                const response = await fetch('/ask', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ query: query })
                });
                const data = await response.json();
                document.getElementById(loadingId).innerHTML = `<span class="ai">AI:</span> ${data.result.replace(/\\n/g, '<br>')}`;
            } catch (error) {
                document.getElementById(loadingId).innerHTML = `<span class="ai">AI:</span> Lỗi kết nối.`;
            }
            chatBox.scrollTop = chatBox.scrollHeight;
        }
    </script>
</body>
</html>
"""

def tim_kiem_web(query):
    try:
        query_chuan = f"{query} site:vi.wikipedia.org OR site:en.wikipedia.org"
        encoded_query = urllib.parse.quote(query_chuan)
        url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.post(url, headers=headers, timeout=3)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            results = soup.find_all('a', class_='result__snippet')
            context = ""
            for r in results:
                context += r.get_text().strip() + " "
                if len(context) > 600:
                    break
            return context
    except:
        pass
    return ""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    cau_hoi = data.get('query', '')
    ngu_canh = tim_kiem_web(cau_hoi)
    
    if ngu_canh:
        prompt = f"Dựa vào thông tin chuẩn sau đây:\n\"{ngu_canh}\"\n\nHãy trả lời câu hỏi: {cau_hoi}. Trả lời ngắn gọn, chính xác bằng tiếng Việt. Tuyệt đối không dùng LaTeX."
    else:
        prompt = f"Trả lời ngắn gọn, chính xác bằng tiếng Việt: {cau_hoi}"

    try:
        # Gọi mô hình Qwen 2.5 72B hoặc Llama 3 siêu mạnh qua Groq Cloud
            completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",  # Đổi thành model này chạy cực nhanh và chuẩn
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        phan_hoi = completion.choices[0].message.content
    except Exception as e:
        phan_hoi = f"Lỗi gọi API: {e}"

    return jsonify({'result': phan_hoi})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
