function togglePassword(inputId, button) {
    var input = document.getElementById(inputId);
    var icon = button.querySelector('i');

    if (input.type === 'password') {
        input.type = 'text';
        icon.classList.remove('fa-eye');
        icon.classList.add('fa-eye-slash');
    } else {
        input.type = 'password';
        icon.classList.remove('fa-eye-slash');
        icon.classList.add('fa-eye');
    }
}

function showChangePasswordModal() {
    const modal = document.getElementById('changePasswordModal');
    document.getElementById('new_password').value = '';
    document.getElementById('confirm_password').value = '';
    modal.style.display = 'block';
}

function closeChangePasswordModal() {
    const modal = document.getElementById('changePasswordModal');
    document.getElementById('new_password').value = '';
    document.getElementById('confirm_password').value = '';
    modal.style.display = 'none';
}

function submitChangePassword(role) {
    const password = document.getElementById('new_password').value;
    const confirmPassword = document.getElementById('confirm_password').value;

    if (password !== confirmPassword) {
        alert('Passwords do not match!');
        return;
    }

    const data = {
        new_password: password,
        role: role
    };

    fetch('/api/change_password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Password changed successfully');
            document.getElementById('changePasswordForm').reset();
            closeChangePasswordModal();
        } else {
            alert(data.message || 'Failed to change password');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error changing password');
    });
}
