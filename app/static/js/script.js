document.addEventListener('DOMContentLoaded', function () {
    const courseFormsContainer = document.getElementById('courseFormsContainer');
    const addCourseBtn = document.getElementById('addCourseBtn');
    const submitAllBtn = document.getElementById('submitAllBtn');
    const lecturerNameField = document.getElementById('lecturerName');
    const designationField = document.getElementById('designation');
    const icNumberField = document.getElementById('icNumber');
    let courseCount = 1; // Start with one course form by default
    const maxCourses = 5;

    // Dummy Data for Lecturer Info
    const lecturerData = {
        "John Doe": { designation: "I", ic_number: "123456-78-9012" },
        "Jane Smith": { designation: "II", ic_number: "987654-32-1098" },
        "new_lecturer": { designation: "", ic_number: "" }
    };

    // Dummy Data for Subject Info
    const subjectData = {
        "DCS1101": { title: "Computer Architecture", lectureWeeks: 14, tutorialWeeks: 14, practicalWeeks: 13, elearningWeeks: 14 },
        "DCS1102": { title: "Data Structures", lectureWeeks: 14, tutorialWeeks: 14, practicalWeeks: 13, elearningWeeks: 14 },
        "DCS1103": { title: "UX Design", lectureWeeks: 14, tutorialWeeks: 13, practicalWeeks: 13, elearningWeeks: 14 },
        "DCS1106": { title: "High Level Programming", lectureWeeks: 14, tutorialWeeks: 14, practicalWeeks: 14, elearningWeeks: 14 }
    };

    // Add new lecturer name input field (initially hidden)
    const lecturerNameContainer = document.querySelector('.lecturer-name-container');
    lecturerNameContainer.innerHTML = `
        <select id="lecturerName" name="lecturer_name" required>
            <option value="">Select Lecturer</option>
            <option value="John Doe">John Doe</option>
            <option value="Jane Smith">Jane Smith</option>
            <option value="new_lecturer">New Lecturer</option>
        </select>
        <input type="text" id="newLecturerName" name="new_lecturer_name" 
               placeholder="Enter lecturer name" class="new-lecturer-input" style="display: none;">
    `;

    // Get the new elements
    const lecturerSelect = document.getElementById('lecturerName');
    const newLecturerInput = document.getElementById('newLecturerName');

    // Update lecturer change handler
    lecturerSelect.addEventListener('change', function() {
        const selectedValue = this.value;
        if (selectedValue === 'new_lecturer') {
            // Show input field and hide select
            this.style.display = 'none';
            newLecturerInput.style.display = 'block';
            newLecturerInput.focus();
            
            // Clear the designation and IC fields
            elements.designationField.value = '';
            elements.icNumberField.value = '';
            
            // Make designation and IC fields editable
            elements.designationField.readOnly = false;
            elements.icNumberField.readOnly = false;
        } else {
            // Handle existing lecturer selection
            const lecturerInfo = lecturerData[selectedValue] || { designation: '', ic_number: '' };
            elements.designationField.value = lecturerInfo.designation;
            elements.icNumberField.value = lecturerInfo.ic_number;
            
            // Make designation and IC fields readonly
            elements.designationField.readOnly = true;
            elements.icNumberField.readOnly = true;
        }
    });

    // Add back button functionality
    const backToSelectBtn = document.createElement('button');
    backToSelectBtn.type = 'button';
    backToSelectBtn.className = 'back-to-select-btn';
    backToSelectBtn.innerHTML = '←';
    backToSelectBtn.style.display = 'none';
    lecturerNameContainer.appendChild(backToSelectBtn);

    backToSelectBtn.addEventListener('click', function() {
        // Show select and hide input
        lecturerSelect.style.display = 'block';
        newLecturerInput.style.display = 'none';
        backToSelectBtn.style.display = 'none';
        
        // Reset values
        lecturerSelect.value = '';
        newLecturerInput.value = '';
        elements.designationField.value = '';
        elements.icNumberField.value = '';
        
        // Make fields readonly again
        elements.designationField.readOnly = true;
        elements.icNumberField.readOnly = true;
    });

    // Show back button when typing in new lecturer name
    newLecturerInput.addEventListener('input', function() {
        backToSelectBtn.style.display = 'block';
    });

    // Make removeCourseForm function globally accessible
    window.removeCourseForm = function(count) {
        const formToRemove = document.getElementById(`courseForm${count}`);
        if (formToRemove) {
            formToRemove.remove();
            courseCount--;
            reorderForms();
            updateCourseButtons();
        }
    }

    // Function to add a new course form dynamically
    function addCourseForm(count) {
        const courseFormHtml = `
            <div id="courseForm${count}" class="course-form">
                ${count > 1 ? '<button type="button" class="close-btn" onclick="removeCourseForm(' + count + ')">×</button>' : ''}
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
                <div class="form-row weeks-row">
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
                        <label for="teachingPeriodStart${count}">Teaching Period Start:</label>
                        <input type="date" id="teachingPeriodStart${count}" name="teachingPeriodStart${count}" required />
                    </div>
                    <div class="form-group">
                        <label for="teachingPeriodEnd${count}">Teaching Period End:</label>
                        <input type="date" id="teachingPeriodEnd${count}" name="teachingPeriodEnd${count}" required />
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label for="rate${count}">Rate (per hour):</label>
                        <input type="number" id="hourlyRate${count}" name="hourlyRate${count}" min="0" step="0.01" required />
                    </div>
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
        if (formToRemove) {
            formToRemove.remove();
            courseCount--;
            // Reorder the remaining forms
            reorderForms();
            updateCourseButtons();
        }
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

    // Add a new function to reorder the forms after removal
    function reorderForms() {
        const forms = document.querySelectorAll('.course-form');
        forms.forEach((form, index) => {
            const newCount = index + 1;
            form.id = `courseForm${newCount}`;
            
            // Update the close button
            const closeBtn = form.querySelector('.close-btn');
            if (closeBtn) {
                closeBtn.onclick = () => removeCourseForm(newCount);
            }
            
            // Update the heading
            const heading = form.querySelector('h3');
            heading.textContent = `Course Details (${newCount}/${maxCourses})`;
            
            // Update all input IDs and labels
            updateFormElements(form, newCount);
        });
    }

    // Helper function to update form element IDs and labels
    function updateFormElements(form, newCount) {
        const elements = form.querySelectorAll('[id]');
        elements.forEach(element => {
            const oldId = element.id;
            const baseId = oldId.replace(/\d+$/, '');
            const newId = `${baseId}${newCount}`;
            
            element.id = newId;
            element.name = newId;
            
            // Update corresponding label if exists
            const label = form.querySelector(`label[for="${oldId}"]`);
            if (label) {
                label.setAttribute('for', newId);
            }
        });
    }

    // Attach lecturer selection listener
    function attachLecturerListener() {
        const lecturerSelect = document.getElementById('lecturerName');
        const designationField = document.getElementById('designation');
        const icNumberField = document.getElementById('icNumber');

        lecturerSelect.addEventListener('change', function () {
            const selectedLecturer = lecturerSelect.value;
            if (lecturerData[selectedLecturer]) {
                const { designation, ic_number } = lecturerData[selectedLecturer];
                designationField.value = designation;
                icNumberField.value = ic_number;
            } else {
                designationField.value = '';
                icNumberField.value = '';
            }
        });
    }

    // Call the function to attach the listener
    attachLecturerListener();

    // Add this near your other event listeners
    submitAllBtn.addEventListener('click', function(e) {
        e.preventDefault();
        console.log('Submit button clicked'); // Debug log

        // Get all form data
        const formData = new FormData();
        
        // Add lecturer info
        formData.append('school_centre', document.getElementById('schoolCentre').value);
        formData.append('lecturer_name', document.getElementById('lecturerName').value);
        formData.append('designation', document.getElementById('designation').value);
        formData.append('ic_number', document.getElementById('icNumber').value);

        // Add course details
        const forms = document.querySelectorAll('.course-form');
        forms.forEach((form, index) => {
            const count = index + 1;
            formData.append(`programLevel${count}`, document.getElementById(`programLevel${count}`).value);
            formData.append(`subjectCode${count}`, document.getElementById(`subjectCode${count}`).value);
            formData.append(`subjectTitle${count}`, document.getElementById(`subjectTitle${count}`).value);
            formData.append(`lectureWeeks${count}`, document.getElementById(`lectureWeeks${count}`).value);
            formData.append(`tutorialWeeks${count}`, document.getElementById(`tutorialWeeks${count}`).value);
            formData.append(`practicalWeeks${count}`, document.getElementById(`practicalWeeks${count}`).value);
            formData.append(`elearningWeeks${count}`, document.getElementById(`elearningWeeks${count}`).value);
            formData.append(`teachingPeriodStart${count}`, document.getElementById(`teachingPeriodStart${count}`).value);
            formData.append(`teachingPeriodEnd${count}`, document.getElementById(`teachingPeriodEnd${count}`).value);
            formData.append(`hourlyRate${count}`, document.getElementById(`hourlyRate${count}`).value);  // Add this line
        });

        // Send form data to server
        fetch('/result', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            console.log('Success:', data); // Debug log
            if (data.success) {
                window.location.href = `/result_page?filename=${data.filename}`;
            } else {
                alert('Error: ' + (data.error || 'Unknown error occurred'));
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error submitting form: ' + error.message);
        });
    });
});
