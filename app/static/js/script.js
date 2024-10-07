document.addEventListener('DOMContentLoaded', function () {
    const courseFormsContainer = document.getElementById('courseFormsContainer');
    const addCourseBtn = document.getElementById('addCourseBtn');
    const removeCourseBtn = document.getElementById('removeCourseBtn');
    const submitAllBtn = document.getElementById('submitAllBtn');
    let courseCount = 1; // Start with one course form by default
    const maxCourses = 4;

    // Function to add a new course form dynamically
    function addCourseForm(count) {
        const courseFormHtml = `
            <div id="courseForm${count}" class="course-form">
                <h3>Course Details (${count}/${maxCourses})</h3>
                <div class="form-row">
                    <div class="form-group">
                        <label for="programLevel${count}">Program Level:</label>
                        <select id="programLevel${count}" name="programLevel${count}" required>
                            <option value="">Select Program Level</option>
                            <option value="Certificate">Cert</option>
                            <option value="Foundation">Foundation</option>
                            <option value="Diploma">Diploma</option>
                            <option value="Pre-University">Pre-U</option>
                            <option value="Degree">Degree</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="subjectCode${count}">Subject Code:</label>
                        <select id="subjectCode${count}" name="subjectCode${count}" required>
                            <option value="">Select Subject Code</option>
                            <option value="CS101">DCS1101</option>
                            <option value="CS102">DCS1102</option>
                            <option value="CS103">DCS1103</option>
                            <option value="CS104">DCS1106</option>
                        </select>
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label for="subjectTitle${count}">Subject Title:</label>
                        <input type="text" id="subjectTitle${count}" name="subjectTitle${count}" required>
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label for="lectureWeeks${count}">Lecture Weeks:</label>
                        <input type="number" id="lectureWeeks${count}" name="lectureWeeks${count}" min="1" required>
                    </div>
                    <div class="form-group">
                        <label for="tutorialWeeks${count}">Tutorial Weeks:</label>
                        <input type="number" id="tutorialWeeks${count}" name="tutorialWeeks${count}" min="1" required>
                    </div>
                    <div class="form-group">
                        <label for="practicalWeeks${count}">Practical Weeks:</label>
                        <input type="number" id="practicalWeeks${count}" name="practicalWeeks${count}" min="1" required>
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label for="teachingPeriodStart${count}">Teaching Period Start Date:</label>
                        <input type="date" id="teachingPeriodStart${count}" name="teachingPeriodStart${count}" required>
                    </div>
                    <div class="form-group">
                        <label for="teachingPeriodEnd${count}">Teaching Period End Date:</label>
                        <input type="date" id="teachingPeriodEnd${count}" name="teachingPeriodEnd${count}" required>
                    </div>
                </div>
                <div class="form-group">
                    <label for="pdfFile${count}">Upload PDF:</label>
                    <input type="file" id="pdfFile${count}" name="pdfFile${count}" accept=".pdf" required>
                </div>
            </div>
        `;
        courseFormsContainer.insertAdjacentHTML('beforeend', courseFormHtml);
    }

    // Function to remove the last added course form
    function removeCourseForm(count) {
        const formToRemove = document.getElementById(`courseForm${count}`);
        if (formToRemove) formToRemove.remove();
    }

    // Function to update the add/remove buttons
    function updateCourseButtons() {
        addCourseBtn.textContent = `Add Course Details (${courseCount + 1}/${maxCourses})`;
        
        // Hide the add button when the maximum number of courses is reached
        if (courseCount === maxCourses) {
            addCourseBtn.style.display = 'none';
        } else {
            addCourseBtn.style.display = 'inline-block';
        }
        
        removeCourseBtn.style.display = (courseCount > 1) ? 'inline-block' : 'none';
    }

    // Initialize with one course form by default
    addCourseForm(courseCount);
    updateCourseButtons();

    // Event listener for adding a new course form
    addCourseBtn.addEventListener('click', function () {
        if (courseCount < maxCourses) {
            courseCount++;
            addCourseForm(courseCount);
            updateCourseButtons();
        }
    });

    // Event listener for removing the last added course form
    removeCourseBtn.addEventListener('click', function () {
        if (courseCount > 1) {
            removeCourseForm(courseCount);
            courseCount--;
            updateCourseButtons();
        }
    });

    // Event listener for submitting all data
    submitAllBtn.addEventListener('click', function (e) {
        e.preventDefault(); // Prevent default form submission
        
        const formData = new FormData(document.getElementById('lecturerForm'));

        // Append additional lecturer details to formData
        formData.append('school_centre', document.getElementById('schoolCentre').value);

        // Append course details and files to formData
        for (let i = 1; i <= courseCount; i++) {
            formData.append(`pdfFile${i}`, document.getElementById(`pdfFile${i}`).files[0]);

            // Append weeks for lecture, tutorial, and practical classes
            formData.append(`lectureWeeks${i}`, document.getElementById(`lectureWeeks${i}`).value);
            formData.append(`tutorialWeeks${i}`, document.getElementById(`tutorialWeeks${i}`).value);
            formData.append(`practicalWeeks${i}`, document.getElementById(`practicalWeeks${i}`).value);
        }

        // Debugging: log formData key-value pairs
        for (let pair of formData.entries()) {
            console.log(`${pair[0]}, ${pair[1]}`);
        }

        // Send formData to the server
        fetch('/result', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success && data.filename) {
                window.location.href = `/result_page?filename=${data.filename}`;
            } else {
                alert('Conversion failed: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error during submission:', error);
            alert('An error occurred while submitting the form.');
        });
    });
});
