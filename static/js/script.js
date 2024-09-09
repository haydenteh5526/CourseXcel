document.addEventListener('DOMContentLoaded', function() {
    const courseForm = document.getElementById('courseForm');
    const lecturerSelect = document.getElementById('lecturer');
    const subjectCodeSelect = document.getElementById('subjectCode');
    const downloadExcelButton = document.getElementById('downloadExcel');
    const loginForm = document.getElementById('loginForm');
    const logoutButton = document.querySelector('.logout');

    // Helper function for AJAX requests
    function fetchJSON(url, options) {
        return fetch(url, options)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred. Please try again.');
            });
    }

    if (courseForm) {
        lecturerSelect.addEventListener('change', function() {
            fetchJSON('/get_lecturer_info', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrf_token')
                },
                body: JSON.stringify({lecturer_id: this.value}),
            })
            .then(data => {
                document.getElementById('level').value = data.level || '';
                document.getElementById('email').value = data.email || '';
                document.getElementById('hourlyRate').value = data.hourlyRate || '';
            });
        });

        subjectCodeSelect.addEventListener('change', function() {
            fetchJSON('/get_subject_info', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrf_token')
                },
                body: JSON.stringify({subject_code: this.value}),
            })
            .then(data => {
                document.getElementById('subjectTitle').value = data.title || '';
                document.getElementById('startDate').value = data.startDate || '';
                document.getElementById('endDate').value = data.endDate || '';
            });
        });
    }

    if (downloadExcelButton) {
        downloadExcelButton.addEventListener('click', function(e) {
            e.preventDefault();
            window.location.href = '/download_excel';
        });
    }

    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(this);
            
            fetchJSON('/login', {
                method: 'POST',
                body: formData
            })
            .then(data => {
                if (data.success) {
                    window.location.href = '/main';
                } else {
                    alert(data.message);
                }
            });
        });
    }

    if (logoutButton) {
        logoutButton.addEventListener('click', function(e) {
            e.preventDefault();
            fetchJSON('/logout', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrf_token')
                }
            })
            .then(data => {
                if (data.success) {
                    window.location.href = '/login';
                } else {
                    alert(data.message);
                }
            });
        });
    }

    // Helper function to get CSRF token from cookies
    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
    }
});