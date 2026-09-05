const loginBtn = document.getElementById("loginBtn");

if (loginBtn) {
    loginBtn.addEventListener("click", loginUser);
}

async function loginUser() {
    const username = document.getElementById("loginUsername").value.trim();
    const password = document.getElementById("loginPassword").value;
    const message = document.getElementById("loginMessage");

    message.textContent = "";

    if (!username || !password) {
        message.textContent = "Please enter your User ID and password.";
        message.style.color = "#c25555";
        return;
    }

    loginBtn.disabled = true;
    loginBtn.textContent = "Logging in...";

    try {
        const response = await fetch("http://127.0.0.1:5000/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                username,
                password
            })
        });

        const data = await response.json();

        if (!response.ok || !data.success) {
            message.textContent = data.message || "Invalid User ID or password.";
            message.style.color = "#c25555";
            return;
        }

        // Save only the non-sensitive user information.
        localStorage.setItem("mindsenseUserId", String(data.user.id));
        localStorage.setItem("mindsenseUsername", data.user.username);

        message.textContent = "Login successful. Redirecting...";
        message.style.color = "#2e8b68";

        setTimeout(() => {
            window.location.href = "index.html";
        }, 700);

    } catch (error) {
        console.error("LOGIN ERROR:", error);

        message.textContent =
            "Unable to connect to the server. Make sure app.py is running.";

        message.style.color = "#c25555";

    } finally {
        loginBtn.disabled = false;
        loginBtn.textContent = "Login";
    }
}
