"use strict";
const messagesEl = document.querySelector("#messages");
const inputEl = document.querySelector("#msgInput");
const sendBtn = document.querySelector("#sendBtn");
const conversationHistory = [];
function requireElements() {
    if (!messagesEl || !inputEl || !sendBtn) {
        throw new Error("The chat interface is missing a required element.");
    }
    return { messages: messagesEl, input: inputEl, button: sendBtn };
}
function autoResize() {
    if (!inputEl)
        return;
    inputEl.style.height = "auto";
    inputEl.style.height = `${Math.min(inputEl.scrollHeight, 120)}px`;
}
function appendMessage(role, text) {
    const { messages } = requireElements();
    const row = document.createElement("div");
    row.className = `msg ${role}`;
    const bubble = document.createElement("div");
    bubble.className = "bubble";
    bubble.textContent = text;
    row.append(bubble);
    messages.append(row);
    messages.scrollTop = messages.scrollHeight;
}
function setBusy(busy) {
    if (!sendBtn || !inputEl)
        return;
    sendBtn.disabled = busy;
    inputEl.disabled = busy;
    if (busy) {
        const row = document.createElement("div");
        row.className = "msg agent typing";
        row.id = "typing";
        const bubble = document.createElement("div");
        bubble.className = "bubble";
        for (let i = 0; i < 3; i += 1) {
            const dot = document.createElement("div");
            dot.className = "dot";
            bubble.append(dot);
        }
        row.append(bubble);
        messagesEl?.append(row);
        if (messagesEl)
            messagesEl.scrollTop = messagesEl.scrollHeight;
    }
    else {
        document.querySelector("#typing")?.remove();
        inputEl.focus();
    }
}
async function sendMessage() {
    const { input, button } = requireElements();
    const text = input.value.trim();
    if (!text || button.disabled)
        return;
    input.value = "";
    autoResize();
    appendMessage("user", text);
    conversationHistory.push({ role: "user", content: text });
    setBusy(true);
    try {
        const response = await fetch("/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ messages: conversationHistory.slice(-40) }),
        });
        const data = await response.json();
        if (!response.ok)
            throw new Error(data.error ?? `Request failed (${response.status})`);
        const reply = data.reply ?? "No response returned.";
        appendMessage("agent", reply);
        conversationHistory.push({ role: "assistant", content: reply });
    }
    catch (error) {
        const message = error instanceof Error ? error.message : "The request failed. Try again.";
        appendMessage("agent", message);
    }
    finally {
        setBusy(false);
    }
}
sendBtn?.addEventListener("click", () => void sendMessage());
inputEl?.addEventListener("input", autoResize);
inputEl?.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        void sendMessage();
    }
});
const statusDot = document.querySelector("#statusDot");
void fetch("/api/status")
    .then((response) => response.json())
    .then((status) => {
    if (!statusDot)
        return;
    statusDot.title = status.modelLoaded
        ? `LM Studio connected · ${status.model}`
        : status.connected
            ? `LM Studio is online, but ${status.model} is not loaded`
            : "LM Studio is not reachable; check its server and model";
    statusDot.classList.toggle("connected", Boolean(status.modelLoaded));
    statusDot.classList.toggle("disconnected", !status.modelLoaded);
})
    .catch(() => {
    if (statusDot)
        statusDot.title = "Finagler server unavailable";
});
