document.addEventListener('DOMContentLoaded', function () {
    const courseFormsContainer = document.getElementById('courseFormsContainer');
    const addCourseBtn = document.getElementById('addCourseBtn');
    const submitAllBtn = document.getElementById('submitAllBtn');
    let courseCount = 1;
    const maxCourses = 5;

    // Get lecturer selection elements
    const lecturerNameContainer = document.querySelector('.lecturer-name-container');
    const lecturerSelect = document.getElementById('lecturerName');
    const newLecturerInput = document.getElementById('newLecturerName');
    const designationField = document.getElementById('designation');
    const icNumberField = document.getElementById('icNumber');

    // Handle lecturer selection change
    if (lecturerSelect) {
        lecturerSelect.addEventListener('change', async function() {
            const selectedValue = this.value;
            console.log('Selected lecturer ID:', selectedValue); // Debug log
            
            if (selectedValue === 'new_lecturer') {
                // Show input field for new lecturer
                this.style.display = 'none';
                newLecturerInput.style.display = 'block';
                newLecturerInput.focus();
                
                // Clear and enable fields for new entry
                designationField.value = '';
                icNumberField.value = '';
                designationField.readOnly = false;
                icNumberField.readOnly = false;
            } else if (selectedValue) {
                try {
                    // Fetch lecturer details from database
                    const response = await fetch(`/get_lecturer_details/${selectedValue}`);
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    const data = await response.json();
                    console.log('Lecturer data:', data); // Debug log

                    if (data.success && data.lecturer) {
                        // Auto-populate fields
                        designationField.value = data.lecturer.level || '';
                        icNumberField.value = data.lecturer.ic_no || '';
                        
                        // Make fields readonly for existing lecturers
                        designationField.readOnly = true;
                        icNumberField.readOnly = true;

                    } else {
                        console.error('Error fetching lecturer details:', data.message);
                        alert('Error fetching lecturer details: ' + data.message);
                    }
                } catch (error) {
                    console.error('Error:', error);
                    alert('Error fetching lecturer details: ' + error.message);
                }
            } else {
                // Clear fields when no selection
                designationField.value = '';
                icNumberField.value = '';
                designationField.readOnly = true;
                icNumberField.readOnly = true;
            }
        });
    }

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
        
        // Reset all fields
        lecturerSelect.value = '';
        newLecturerInput.value = '';
        designationField.value = '';
        icNumberField.value = '';
        
        // Make fields readonly again
        designationField.readOnly = true;
        icNumberField.readOnly = true;
    });

    // Show back button when typing in new lecturer name
    if (newLecturerInput) {
        newLecturerInput.addEventListener('input', function() {
            backToSelectBtn.style.display = 'block';
        });
    }

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
                            <option value="Masters">Masters</option>
                            <option value="Others">Others</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="subjectCode${count}">Subject Code:</label>
                        <select id="subjectCode${count}" name="subjectCode${count}" required>
                            <option value="">Select Subject Code</option>
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
                <div class="form-row hours-row">
                    <div class="form-group">
                        <label for="lectureHours${count}">Lecture Hours:</label>
                        <input type="number" id="lectureHours${count}" name="lectureHours${count}" readonly min="1" required />
                    </div>
                    <div class="form-group">
                        <label for="tutorialHours${count}">Tutorial Hours:</label>
                        <input type="number" id="tutorialHours${count}" name="tutorialHours${count}" readonly min="1" required />
                    </div>
                    <div class="form-group">
                        <label for="practicalHours${count}">Practical Hours:</label>
                        <input type="number" id="practicalHours${count}" name="practicalHours${count}" readonly min="1" required />
                    </div>
                    <div class="form-group">
                        <label for="blendedHours${count}">Blended Hours:</label>
                        <input type="number" id="blendedHours${count}" name="blendedHours${count}" readonly min="1" required />
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
        attachFormListeners(count);
    }

    // Update attachSubjectCodeListener to use database data
    function attachFormListeners(count) {
        const programLevelField = document.getElementById(`programLevel${count}`);
        const subjectCodeField = document.getElementById(`subjectCode${count}`);
        
        // Listen for program level changes
        programLevelField.addEventListener('change', function() {
            const selectedLevel = this.value;
            const subjectCodeField = document.getElementById(`subjectCode${count}`);
            
            if (selectedLevel) {
                fetch(`/get_subjects_by_level/${selectedLevel}`)
                    .then(response => response.json())
                    .then(data => {
                        console.log('Subjects data:', data);
                        
                        if (data.success && data.subjects) {
                            // Clear and populate the subject dropdown
                            subjectCodeField.innerHTML = `
                                <option value="">Select Subject Code</option>
                                ${Object.entries(data.subjects).map(([code, subject]) => 
                                    `<option value="${code}">${code} - ${subject.description}</option>`
                                ).join('')}
                            `;
                        } else {
                            subjectCodeField.innerHTML = '<option value="">No subjects available</option>';
                        }
                    })
                    .catch(error => {
                        console.error('Error fetching subjects:', error);
                        subjectCodeField.innerHTML = '<option value="">Error loading subjects</option>';
                    });
            } else {
                subjectCodeField.innerHTML = '<option value="">Select Subject Code</option>';
            }
        });

        // Listen for subject code changes
        subjectCodeField.addEventListener('change', function() {
            const selectedSubject = this.value;
            console.log('Selected subject:', selectedSubject);
            
            if (selectedSubject) {
                fetch(`/get_subject_details/${selectedSubject}`)
                    .then(response => response.json())
                    .then(data => {
                        console.log('Received subject details:', data);
                        if (data.success) {
                            const subject = data.subject;
                            document.getElementById(`subjectTitle${count}`).value = subject.description;
                            document.getElementById(`lectureWeeks${count}`).value = subject.lecture_weeks;
                            document.getElementById(`tutorialWeeks${count}`).value = subject.tutorial_weeks;
                            document.getElementById(`practicalWeeks${count}`).value = subject.practical_weeks;
                            document.getElementById(`elearningWeeks${count}`).value = subject.blended_weeks;
                            
                            document.getElementById(`lectureHours${count}`).value = subject.lecture_hours;
                            document.getElementById(`tutorialHours${count}`).value = subject.tutorial_hours;
                            document.getElementById(`practicalHours${count}`).value = subject.practical_hours;
                            document.getElementById(`blendedHours${count}`).value = subject.blended_hours;
                        }
                    })
                    .catch(error => console.error('Error:', error));
            } else {
                // Clear all fields if no subject selected
                document.getElementById(`subjectTitle${count}`).value = '';
                document.getElementById(`lectureWeeks${count}`).value = '';
                document.getElementById(`tutorialWeeks${count}`).value = '';
                document.getElementById(`practicalWeeks${count}`).value = '';
                document.getElementById(`elearningWeeks${count}`).value = '';
                document.getElementById(`lectureHours${count}`).value = '';
                document.getElementById(`tutorialHours${count}`).value = '';
                document.getElementById(`practicalHours${count}`).value = '';
                document.getElementById(`blendedHours${count}`).value = '';
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

    // Add this near your other event listeners
    submitAllBtn.addEventListener('click', function(e) {
        e.preventDefault();
        
        // Create FormData object
        const formData = new FormData();
        
        // Get lecturer select element
        const lecturerSelect = document.getElementById('lecturerName');
        const selectedLecturerId = lecturerSelect.value;
        
        // Get the actual lecturer name
        let lecturerName;
        if (selectedLecturerId === 'new_lecturer') {
            lecturerName = document.getElementById('newLecturerName').value;
        } else {
            // Get the selected option's text content (actual name)
            lecturerName = lecturerSelect.options[lecturerSelect.selectedIndex].text;
        }
        
        // Add lecturer info with both ID and name
        formData.append('school_centre', document.getElementById('schoolCentre').value);
        formData.append('lecturer_id', selectedLecturerId);
        formData.append('lecturer_name', lecturerName);
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
            formData.append(`lectureHours${count}`, document.getElementById(`lectureHours${count}`).value || '2');
            formData.append(`tutorialHours${count}`, document.getElementById(`tutorialHours${count}`).value || '1');
            formData.append(`practicalHours${count}`, document.getElementById(`practicalHours${count}`).value || '2');
            formData.append(`blendedHours${count}`, document.getElementById(`blendedHours${count}`).value || '1');
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

    // Update the fetchSubjects function
    function fetchSubjects(programLevel) {
        console.log('Fetching subjects for level:', programLevel); // Debug log
        return fetch(`/get_subjects_by_level/${programLevel}`)
            .then(response => response.json())
            .then(data => {
                console.log('Received subjects data:', data); // Debug log
                if (data.success) {
                    return data.subjects;
                } else {
                    console.error('Error fetching subjects:', data.message);
                    return {};
                }
            })
            .catch(error => {
                console.error('Error:', error);
                return {};
            });
    }

    function populateSubjectFields() {
        const subjectSelect = document.getElementById('subject_code');
        if (!subjectSelect) return;

        subjectSelect.addEventListener('change', function() {
            fetch('/get_subjects')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        const selectedSubject = data.subjects.find(
                            s => s.subject_code === this.value
                        );
                        if (selectedSubject) {
                            // Populate other fields
                            document.getElementById('subject_title').value = selectedSubject.subject_title;
                            document.getElementById('lecture_hours').value = selectedSubject.lecture_hours;
                            document.getElementById('tutorial_hours').value = selectedSubject.tutorial_hours;
                            document.getElementById('practical_hours').value = selectedSubject.practical_hours;
                            document.getElementById('blended_hours').value = selectedSubject.blended_hours;
                            document.getElementById('lecture_weeks').value = selectedSubject.lecture_weeks;
                            document.getElementById('tutorial_weeks').value = selectedSubject.tutorial_weeks;
                            document.getElementById('practical_weeks').value = selectedSubject.practical_weeks;
                            document.getElementById('blended_weeks').value = selectedSubject.blended_weeks;
                        }
                    }
                })
                .catch(error => console.error('Error:', error));
        });
    }

    document.addEventListener('DOMContentLoaded', function() {
        populateSubjectFields();
    });

    // When program level changes, update subject options
    document.querySelectorAll('[id^="programLevel"]').forEach(select => {
        select.addEventListener('change', function() {
            const formNumber = this.id.replace('programLevel', '');
            updateSubjectOptions(this.value, formNumber);
        });
    });

    // Update subject options based on program level
    function updateSubjectOptions(level, formNumber) {
        fetch(`/get_subjects_by_level/${level}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const subjectSelect = document.getElementById(`subjectCode${formNumber}`);
                    subjectSelect.innerHTML = '<option value="">Select Subject</option>';
                    
                    data.subjects.forEach(subject => {
                        const option = document.createElement('option');
                        option.value = subject.subject_code;
                        option.textContent = `${subject.subject_code} - ${subject.subject_title}`;
                        subjectSelect.appendChild(option);
                    });
                }
            })
            .catch(error => console.error('Error:', error));
    }

    // When subject code changes, populate other fields
    document.querySelectorAll('[id^="subjectCode"]').forEach(select => {
        select.addEventListener('change', function() {
            const formNumber = this.id.replace('subjectCode', '');
            if (this.value) {
                fetch(`/get_subject_details/${this.value}`)
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            const subject = data.subject;
                            document.getElementById(`subjectTitle${formNumber}`).value = subject.subject_title;
                            document.getElementById(`lectureWeeks${formNumber}`).value = subject.lecture_weeks;
                            document.getElementById(`tutorialWeeks${formNumber}`).value = subject.tutorial_weeks;
                            document.getElementById(`practicalWeeks${formNumber}`).value = subject.practical_weeks;
                            document.getElementById(`elearningWeeks${formNumber}`).value = subject.blended_weeks;
                        }
                    })
                    .catch(error => console.error('Error:', error));
            }
        });
    });
});
