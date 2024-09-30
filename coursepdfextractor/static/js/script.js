document.addEventListener('DOMContentLoaded', function() {
    const courseForm = document.getElementById('courseForm');
    const lecturerSelect = document.getElementById('lecturer');
    const subjectCodeSelect = document.getElementById('subjectCode');
    const downloadExcelButton = document.getElementById('downloadExcel');

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
            window.location.href = '/main';
        });
    }
});