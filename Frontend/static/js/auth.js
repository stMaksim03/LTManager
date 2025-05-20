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

    function validateEmail(email) {
        const re = /^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$/;
        return re.test(String(email));
    }

    function validatePassword(password) {
        const re = /^(?=.*[0-9])(?=.*[a-z])(?=.*[A-Z])(?=.*[-!@#$%^&*()_+№;:?=]).{8,}$/;
        return re.test(String(password));
    }

    // Обработка формы регистрации
    document.getElementById('registration-form').addEventListener('submit', function(e) {
        e.preventDefault();
        
        const email = document.getElementById('register-email').value;
        const password = document.getElementById('register-password').value;
        let isValid = true;
        
        if (!validateEmail(email)) {
            document.getElementById('register-email-error').textContent = 'Введенный email некорректный';
            isValid = false;
        } else {
            document.getElementById('register-email-error').textContent = '';
        }
        
        if (!validatePassword(password)) {
            document.getElementById('register-password-error').textContent = 'Пароль должен содержать минимум 8 символов (строчные и заглавные буквы, цифры, спец. символы)';
            isValid = false;
        } else {
            document.getElementById('register-password-error').textContent = '';
        }
        
        if (isValid) {
            fetch('http://localhost:5000/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams(new FormData(this))
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    window.location.href = '/';
                } else {
                    alert('Ошибка регистрации: ' + data.message);
                }
            });
        }
    });

    // Обработка формы входа
    document.getElementById('login-form').addEventListener('submit', function(e) {
        e.preventDefault();
        
        const email = document.getElementById('login-email').value;
        const password = document.getElementById('login-password').value;
        let isValid = true;
        
        if (!validateEmail(email)) {
            document.getElementById('login-email-error').textContent = 'Введенный email некорректный';
            isValid = false;
        } else {
            document.getElementById('login-email-error').textContent = '';
        }
        
        if (!validatePassword(password)) {
            document.getElementById('login-password-error').textContent = 'Пароль должен содержать минимум 8 символов (строчные и заглавные буквы, цифры, спец. символы)';
            isValid = false;
        } else {
            document.getElementById('login-password-error').textContent = '';
        }
        
        if (isValid) {
            fetch('http://localhost:5000/login', {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams(new FormData(this))
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    window.location.href = '/';
                } else {
                    alert('Ошибка входа: ' + data.message);
                }
            });
        }
    });
});