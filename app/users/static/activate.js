// Obtener token de la URL
const urlParams = new URLSearchParams(window.location.search);
const token = urlParams.get('token');

const API_URL = 'http://localhost:8000/graphql';

// Elementos del DOM
const form = document.getElementById('activateForm');
const userInfo = document.getElementById('userInfo');
const userName = document.getElementById('userName');
const userEmail = document.getElementById('userEmail');
const errorMessage = document.getElementById('errorMessage');
const tokenError = document.getElementById('tokenError');
const loading = document.getElementById('loading');

// Validación de contraseña en tiempo real
const passwordInput = document.getElementById('password');
const passwordConfirmation = document.getElementById('passwordConfirmation');

const requirements = {
    length: /^.{8,}$/,
    upper: /[A-Z]/,
    lower: /[a-z]/,
    number: /\d/,
    special: /[!@#$%^&*(),.?":{}|<>]/
};

passwordInput.addEventListener('input', function() {
    const password = this.value;

    // Validar cada requisito
    Object.keys(requirements).forEach(req => {
        const element = document.getElementById(`req-${req}`);
        if (requirements[req].test(password)) {
            element.classList.add('valid');
            element.textContent = element.textContent.replace('✗', '✓');
        } else {
            element.classList.remove('valid');
            element.textContent = element.textContent.replace('✓', '✗');
        }
    });
});

passwordConfirmation.addEventListener('input', function() {
    const matchElement = document.getElementById('password-match');
    if (this.value) {
        if (this.value === passwordInput.value) {
            matchElement.textContent = '✓ Las contraseñas coinciden';
            matchElement.style.color = '#27ae60';
            matchElement.style.display = 'block';
        } else {
            matchElement.textContent = '✗ Las contraseñas no coinciden';
            matchElement.style.color = '#c62828';
            matchElement.style.display = 'block';
        }
    } else {
        matchElement.style.display = 'none';
    }
});

// Verificar que hay token
if (!token) {
    showTokenError('Token de activación no encontrado en la URL');
} else {
    validateToken();
}

// Validar token al cargar
async function validateToken() {
    showLoading(true);

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                query: `
                    query {
                        validateActivationToken(input: { token: "${token}" }) {
                            isValid
                            reason
                            user {
                                fullName
                                email
                            }
                            expiresAt
                        }
                    }
                `
            })
        });

        const result = await response.json();

        if (result.errors) {
            throw new Error(result.errors[0].message);
        }

        const validation = result.data.validateActivationToken;

        if (!validation.isValid) {
            showTokenError(validation.reason || 'Token inválido o expirado');
        } else {
            // Token válido, mostrar formulario
            userName.textContent = validation.user.fullName;
            userEmail.textContent = validation.user.email;
            userInfo.style.display = 'block';
            form.style.display = 'block';
        }
    } catch (error) {
        showTokenError('Error al validar el token: ' + error.message);
    } finally {
        showLoading(false);
    }
}

// Manejar envío del formulario
form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const employeeId = document.getElementById('employeeId').value.trim();
    const password = document.getElementById('password').value;
    const passwordConfirmation = document.getElementById('passwordConfirmation').value;
    const personalEmail = document.getElementById('personalEmail').value.trim();
    const consent = document.getElementById('consent').checked;

    // Validaciones del lado del cliente
    if (password !== passwordConfirmation) {
        showError('Las contraseñas no coinciden');
        return;
    }

    if (!consent) {
        showError('Debes aceptar el tratamiento de datos para continuar');
        return;
    }

    // Validar requisitos de contraseña
    const isPasswordValid = Object.values(requirements).every(regex => regex.test(password));
    if (!isPasswordValid) {
        showError('La contraseña no cumple con todos los requisitos de seguridad');
        return;
    }

    showLoading(true);
    hideError();

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                query: `
                    mutation {
                        activateUserAccount(input: {
                            token: "${token}"
                            employeeId: "${employeeId}"
                            password: "${password}"
                            passwordConfirmation: "${passwordConfirmation}"
                            personalEmail: "${personalEmail}"
                            dataProcessingConsent: ${consent}
                        }) {
                            success
                            message
                            userId
                        }
                    }
                `
            })
        });

        const result = await response.json();

        if (result.errors) {
            throw new Error(result.errors[0].message);
        }

        const activation = result.data.activateUserAccount;

        if (activation.success) {
            // Redirigir a página de éxito
            window.location.href = '/activate/success';
        } else {
            showError(activation.message);
        }
    } catch (error) {
        showError('Error al activar la cuenta: ' + error.message);
    } finally {
        showLoading(false);
    }
});

// Funciones auxiliares
function showError(message) {
    errorMessage.textContent = message;
    errorMessage.style.display = 'block';
    errorMessage.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function hideError() {
    errorMessage.style.display = 'none';
}

function showTokenError(message) {
    tokenError.textContent = message;
    tokenError.style.display = 'block';
    form.style.display = 'none';
    userInfo.style.display = 'none';
}

function showLoading(show) {
    loading.style.display = show ? 'block' : 'none';
    form.style.display = show ? 'none' : (token ? 'block' : 'none');
}