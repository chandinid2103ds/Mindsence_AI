/* ============================================================
   MindSense AI Assistant
   Front-end for the existing Python/Flask chatbot model.

   Expected backend:
       POST http://127.0.0.1:5000/chat

   Request:
       { "message": "...", "condition": "stress" }

   Response follows the structure used by the supplied Python model:
       {
         success: true,
         type: "stress",
         message: "...",
         condition_context: "...",
         solution: "..."
       }

   If your Flask route uses another URL, change API_URL below.
   ============================================================ */

const API_URL = "http://127.0.0.1:5000/chat";

const pageLoader = document.getElementById("pageLoader");
const conversation = document.getElementById("conversation");
const welcomeBlock = document.getElementById("welcomeBlock");
const messages = document.getElementById("messages");
const chatForm = document.getElementById("chatForm");
const messageInput = document.getElementById("messageInput");
const sendBtn = document.getElementById("sendBtn");
const characterCount = document.getElementById("characterCount");
const typingIndicator = document.getElementById("typingIndicator");
const newChatBtn = document.getElementById("newChatBtn");

const safetyBtn = document.getElementById("safetyBtn");
const safetyModal = document.getElementById("safetyModal");
const closeSafety = document.getElementById("closeSafety");

let isSending = false;

/* ---------- Initial setup ---------- */

window.addEventListener("load", () => {
    setTimeout(() => pageLoader.classList.add("hidden"), 450);
});

messageInput.focus();

/* ---------- Helpers ---------- */

function escapeHTML(value) {
    return String(value ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function formatText(value) {
    return escapeHTML(value).replace(/\n/g, "<br>");
}

function getCondition() {
    const keys = [
        "condition",
        "userCondition",
        "wellnessCondition",
        "mindsenseCondition"
    ];

    for (const key of keys) {
        const value = localStorage.getItem(key);
        if (value) return value;
    }

    return null;
}

function currentTime() {
    return new Intl.DateTimeFormat([], {
        hour: "2-digit",
        minute: "2-digit"
    }).format(new Date());
}

function scrollToLatest() {
    requestAnimationFrame(() => {
        conversation.scrollTo({
            top: conversation.scrollHeight,
            behavior: "smooth"
        });
    });
}

function setSending(state) {
    isSending = state;
    sendBtn.disabled = state;
    messageInput.disabled = state;
    typingIndicator.classList.toggle("visible", state);
}

/* ---------- Message rendering ---------- */

function addMessage(role, text, options = {}) {
    const item = document.createElement("article");
    item.className = `message ${role}`;

    if (options.safety) {
        item.classList.add("safety-message");
    }

    const avatar = role === "assistant" ? "M" : "YOU";

    let extra = "";

    if (options.conditionContext) {
        extra += `
            <div class="response-context">
                ${formatText(options.conditionContext)}
            </div>
        `;
    }

    if (options.solution) {
        extra += `
            <div class="response-suggestion">
                ${formatText(options.solution)}
            </div>
        `;
    }

    item.innerHTML = `
        <div class="message-avatar">${avatar}</div>
        <div class="message-content">
            <div class="message-bubble">${formatText(text)}</div>
            ${extra}
            <div class="message-meta">${role === "assistant" ? "MINDSENSE AI" : "YOU"} · ${currentTime()}</div>
        </div>
    `;

    messages.appendChild(item);
    welcomeBlock.style.display = "none";
    scrollToLatest();

    return item;
}

/* ---------- Backend ---------- */

async function requestAssistant(message) {
    const condition = getCondition();

    const response = await fetch(API_URL, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            message,
            condition
        })
    });

    if (!response.ok) {
        throw new Error(`Server returned ${response.status}`);
    }

    return await response.json();
}

/*
   Demo fallback.

   This keeps the interface usable if the Flask server is not running.
   It does NOT replace your Python model. Once the backend is available,
   the real response is used automatically.
*/
function demoResponse(message) {
    const text = message.toLowerCase();

    if (
        text.includes("suicide") ||
        text.includes("kill myself") ||
        text.includes("end my life") ||
        text.includes("want to die") ||
        text.includes("self harm") ||
        text.includes("hurt myself")
    ) {
        return {
            success: true,
            type: "safety",
            message: "I'm really sorry that you're going through this. You deserve support, and you don't have to handle this alone.",
            solution: "Please contact a trusted person or a qualified mental health professional right now. If you are in immediate danger, contact your local emergency service or go to the nearest emergency department."
        };
    }

    if (text.includes("stress") || text.includes("overwhelmed") || text.includes("pressure")) {
        return {
            success: true,
            type: "stress",
            message: "It sounds like you may be feeling under a lot of pressure. You do not have to solve everything at once.",
            solution: "Take 5 slow and deep breaths, then choose one small task to focus on."
        };
    }

    if (text.includes("anxious") || text.includes("anxiety") || text.includes("worried") || text.includes("panic")) {
        return {
            success: true,
            type: "anxiety",
            message: "It sounds like you may be experiencing some anxiety. You are not alone in feeling this way.",
            solution: "Try breathing in for 4 seconds and out for 6 seconds, then focus on one thing you can control right now."
        };
    }

    if (text.includes("sad") || text.includes("lonely") || text.includes("empty") || text.includes("upset")) {
        return {
            success: true,
            type: "sadness",
            message: "I'm sorry that you are going through a difficult moment. Your feelings are important.",
            solution: "Consider talking with a trusted friend or family member and give yourself permission to rest."
        };
    }

    if (text.includes("sleep") || text.includes("tired") || text.includes("insomnia")) {
        return {
            success: true,
            type: "sleep",
            message: "It sounds like your sleep may be affecting how you are feeling.",
            solution: "Try keeping a consistent bedtime and reducing screen use before sleeping."
        };
    }

    if (text.includes("motivation") || text.includes("lazy") || text.includes("focus")) {
        return {
            success: true,
            type: "motivation",
            message: "You do not need to accomplish everything at once. Small progress still counts.",
            solution: "Choose one small task and work on it for just 10 minutes."
        };
    }

    return {
        success: true,
        type: "general",
        message: "Thank you for sharing that with me. I'm here to listen and help you think through it.",
        solution: "Try describing what has been bothering you most today, and we can take it one step at a time."
    };
}

async function sendMessage(text) {
    const clean = text.trim();

    if (!clean || isSending) return;

    addMessage("user", clean);

    messageInput.value = "";
    updateCharacterCount();
    autoResize();

    setSending(true);

    try {
        let data;

        try {
            data = await requestAssistant(clean);
        } catch (backendError) {
            console.warn("MindSense backend unavailable. Using interface fallback.", backendError);
            await new Promise(resolve => setTimeout(resolve, 650));
            data = demoResponse(clean);
        }

        if (!data || data.success === false) {
            throw new Error(data?.message || "Unable to generate a response.");
        }

        addMessage(
            "assistant",
            data.message || "Thank you for sharing that with me.",
            {
                conditionContext: data.condition_context,
                solution: data.solution,
                safety: data.type === "safety"
            }
        );

    } catch (error) {
        console.error(error);

        addMessage(
            "assistant",
            "I’m unable to complete that response right now. Please try again in a moment."
        );
    } finally {
        setSending(false);
        messageInput.focus();
    }
}

/* ---------- Composer ---------- */

function autoResize() {
    messageInput.style.height = "auto";
    messageInput.style.height = Math.min(messageInput.scrollHeight, 125) + "px";
}

function updateCharacterCount() {
    characterCount.textContent = `${messageInput.value.length} / 1200`;
}

messageInput.addEventListener("input", () => {
    updateCharacterCount();
    autoResize();
});

messageInput.addEventListener("keydown", event => {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        chatForm.requestSubmit();
    }
});

chatForm.addEventListener("submit", event => {
    event.preventDefault();
    sendMessage(messageInput.value);
});

/* ---------- Quick prompts ---------- */

document.querySelectorAll(".prompt-card").forEach(button => {
    button.addEventListener("click", () => {
        sendMessage(button.dataset.prompt);
    });
});

/* ---------- New conversation ---------- */

newChatBtn.addEventListener("click", () => {
    messages.innerHTML = "";
    welcomeBlock.style.display = "";
    messageInput.value = "";
    updateCharacterCount();
    autoResize();
    messageInput.focus();
});

/* ---------- Safety modal ---------- */

function openSafetyModal() {
    safetyModal.classList.add("open");
    safetyModal.setAttribute("aria-hidden", "false");
}

function closeSafetyModal() {
    safetyModal.classList.remove("open");
    safetyModal.setAttribute("aria-hidden", "true");
}

safetyBtn.addEventListener("click", openSafetyModal);
closeSafety.addEventListener("click", closeSafetyModal);

document.querySelectorAll("[data-close-modal]").forEach(el => {
    el.addEventListener("click", closeSafetyModal);
});

document.addEventListener("keydown", event => {
    if (event.key === "Escape") {
        closeSafetyModal();
    }
});

/* ---------- Start clean ---------- */

updateCharacterCount();
autoResize();
