document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.querySelector('.login-form');
    const courseForm = document.getElementById('courseForm');
    const lecturerSelect = document.getElementById('lecturer');
    const subjectCodeSelect = document.getElementById('subjectCode');
    const logoutButtons = document.querySelectorAll('.logout');
    const downloadExcelButton = document.getElementById('downloadExcel');

    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            console.log('Login attempted with:', email, password);
            // Here you would typically send a request to your server to authenticate
            window.location.href = 'main';
        });
    }

    if (courseForm) {
        lecturerSelect.addEventListener('change', function() {
            fetch('/get_lecturer_info', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({lecturer_id: this.value}),
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('level').value = data.level;
                document.getElementById('email').value = data.email;
                document.getElementById('hourlyRate').value = data.hourlyRate;
            });
        });

        subjectCodeSelect.addEventListener('change', function() {
            fetch('/get_subject_info', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({subject_code: this.value}),
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('subjectTitle').value = data.title;
                document.getElementById('startDate').value = data.startDate;
                document.getElementById('endDate').value = data.endDate;
            });
        });
    }

    if (downloadExcelButton) {
        downloadExcelButton.addEventListener('click', function(e) {
            e.preventDefault();
            window.location.href = '/download_excel';
        });
    }
});