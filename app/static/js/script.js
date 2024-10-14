document.addEventListener('DOMContentLoaded', function () {
    const courseFormsContainer = document.getElementById('courseFormsContainer');
    const addCourseBtn = document.getElementById('addCourseBtn');
    const removeCourseBtn = document.getElementById('removeCourseBtn');
    const submitAllBtn = document.getElementById('submitAllBtn');
    const lecturerNameField = document.getElementById('lecturerName');
    const designationField = document.getElementById('designation');
    const icNumberField = document.getElementById('icNumber');
    let courseCount = 1; // Start with one course form by default
    const maxCourses = 5;

    // Dummy Data for Lecturer Info
    const lecturerData = {
        "John Doe": { designation: "I", ic_number: "123456-78-9012" },
        "Jane Smith": { designation: "II", ic_number: "987654-32-1098" }
    };

    // Dummy Data for Subject Info
    const subjectData = {
        "DCS1101": { title: "Computer Architecture", lectureWeeks: 14, tutorialWeeks: 14, practicalWeeks: 13, elearningWeeks: 14 },
        "DCS1102": { title: "Data Structures", lectureWeeks: 14, tutorialWeeks: 14, practicalWeeks: 13, elearningWeeks: 14 },
        "DCS1103": { title: "UX Design", lectureWeeks: 14, tutorialWeeks: 13, practicalWeeks: 13, elearningWeeks: 14 },
        "DCS1106": { title: "High Level Programming", lectureWeeks: 14, tutorialWeeks: 14, practicalWeeks: 14, elearningWeeks: 14 }
    };

    // Auto-populate designation and IC number when lecturer changes
    lecturerNameField.addEventListener('change', function () {
        const selectedLecturer = lecturerNameField.value;
        if (lecturerData[selectedLecturer]) {
            const { designation, ic_number } = lecturerData[selectedLecturer];
            designationField.value = designation;
            icNumberField.value = ic_number;
        } else {
            designationField.value = '';
            icNumberField.value = '';
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
                        <select id="programLevel${count}" name="programLevel${count}" required>
                            <option value="">Select Program Level</option>
                            <option value="Certificate">Certificate</option>
                            <option value="Foundation">Foundation</option>
                            <option value="Diploma">Diploma</option>
                            <option value="Pre-University">Pre-University</option>
                            <option value="Degree">Degree</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="subjectCode${count}">Subject Code:</label>
                        <select id="subjectCode${count}" name="subjectCode${count}" required>
                            <option value="">Select Subject Code</option>
                            ${Object.keys(subjectData).map(code => `<option value="${code}">${code}</option>`).join('')}
                        </select>
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label for="subjectTitle${count}">Subject Title:</label>
                        <input type="text" id="subjectTitle${count}" name="subjectTitle${count}" readonly required />
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label for="lectureWeeks${count}">Lecture Weeks:</label>
                        <input type="number" id="lectureWeeks${count}" name="lectureWeeks${count}" readonly min="1" required />
                    </div>
                    <div class="form-group">
                        <label for="tutorialWeeks${count}">Tutorial Weeks:</label>
                        <input type="number" id="tutorialWeeks${count}" name="tutorialWeeks${count}" readonly min="1" required />
                    </div>
                    <div class="form-group">
                        <label for="practicalWeeks${count}">Practical Weeks:</label>
                        <input type="number" id="practicalWeeks${count}" name="practicalWeeks${count}" readonly min="1" required />
                    </div>
                    <div class="form-group">
                        <label for="elearningWeeks${count}">E-Learning Weeks:</label>
                        <input type="number" id="elearningWeeks${count}" name="elearningWeeks${count}" readonly min="1" required />
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label for="teachingPeriodStart${count}">Teaching Period Start Date:</label>
                        <input type="date" id="teachingPeriodStart${count}" name="teachingPeriodStart${count}" required />
                    </div>
                    <div class="form-group">
                        <label for="teachingPeriodEnd${count}">Teaching Period End Date:</label>
                        <input type="date" id="teachingPeriodEnd${count}" name="teachingPeriodEnd${count}" required />
                    </div>
                </div>
                <div class="form-group">
                    <label for="rate${count}">Rate (per hour):</label>
                    <input type="number" id="rate${count}" name="rate${count}" min="0" step="0.01" required />
                </div>
            </div>
        `;
        courseFormsContainer.insertAdjacentHTML('beforeend', courseFormHtml);
        attachSubjectCodeListener(count);
    }

    // Attach subject code change listener to auto-populate fields
    function attachSubjectCodeListener(count) {
        const subjectCodeField = document.getElementById(`subjectCode${count}`);
        const subjectTitleField = document.getElementById(`subjectTitle${count}`);
        const lectureWeeksField = document.getElementById(`lectureWeeks${count}`);
        const tutorialWeeksField = document.getElementById(`tutorialWeeks${count}`);
        const practicalWeeksField = document.getElementById(`practicalWeeks${count}`);
        const elearningWeeksField = document.getElementById(`elearningWeeks${count}`);

        subjectCodeField.addEventListener('change', function () {
            const selectedSubject = subjectCodeField.value;
            if (subjectData[selectedSubject]) {
                const { title, lectureWeeks, tutorialWeeks, practicalWeeks, elearningWeeks } = subjectData[selectedSubject];
                subjectTitleField.value = title;
                lectureWeeksField.value = lectureWeeks;
                tutorialWeeksField.value = tutorialWeeks;
                practicalWeeksField.value = practicalWeeks;
                elearningWeeksField.value = elearningWeeks;
            } else {
                subjectTitleField.value = '';
                lectureWeeksField.value = '';
                tutorialWeeksField.value = '';
                practicalWeeksField.value = '';
                elearningWeeksField.value = '';
            }
        });
    }

    // Function to remove the last added course form
    function removeCourseForm(count) {
        const formToRemove = document.getElementById(`courseForm${count}`);
        if (formToRemove) formToRemove.remove();
    }

    // Function to update add/remove buttons visibility
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

    addCourseBtn.addEventListener('click', function () {
        if (courseCount < maxCourses) {
            courseCount++;
            addCourseForm(courseCount);
            updateCourseButtons();
        }
    });

    removeCourseBtn.addEventListener('click', function () {
        if (courseCount > 1) {
            document.getElementById(`courseForm${courseCount}`).remove();
            courseCount--;
            updateCourseButtons();
        }
    });
});
