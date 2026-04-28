console.log("UI Loaded");

let lastIndexedUrl = null;
let lastIndexedContentHash = null;

let isLoading = false;
const userId = localStorage.getItem("user_id") || generateUserId();

function generateUserId() {
    const id = "user_" + Math.random().toString(36).substring(2, 10);
    localStorage.setItem("user_id", id);
    return id;
}

function hashText(text) {
    let hash = 0;
    for (let i = 0; i < text.length; i++) {
        hash = ((hash << 5) - hash) + text.charCodeAt(i);
        hash |= 0;
    }
    return hash.toString();
}

async function safeFetch(url, options = {}) {
    const res = await fetch(url, options);
    if (!res.ok) throw new Error("Request failed");
    return await res.json();
}

function addUserBubble(text) {
    const chat = document.getElementById("chat");
    chat.innerHTML += `<div class="bubble user">${text}</div>`;
    chat.scrollTop = chat.scrollHeight;
}

function addBotBubble(data) {
    const chat = document.getElementById("chat");

    let html = `<div class="bubble">`;

    if (data.answer) {
        html += `<div>${data.answer}</div>`;
    }

    html += `</div>`;

    chat.innerHTML += html;
    chat.scrollTop = chat.scrollHeight;
}

function showLoader() {
    const chat = document.getElementById("chat");
    chat.innerHTML += `<div class="loader">Thinking...</div>`;
    chat.scrollTop = chat.scrollHeight;
}

function removeLoader() {
    document.querySelectorAll(".loader").forEach(e => e.remove());
}

document.getElementById("askBtn").addEventListener("click", sendQuery);

async function sendQuery() {
    if (isLoading) return;

    const queryBox = document.getElementById("query");
    const query = queryBox.value.trim();

    if (!query) return;

    isLoading = true;
    queryBox.value = "";

    addUserBubble(query);
    showLoader();

    try {
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

        const [{ result }] = await chrome.scripting.executeScript({
            target: { tabId: tab.id },
            func: () => {

                function cleanText(text) {
                    const junkPatterns = [
                        "Jump to content",
                        "Main menu",
                        "Search",
                        "Donate",
                        "Log in",
                        "Create account",
                        "Subscribe",
                        "Privacy Policy",
                        "Terms",
                        "Cookies"
                    ];

                    junkPatterns.forEach(junk => {
                        text = text.replaceAll(junk, "");
                    });

                    return text
                        .split("\n")
                        .map(line => line.trim())
                        .filter(line => line.length > 40)
                        .join(" ")
                        .replace(/\s+/g, " ")
                        .trim();
                }

                function extractContent() {
                    const selectors = [
                        "article",
                        "main",
                        "[role='main']",
                        ".post-content",
                        ".article-content",
                        ".entry-content",
                        ".mw-parser-output"
                    ];

                    for (let sel of selectors) {
                        const el = document.querySelector(sel);
                        if (el && el.innerText.length > 500) {
                            return cleanText(el.innerText);
                        }
                    }

                    // fallback (structured)
                    let text = Array.from(document.querySelectorAll("p, h1, h2, h3"))
                        .map(el => el.innerText)
                        .join(" ");

                    return cleanText(text);
                }

                return extractContent(); 
            }
        });

        console.log("TEXT LENGTH:", result.length);

        // 🚨 HARD FILTER
        if (!result || result.length < 300 || result.split(" ").length < 80) {
            removeLoader();
            addBotBubble({ answer: "Page content not readable. Try another page." });
            return;
        }

        const currentUrl = tab.url;
        const contentHash = hashText(result);

        const trimmed = result.slice(0, 8000);

        if (lastIndexedUrl !== currentUrl || lastIndexedContentHash !== contentHash) {

            console.log("📥 Ingesting CLEAN content...");

            await safeFetch("http://127.0.0.1:8000/ingest", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    text: trimmed,
                    user_id: userId
                })
            });

            lastIndexedUrl = currentUrl;
            lastIndexedContentHash = contentHash;

        } else {
            console.log("⚡ Using cached content");
        }

        const data = await safeFetch("http://127.0.0.1:8000/query", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                query,
                user_id: userId
            })
        });

        removeLoader();
        addBotBubble(data);

    } catch (err) {
        removeLoader();
        addBotBubble({ answer: "Error: " + err.message });
    } finally {
        isLoading = false;
    }
}