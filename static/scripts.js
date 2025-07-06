// <!-- Password Toggle Script -->

document.addEventListener("DOMContentLoaded", function () {
    const passwordInput = document.getElementById("password");
    const toggleIcon = document.getElementById("eyeIcon");
    const toggleButton = document.getElementById("togglePassword");

    toggleButton.addEventListener("click", function () {
        const isPassword = passwordInput.type === "password";
        passwordInput.type = isPassword ? "text" : "password";
        toggleIcon.className = isPassword ? "bi bi-eye-slash-fill" : "bi bi-eye-fill";
    });
});

