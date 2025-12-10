// Run this when the page loads
document.addEventListener("DOMContentLoaded", function() {
    loadChatHistory();
});

function handleEnter(e) {
    if (e.key === 'Enter') sendMessage();
}

async function loadChatHistory() {
    const chatBox = document.getElementById("chat-box");
    
    try {
        const response = await fetch("/api/history");
        const history = await response.json();
        
        // Clear default welcome message if we have history
        if (history.length > 0) {
            chatBox.innerHTML = ""; 
        }

        history.forEach(msg => {
            const cssClass = (msg.role === 'user') ? 'user-message' : 'bot-message';
            // Convert newlines to line breaks for bot messages
            let content = msg.content.replace(/\n/g, '<br>');
            chatBox.innerHTML += `<div class="message ${cssClass}">${content}</div>`;
        });
        
        // Scroll to bottom
        chatBox.scrollTop = chatBox.scrollHeight;
    } catch (error) {
        console.error("Could not load history:", error);
    }
}

async function sendMessage() {
    const input = document.getElementById("user-input");
    const chatBox = document.getElementById("chat-box");
    const text = input.value.trim();
    
    if (!text) return;

    // 1. Show User Message
    chatBox.innerHTML += `<div class="message user-message">${text}</div>`;
    input.value = "";
    chatBox.scrollTop = chatBox.scrollHeight;

    // 2. Show "Thinking..."
    const loadingDiv = document.createElement("div");
    loadingDiv.className = "message bot-message";
    loadingDiv.innerText = "Thinking...";
    chatBox.appendChild(loadingDiv);
    chatBox.scrollTop = chatBox.scrollHeight;

    try {
        // 3. Send to Backend
        const response = await fetch("/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: text })
        });
        const data = await response.json();
        
        // 4. Update with Real Response
        chatBox.removeChild(loadingDiv);
        
        if (data.error) {
            chatBox.innerHTML += `<div class="message bot-message" style="color:red">Error: ${data.error}</div>`;
        } else {
            let cleanResponse = data.response.replace(/\n/g, '<br>');
            chatBox.innerHTML += `<div class="message bot-message">${cleanResponse}</div>`;
        }
    } catch (error) {
        chatBox.removeChild(loadingDiv);
        chatBox.innerHTML += `<div class="message bot-message" style="color:red">Connection Error.</div>`;
    }
    chatBox.scrollTop = chatBox.scrollHeight;
}