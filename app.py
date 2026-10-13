import os
import requests
from bs4 import BeautifulSoup
import urllib.parse
from flask import Flask, render_template_string, request, jsonify
from groq import Groq

app = Flask(__name__)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NerVous - AI</title>
    <style>
        body { 
          font-family: sans-serif; 
          background: rgb(10, 5, 9); 
          box-shadow: 0px 5px 7px rgba(6, 2, 65, 0.3);
          color: #e0e0e0; 
          margin: 0; 
          padding: 15px; 
          display: flex; 
          flex-direction: column; 
          height: 92vh; 
        }
        #swbs {
          background-color: rgba(150, 150, 150, 0.2);
          margin: 0 auto 12px auto;
          text-align: center;
          width: 50%;
          box-shadow: 0px 0px 20px rgb(100, 0, 100);
          padding: 8px;
          overflow-y: auto;
          border: 2px solid black;
          border-radius: 10px;  
          transition: box-shadow 0.5s ease-in;
        }
        #swbs.active { 
          box-shadow: 0px 0px 25px rgba(246, 169, 255, 0.9); 
        }
          #swb {
          color: yellow;
          border: 2px solid gray;
          padding: 4px 12px;
          font-size: 12px;
          position: absolute;
          top: 20px;
          right: 20px; /* Đưa ra góc phải cho gọn, không bị đè lên tiêu đề */
          text-shadow: 0px 0px 5px rgb(200, 200, 200);
          font-family: system-ui, sans-serif;
          background-color: rgba(255, 255, 255, 0.87);
          cursor: pointer;
          border-radius: 8px;
          transition: background-color 0.5s ease-in, all 0.5s ease-in-out;
        }
        #swb.active { 
          background-color: rgba(97, 10, 100, 0.9); 
        }
        #chat-box { 
          flex: 1; 
          border: 1px solid #333;
          box-shadow: 0px 0px 20px rgba(253, 149, 235, 0.3);
          padding: 12px; 
          overflow-x:auto;
          border-radius: 8px; 
          background: rgba(100, 8, 9,0.05); 
          margin-bottom: 12px; 
          transition: box-shadow 0.5s ease-in;
        }
        #chat-box.active {
          box-shadow: 0px 0px 25px rgba(200, 100, 200, 0.5);
        }

        .message { 
          margin-bottom: 12px; 
          line-height: 1.4; 
        }
        .msg-bubble {
          background-color: rgba(150, 150, 150, 0.15);
          padding: 8px 12px;
          overflow-y: auto;
          border-radius: 8px;
          border: 1px solid #444;
        }

        .user { 
          color: #64B5F6; 
          font-weight: bold; 
        }
        .ai { 
          color: #81C784; 
        }

        .input-group { 
          display: flex; 
          gap: 8px; 
        }
        input { 
          flex: 1; 
          padding: 7px; 
          border-radius: 5px; 
          border: 1px solid #444; 
          background: #2c2c2c; 
          color: white; 
          font-size: 16px; 
        }
        button.send-btn { 
          padding: 10px 10px; 
          background: #4CAF50; 
          color: white; 
          border: none; 
          border-radius: 5px; 
          font-size: 16px; 
          cursor: pointer; 
        }
    </style>
</head>
<body>
    <button id="swb">
        <span id="icon">🌐</span>
    </button>

    <h2 id="swbs">NerVous AI</h2>
    <div id="chat-box">
        <div class="message">
            <div class="msg-bubble"><span class="ai">NerVous:</span> Chào bạn! Tôi là NerVous, hệ thống RAG Cloud đã sẵn sàng phục vụ 24/7.</div>
        </div>
    </div>
    <div class="input-group">
        <input type="text" id="query" placeholder="Nhập câu hỏi..." onkeypress="if(event.key === 'Enter') sendQuery()">
        <button class="send-btn" onclick="sendQuery()">Gửi</button>
    </div>
</body>

    <script>
       let a = 0; 
       const swbButton = document.getElementById("swb");
       const swbsElement = document.getElementById("swbs");
       const chatBoxElement = document.getElementById("chat-box");
       const iconElement = document.getElementById("icon");

       swbButton.addEventListener("click", function() {
            a += 1;
            console.log("Số lần bấm hiện tại:", a);
            swbButton.classList.toggle("active");
            swbsElement.classList.toggle("active");
            chatBoxElement.classList.toggle("active");
            
            if (a % 2 !== 0) {
                iconElement.innerHTML = "🌘";
            } else {
                iconElement.innerHTML = "🌐";
            }
        });

        async function sendQuery() {
            const inputField = document.getElementById('query');
            const chatBox = document.getElementById('chat-box');
            const query = inputField.value.trim();
            if (!query) return;
            chatBox.innerHTML += `<div class="message"><div class="msg-bubble"><span class="user">Bạn:</span> ${query}</div></div>`;
            inputField.value = '';
            chatBox.scrollTop = chatBox.scrollHeight;

            const loadingId = 'loading-' + Date.now();
            chatBox.innerHTML += `<div class="message" id="${loadingId}"><div class="msg-bubble"><span class="ai">NerVous:</span> 🔍 Đang tìm kiếm và xử lý...</div></div>`;
            chatBox.scrollTop = chatBox.scrollHeight;

            try {
                const response = await fetch('/ask', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ query: query })
                });
                const data = await response.json();
                document.getElementById(loadingId).innerHTML = `<div class="msg-bubble"><span class="ai">NerVous:</span> ${data.result.replace(/\\n/g, '<br>')}</div>`;
            } catch (error) {
                document.getElementById(loadingId).innerHTML = `<div class="msg-bubble"><span class="ai">NerVous:</span> Lỗi kết nối.</div>`;
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
        user_content = f"Dựa vào thông tin chuẩn sau đây:\n\"{ngu_canh}\"\n\nHãy trả lời câu hỏi: {cau_hoi}. Trả lời ngắn gọn, chính xác bằng tiếng Việt. Tuyệt đối không dùng LaTeX."
    else:
        user_content = f"Trả lời ngắn gọn, chính xác bằng tiếng Việt: {cau_hoi}"

    try:
        completion = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {
                    "role": "system", 
                    "content": "Bạn tên là NerVous, một trợ lý trí tuệ nhân tạo thân thiện, vui vẻ, thông minh và tràn đầy năng lượng. Hãy trả lời các câu hỏi bằng tiếng Việt một cách nhiệt tình, lịch sự, có cảm xúc tích cực và tuyệt đối không bao giờ được xưng là ChatGPT."
                },
                {"role": "user", "content": user_content}
            ],
            temperature=0.7,
        )
        phan_hoi = completion.choices[0].message.content
    except Exception as e:
        phan_hoi = f"Lỗi gọi API: {e}"

    return jsonify({'result': phan_hoi})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
