const signupBtn = document.getElementById("signupBtn");
const signupMessage = document.getElementById("signupMessage");

signupBtn.addEventListener("click", createAccount);

async function createAccount() {
    const username = document
        .getElementById("signupUsername")
        .value
        .trim();

    const password = document
        .getElementById("signupPassword")
        .value;

    const confirmPassword = document
        .getElementById("confirmPassword")
        .value;

    signupMessage.textContent = "";
    signupMessage.className = "";

    // -----------------------------
    // Front-end validation
    // -----------------------------

    if (!username || !password || !confirmPassword) {
        showMessage("Please fill in all fields.", "error");
        return;
    }

    if (username.length < 3 || username.length > 50) {
        showMessage("User ID must be between 3 and 50 characters.", "error");
        return;
    }

    if (!/^[A-Za-z0-9_-]+$/.test(username)) {
        showMessage(
            "User ID can contain only letters, numbers, _ and -.",
            "error"
        );
        return;
    }

    if (password.length < 6) {
        showMessage(
            "Password must contain at least 6 characters.",
            "error"
        );
        return;
    }

    if (password !== confirmPassword) {
        showMessage("Passwords do not match.", "error");
        return;
    }

    // -----------------------------
    // Disable button during request
    // -----------------------------

    signupBtn.disabled = true;
    signupBtn.textContent = "Creating account...";

    try {
        const response = await fetch("http://127.0.0.1:5000/signup", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                username: username,
                password: password
            })
        });

        // Handle server responses that are not JSON.
        let data;

        try {
            data = await response.json();
        } catch {
            throw new Error("The server returned an invalid response.");
        }

        if (!response.ok || !data.success) {
            showMessage(
                data.message || "Unable to create the account.",
                "error"
            );
            return;
        }

        showMessage(
            "Account created successfully. Redirecting to login...",
            "success"
        );

        // Clear password fields.
        document.getElementById("signupPassword").value = "";
        document.getElementById("confirmPassword").value = "";

        setTimeout(() => {
            window.location.href = "login.html";
        }, 1200);

    } catch (error) {
        console.error("SIGNUP ERROR:", error);

        showMessage(
            "Unable to connect to the server. Make sure app.py is running.",
            "error"
        );

    } finally {
        signupBtn.disabled = false;
        signupBtn.textContent = "Create Account";
    }
}


function showMessage(text, type) {
    signupMessage.textContent = text;
    signupMessage.className = type;

    signupMessage.style.marginTop = "14px";
    signupMessage.style.fontSize = "13px";

    if (type === "success") {
        signupMessage.style.color = "#2e8b68";
    } else {
        signupMessage.style.color = "#c25555";
    }
}


// Allow Enter key to submit.
document.querySelectorAll(
    "#signupUsername, #signupPassword, #confirmPassword"
).forEach(input => {
    input.addEventListener("keydown", event => {
        if (event.key === "Enter") {
            event.preventDefault();
            createAccount();
        }
    });
});
