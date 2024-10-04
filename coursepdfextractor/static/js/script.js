document.addEventListener('DOMContentLoaded', function() {
    const courseFormsContainer = document.getElementById('courseFormsContainer');
    const lecturerSelect = document.getElementById('lecturerName');
    const addCourseBtn = document.getElementById('addCourseBtn');
    const removeCourseBtn = document.getElementById('removeCourseBtn');
    const downloadExcelButton = document.getElementById('submitAllBtn');
    let courseCount = 1; // Start with one course form by default
    const maxCourses = 4;

    // Event listener for adding a new course form
    addCourseBtn.addEventListener('click', function() {
        if (courseCount < maxCourses) {
            courseCount++;
            addCourseForm(courseCount);
            updateCourseButtons();
        }
    });

    // Event listener for removing the last added course form
    removeCourseBtn.addEventListener('click', function() {
        if (courseCount > 1) {
            removeCourseForm(courseCount);
            courseCount--;
            updateCourseButtons();
        }
    });

    // Function to add a new course form dynamically
    function addCourseForm(count) {
        const courseFormHtml = `
            <div id="courseForm${count}" class="course-form">
                <h3>Course Details (${count}/${maxCourses})</h3>
                <div class="form-row">
                    <div class="form-group">
                        <label for="programLevel${count}">Program Level:</label>
                        <select id="programLevel${count}" name="programLevel${count}">
                            <option value="">Select Program Level</option>
                            <option value="cert">Cert</option>
                            <option value="found">Foundation</option>
                            <option value="dip">Diploma</option>
                            <option value="preu">Pre-U</option>
                            <option value="degree">Degree</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="subjectCode${count}">Subject Code:</label>
                        <select id="subjectCode${count}" name="subjectCode${count}">
                            <option value="">Select Subject Code</option>
                            <!-- Hardcode options for now -->
                            <option value="CS101">CS101</option>
                            <option value="CS102">CS102</option>
                            <!-- More options as needed -->
                        </select>
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label for="subjectTitle${count}">Subject Title:</label>
                        <input type="text" id="subjectTitle${count}" name="subjectTitle${count}" readonly>
                    </div>
                    <div class="form-group">
                        <label for="weeks${count}">Number of Weeks:</label>
                        <input type="number" id="weeks${count}" name="weeks${count}" min="1" required>
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label for="teachingPeriodStart${count}">Teaching Period Start Date:</label>
                        <input type="date" id="teachingPeriodStart${count}" name="teachingPeriodStart${count}" readonly>
                    </div>
                    <div class="form-group">
                        <label for="teachingPeriodEnd${count}">Teaching Period End Date:</label>
                        <input type="date" id="teachingPeriodEnd${count}" name="teachingPeriodEnd${count}" readonly>
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
        if (courseCount === maxCourses) {
            addCourseBtn.disabled = true;
        } else {
            addCourseBtn.disabled = false;
        }

        // Enable/Disable remove button based on count
        if (courseCount > 1) {
            removeCourseBtn.style.display = 'inline-block';
        } else {
            removeCourseBtn.style.display = 'none';
        }
    }

    // Initialize with one course form by default
    addCourseForm(courseCount);
    updateCourseButtons();
});
