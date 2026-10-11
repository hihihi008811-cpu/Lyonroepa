import os
import requests
from bs4 import BeautifulSoup
import urllib.parse
from flask import Flask, render_template_string, request, jsonify
from groq import Groq

app = Flask(__name__)

# Điền Groq API Key của bạn
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
