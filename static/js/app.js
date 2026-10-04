// HealthForge AI Interactive App Engine

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('hf_theme', newTheme);
}

function appendSymptom(text) {
    const textarea = document.getElementById("symptoms");
    if (!textarea) return;
    const currentVal = textarea.value.trim();
    if (currentVal.length === 0) {
        textarea.value = text;
    } else if (!currentVal.toLowerCase().includes(text.toLowerCase())) {
        textarea.value = currentVal + ", " + text;
    }
    textarea.focus();
}

function updateSeverityLabel(val) {
    const badge = document.getElementById("severity-badge");
    const numSpan = document.getElementById("severity-num");
    if (numSpan) numSpan.textContent = val;
    if (!badge) return;

    badge.className = "severity-indicator-badge";
    if (val <= 3) {
        badge.textContent = "Mild Care";
        badge.classList.add("sev-low");
    } else if (val <= 6) {
        badge.textContent = "Moderate Care";
        badge.classList.add("sev-med");
    } else if (val <= 8) {
        badge.textContent = "High Priority";
        badge.classList.add("sev-high");
    } else {
        badge.textContent = "Critical / Urgent";
        badge.classList.add("sev-urgent");
    }
}

function speakText(text) {
    if (!('speechSynthesis' in window)) {
        alert("Speech synthesis is not supported in your browser.");
        return;
    }
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    window.speechSynthesis.speak(utterance);
}

function fillDemoLogin(email, password, role) {
    const emailInput = document.getElementById("email");
    const passwordInput = document.getElementById("password");
    const roleSelect = document.getElementById("role");

    if (emailInput) emailInput.value = email;
    if (passwordInput) passwordInput.value = password;
    if (roleSelect) roleSelect.value = role;

    // Highlight form submit button
    const submitBtn = document.querySelector(".login-submit");
    if (submitBtn) {
        submitBtn.classList.add("pulse-glow");
        setTimeout(() => submitBtn.classList.remove("pulse-glow"), 1200);
    }
}

document.addEventListener("DOMContentLoaded", () => {
    // Auto-dismiss flashes after delay
    setTimeout(() => {
        document.querySelectorAll(".flash").forEach((flash) => {
            flash.style.opacity = "0";
            flash.style.transform = "translateY(-6px)";
            setTimeout(() => flash.remove(), 250);
        });
    }, 5500);

    // Live Clock initialization for dashboards
    const clockElement = document.getElementById("live-header-clock");
    if (clockElement) {
        const updateClock = () => {
            const now = new Date();
            clockElement.textContent = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }) + ' · ' + now.toLocaleDateString([], { weekday: 'short', month: 'short', day: 'numeric' });
        };
        updateClock();
        setInterval(updateClock, 1000);
    }

    // Auto focus symptom form textarea if present
    const symptomTextarea = document.getElementById("symptoms");
    if (symptomTextarea && symptomTextarea.dataset.autofocus === "true") {
        symptomTextarea.focus();
    }
});
