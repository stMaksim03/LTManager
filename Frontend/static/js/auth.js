document.addEventListener('DOMContentLoaded', function() {
    const registerButton = document.getElementById('show-register');
    const loginButton = document.getElementById('show-login');
    const registerForm = document.getElementById('register-form');
    const loginForm = document.getElementById('login-container');
    
    registerButton.addEventListener('click', () => {
        registerForm.classList.add('active');
        loginForm.classList.remove('active');
    });
    
    loginButton.addEventListener('click', () => {
        loginForm.classList.add('active');
        registerForm.classList.remove('active');
    });
});