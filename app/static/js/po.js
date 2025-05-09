document.addEventListener('DOMContentLoaded', function () {
    setupTableSearch();  

    const container = document.getElementById('lecturers');
    if (container) {
        const prevBtn = container.querySelector('.prev-btn');
        const nextBtn = container.querySelector('.next-btn');

        if (prevBtn) {
            prevBtn.addEventListener('click', () => {
                if (currentLecturerPage > 1) {
                    currentLecturerPage--;
                    updateTable(currentLecturerPage);
                }
            });
        }

        if (nextBtn) {
            nextBtn.addEventListener('click', () => {
                const tableElement = document.getElementById('lecturersTable');
                const rows = Array.from(tableElement.querySelectorAll('tbody tr'));
                const filteredRows = rows.filter(row => row.dataset.searchMatch !== 'false');
                const totalPages = Math.ceil(filteredRows.length / RECORDS_PER_PAGE);

                if (currentLecturerPage < totalPages) {
                    currentLecturerPage++;
                    updateTable(currentLecturerPage);
                }
            });
        }

        // Initialize table pagination
        updateTable(1);
    }

    const courseFormsContainer = document.getElementById('courseFormsContainer');
    const addCourseBtn = document.getElementById('addCourseBtn');
    const submitAllBtn = document.getElementById('submitAllBtn');
    let courseCount = 1;

    // Get lecturer selection elements
    const lecturerSelect = document.getElementById('lecturerName');
    const designationField = document.getElementById('designation');
    const icNumberField = document.getElementById('icNumber');

    // Handle lecturer selection change
    if (lecturerSelect) {
        lecturerSelect.addEventListener('change', async function() {
            const selectedValue = this.value;
            
            if (selectedValue) {
                try {
                    const response = await fetch(`/get_lecturer_details/${selectedValue}`);
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    const data = await response.json();
                    
                    if (data.success && data.lecturer) {
                        // Auto-populate fields
                        designationField.value = data.lecturer.level || '';
                        icNumberField.value = data.lecturer.ic_no || '';
                        
                        // Make fields readonly for existing lecturers
                        designationField.style.display = 'block';
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
                designationField.style.display = 'block';
                designationField.readOnly = true;
                icNumberField.readOnly = true;
            }
        });
    }

    // Helper function to clear subject fields
    function clearSubjectFields(count) {
        const fields = [
            'subjectTitle', 'lectureWeeks', 'tutorialWeeks', 
            'practicalWeeks', 'elearningWeeks', 'lectureHours', 
            'tutorialHours', 'practicalHours', 'blendedHours'
        ];
        
        fields.forEach(field => {
            document.getElementById(`${field}${count}`).value = '';
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

    function addCourseForm(count) {
        const courseFormHtml = `
            <div id="courseForm${count}" class="course-form">
                ${count > 1 ? '<button type="button" class="close-btn" onclick="removeCourseForm(' + count + ')">×</button>' : ''}
                <h3>Course Details (${count})</h3>
                <div class="form-row">
                    <div class="form-group">
                        <label for="programLevel${count}">Program Level:</label>
                        <select id="programLevel${count}" name="programLevel${count}" required>
                            <option value="">Select Program Level</option>
                            <option value="Certificate">Certificate</option>
                            <option value="Foundation">Foundation</option>
                            <option value="Diploma">Diploma</option>
                            <option value="Degree">Degree</option>
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
                        <label for="hourlyRate${count}">Rate (RM per hour):</label>
                        <select id="hourlyRate${count}" name="hourlyRate${count}" required>
                            <option value="">Select Rate</option>
                            <option value="60">60</option>
                            <option value="65">65</option>
                            <option value="70">70</option>
                            <option value="75">75</option>
                            <option value="80">80</option>
                            <option value="85">85</option>
                            <option value="90">90</option>
                            <option value="95">95</option>
                            <option value="100">100</option>
                        </select>
                    </div>
                </div>
            </div>
        `;
        courseFormsContainer.insertAdjacentHTML('beforeend', courseFormHtml);
        attachFormListeners(count);
    }

    function attachFormListeners(count) {
        const programLevelField = document.getElementById(`programLevel${count}`);
        const subjectCodeField = document.getElementById(`subjectCode${count}`);
        
        // Listen for program level changes
        programLevelField.addEventListener('change', function() {
            const selectedLevel = this.value;
            if (selectedLevel) {
                fetch(`/get_subjects_by_level/${selectedLevel}`)
                    .then(response => response.json())
                    .then(data => {                        
                        if (data.success && data.subjects && data.subjects.length > 0) {
                            // Clear and populate the subject dropdown
                            subjectCodeField.innerHTML = '<option value="">Select Subject Code</option>';
                            
                            data.subjects.forEach(subject => {
                                const option = document.createElement('option');
                                option.value = subject.subject_code;
                                option.textContent = `${subject.subject_code} - ${subject.subject_title}`;
                                subjectCodeField.appendChild(option);
                            });
                        } else {
                            subjectCodeField.innerHTML = '<option value="">No subjects available</option>';
                            clearSubjectFields(count);
                        }
                    })
                    .catch(error => {
                        console.error('Error fetching subjects:', error);
                        subjectCodeField.innerHTML = '<option value="">Error loading subjects</option>';
                        clearSubjectFields(count);
                    });
            } else {
                subjectCodeField.innerHTML = '<option value="">Select Subject Code</option>';
                clearSubjectFields(count);
            }
        });

        // Attach the subject code change listener
        populateSubjectFields(count);
    }

    function populateSubjectFields(count) {
        const subjectSelect = document.getElementById(`subjectCode${count}`);
        if (!subjectSelect) return;

        subjectSelect.addEventListener('change', function() {
            const selectedSubjectCode = this.value;
            if (!selectedSubjectCode) {
                clearSubjectFields(count);
                return;
            }

            fetch(`/get_subject_details/${selectedSubjectCode}`)
                .then(response => response.json())
                .then(data => {                    
                    if (data.success && data.subject) {
                        const subject = data.subject;
                        document.getElementById(`subjectTitle${count}`).value = subject.subject_title || '';
                        document.getElementById(`lectureHours${count}`).value = subject.lecture_hours ?? '';
                        document.getElementById(`tutorialHours${count}`).value = subject.tutorial_hours ?? '';
                        document.getElementById(`practicalHours${count}`).value = subject.practical_hours ?? '';
                        document.getElementById(`blendedHours${count}`).value = subject.blended_hours ?? '';
                        document.getElementById(`lectureWeeks${count}`).value = subject.lecture_weeks ?? '';
                        document.getElementById(`tutorialWeeks${count}`).value = subject.tutorial_weeks ?? '';
                        document.getElementById(`practicalWeeks${count}`).value = subject.practical_weeks ?? '';
                        document.getElementById(`elearningWeeks${count}`).value = subject.blended_weeks ?? '';
                    } else {
                        console.error('Error:', data.message);
                        clearSubjectFields(count);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    clearSubjectFields(count);
                });
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
        addCourseBtn.textContent = `Add Course Details (${courseCount + 1})`;
        addCourseBtn.style.display = 'inline-block';
    }

    // Initialize with one course form by default
    addCourseForm(courseCount);
    updateCourseButtons();

    addCourseBtn.addEventListener('click', function () {
        courseCount++;
        addCourseForm(courseCount);
        updateCourseButtons();
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
            heading.textContent = `Course Details (${newCount})`;
            
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

    // Add this validation function
    function validateRequiredFields() {
        const forms = document.querySelectorAll('.course-form');
        
        for (let i = 0; i < forms.length; i++) {
            const formNumber = i + 1;
            const startDate = document.getElementById(`teachingPeriodStart${formNumber}`).value;
            const endDate = document.getElementById(`teachingPeriodEnd${formNumber}`).value;
            const rate = document.getElementById(`hourlyRate${formNumber}`).value;
    
            if (!startDate || !endDate || !rate) {
                alert("Please make sure to fill in all required fields");
                return false;
            }
    
            // Validate that end date is after start date
            if (new Date(endDate) <= new Date(startDate)) {
                alert(`Course ${formNumber}: Teaching Period End must be after Teaching Period Start`);
                return false;
            }
        }
        return true;
    }    

    // Add this new validation function
    function validateLecturerDetails() {
        const schoolCentre = document.getElementById('schoolCentre').value;
        const lecturerSelect = document.getElementById('lecturerName');

        if (!schoolCentre) {
            alert('Please select a School/Centre');
            return false;
        }

        if (!lecturerSelect.value) {
            alert('Please select a lecturer');
            return false;
        }

        return true;
    }

    // Modify the submit button event listener
    submitAllBtn.addEventListener('click', async function(e) {
        e.preventDefault();
        
        // Add lecturer details validation before proceeding
        if (!validateLecturerDetails()) {
            return;
        }
        
        // Add existing validation check
        if (!validateRequiredFields()) {
            return;
        }
        
        // Create FormData object
        const formData = new FormData();
        
        // Get lecturer select element
        const lecturerSelect = document.getElementById('lecturerName');
        const selectedLecturerId = lecturerSelect.value;
        
        formData.append('lecturer_id', selectedLecturerId);
        formData.append('name', lecturerSelect.options[lecturerSelect.selectedIndex].text);
        
        // Add lecturer info with both ID and name
        formData.append('school_centre', document.getElementById('schoolCentre').value);
        formData.append('designation',  document.getElementById('designation').value);
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
            formData.append(`lectureHours${count}`, document.getElementById(`lectureHours${count}`).value || '0');
            formData.append(`tutorialHours${count}`, document.getElementById(`tutorialHours${count}`).value || '0');
            formData.append(`practicalHours${count}`, document.getElementById(`practicalHours${count}`).value || '0');
            formData.append(`blendedHours${count}`, document.getElementById(`blendedHours${count}`).value || '1');
        });

        // Send form data to server
        fetch('/poConversionResultPage', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            console.log('Success:', data); // Debug log
            if (data.success) {
                window.location.href = `/poConversionResultDownload?filename=${data.filename}`;
            } else {
                alert('Error: ' + (data.error || 'Unknown error occurred'));
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error submitting form: ' + error.message);
        });
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
                    subjectSelect.innerHTML = '<option value="">Select Subject Code</option>';
                    
                    data.subjects.forEach(subject => {
                        const option = document.createElement('option');
                        option.value = subject.subject_code;
                        option.textContent = `${subject.subject_code} - ${subject.subject_title}`;
                        subjectSelect.appendChild(option);
                    });
                } else {
                    console.error('Error loading subjects:', data.message);
                }
            })
            .catch(error => console.error('Error:', error));
    }
});

// Add these constants at the top of your file
const RECORDS_PER_PAGE = 20;
let currentLecturerPage = 1;

function openLecturerTab(evt, tabName) {
    const tabContent = document.getElementsByClassName("tab-content");
    const tabButtons = document.getElementsByClassName("tab-button");
    
    // Hide all tab content
    Array.from(tabContent).forEach(tab => {
        tab.style.display = "none";
    });
    
    // Remove active class from all buttons
    Array.from(tabButtons).forEach(button => {
        button.className = button.className.replace(" active", "");
    });
    
    // Show selected tab and activate button
    document.getElementById(tabName).style.display = "block";
    evt.currentTarget.className += " active";

    // Store current tab in session via AJAX
    fetch('/set_lecturerspage_tab', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ lecturerspage_current_tab: tabName })
    });
}

function setupTableSearch() {
    const searchInput = document.querySelector('.table-search[data-table="lecturersTable"]');
    const table = document.getElementById('lecturersTable');

    if (!searchInput || !table) return;

    searchInput.addEventListener('input', function () {
        const searchTerm = this.value.toLowerCase();
        const rows = table.querySelectorAll('tbody tr');

        rows.forEach(row => {
            const text = Array.from(row.querySelectorAll('td'))
                .slice(1) // Skip checkbox column
                .map(cell => cell.textContent.trim())
                .join(' ')
                .toLowerCase();

            row.dataset.searchMatch = text.includes(searchTerm) ? 'true' : 'false';
        });

        currentLecturerPage = 1;
        updateTable(1);
    });
}

// Handle select all checkbox
document.querySelector('.select-all[data-table="lecturersTable"]').addEventListener('change', function() {
    const table = document.getElementById('lecturersTable');
    const checkboxes = table.querySelectorAll('.record-checkbox');
    checkboxes.forEach(box => {
        box.checked = this.checked;
    });
});

// Handle delete selected
document.querySelector('.delete-selected[data-table="lecturers"]').addEventListener('click', async function() {
    const table = document.getElementById('lecturers');
    const selectedBoxes = table.querySelectorAll('.record-checkbox:checked');

    if (selectedBoxes.length === 0) {
        alert('Please select record(s) to delete');
        return;
    }

    if (!confirm('Are you sure you want to delete the selected record(s)?')) {
        return;
    }

    const selectedIds = Array.from(selectedBoxes).map(box => box.dataset.id);

    try {
        const response = await fetch('/api/delete_record/lecturers', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ ids: selectedIds })
        });

        if (response.ok) {
            selectedBoxes.forEach(box => box.closest('tr').remove());
            alert('Records deleted successfully');
            window.location.reload(true);
        } else {
            alert('Failed to delete records');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred while deleting records');
    }
});

document.querySelector('.create-record[data-table="lecturers"]').addEventListener('click', function() {
    const modal = document.getElementById('editModal');
    const form = document.getElementById('editForm');

    form.dataset.table = 'lecturers';
    form.dataset.mode = 'create';

    createFormFields(form);
    
    modal.style.display = 'block';
});

async function editRecord(id) {
    try {
        const response = await fetch(`/get_record/lecturers/${id}`);
        const data = await response.json();

        if (!data.success) {
            console.error('Failed to get record data:', data);
            alert('Error: ' + (data.message || 'Failed to load record data'));
            return;
        }

        const modal = document.getElementById('editModal');
        const form = document.getElementById('editForm');

        form.dataset.table = 'lecturers';
        form.dataset.id = id;
        form.dataset.mode = 'edit';

        // Wait for form fields (and any fetched data) to be created before continuing
        await createFormFields(form);

        // Populate fields with the fetched data
        for (const [key, value] of Object.entries(data.record)) {
            const input = form.querySelector(`[name="${key}"]`);
            console.log(`Setting ${key} to ${value}, input found:`, !!input);

            if (input) {
                if (input.tagName === 'SELECT') {
                    Array.from(input.options).forEach(option => {
                        option.selected = option.value === String(value);
                    });
                } else {
                    input.value = value ?? '';
                }

                input.dispatchEvent(new Event('change'));
            }
        }

        modal.style.display = 'block';

    } catch (error) {
        console.error('Error in editRecord:', error);
        alert('Error loading record: ' + error.message);
    }
}

function closeEditModal() {
    const modal = document.getElementById('editModal');
    modal.style.display = 'none';
}

// Update the form submission event listener
document.getElementById('editForm').addEventListener('submit', async function(e) {
    e.preventDefault();

    const mode = this.dataset.mode;
    const originalId = this.dataset.id;
    const formData = {};

    // Collect form data
    this.querySelectorAll('input, select').forEach(input => {
        formData[input.name] = input.value;
    });

    // Validate form data
    const validationErrors = validateFormData('lecturers', formData);
    if (validationErrors.length > 0) {
        alert('Validation error(s):\n' + validationErrors.join('\n'));
        return;
    }

    if (mode === 'create') {
        try {
            const response = await fetch('/api/create_record/lecturers', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });

            const data = await response.json();
            if (data.success) {
                alert('Lecturer created successfully');
                window.location.reload(true);
            } else {
                alert(data.error || 'Failed to create lecturer');
            }
        } catch (error) {
            alert('Error creating lecturer: ' + error.message);
        }
        return;
    }

    // Edit mode
    if (mode === 'edit') {
        const primaryKeyField = 'ic_no';
        const primaryKeyValue = formData[primaryKeyField];

        // Check if IC number changed and already exists
        const originalRecord = await fetch(`/get_record/lecturers/${originalId}`).then(r => r.json());
        if (originalRecord.success && originalRecord.record[primaryKeyField] !== primaryKeyValue) {
            const exists = await checkExistingRecord('lecturers', primaryKeyField, primaryKeyValue);
            if (exists) {
                alert(`A lecturer with this IC number already exists.`);
                return;
            }
        }

        formData.id = originalId;

        fetch(`/api/update_record/lecturers/${originalId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert(data.message || 'Lecturer updated successfully');
                window.location.reload(true);
            } else {
                alert('Error: ' + (data.message || 'Failed to update lecturer'));
            }
        })
        .catch(error => {
            alert('Error: ' + error.message);
        });
    }
});

// Helper function to create a select element
function createSelect(name, options, multiple = false) {
    const select = document.createElement('select');
    select.name = name;
    select.required = true;
    select.multiple = multiple;
    
    options.forEach(opt => {
        const option = document.createElement('option');
        if (typeof opt === 'object') {
            option.value = opt.value;
            option.textContent = opt.label;
        } else {
            option.value = opt;
            option.textContent = opt;
        }
        select.appendChild(option);
    });
    
    return select;
}

async function getDepartments() {
    try {
        const response = await fetch('/get_departments');
        const data = await response.json();
        if (data.success) {
            return data.departments.map(dept => ({
                value: dept.department_code,
                label: `${dept.department_code} - ${dept.department_name}`
            }));
        }
        return [];
    } catch (error) {
        console.error('Error fetching departments:', error);
        return [];
    }
}

async function getHops() {
    try {
        const response = await fetch('/get_hops');
        const data = await response.json();
        if (data.success) {
            return data.hops.map(hop => ({
                value: hop.name,
                label: `${hop.name}`
            }));
        }
        return [];
    } catch (error) {
        console.error('Error fetching heads of programme:', error);
        return [];
    }
}

async function getDeans() {
    try {
        const response = await fetch('/get_deans');
        const data = await response.json();
        if (data.success) {
            return data.deans.map(dean => ({
                value: dean.name,
                label: `${dean.name}`
            }));
        }
        return [];
    } catch (error) {
        console.error('Error fetching deans:', error);
        return [];
    }
}

function createFormFields(form) {
    return new Promise(async (resolve) => {
        const formFields = form.querySelector('#editFormFields');
        formFields.innerHTML = '';

        const fields = ['name', 'email', 'ic_no', 'level', 'department_code', 'hop_id', 'dean_id'];
        const departments = await getDepartments();

        fields.forEach(key => {
            const formGroup = document.createElement('div');
            formGroup.className = 'form-group';

            const label = document.createElement('label');
            label.textContent = key
                .replace(/_/g, ' ')                          // replace underscores with spaces
                .replace(/\b\w/g, c => c.toUpperCase())      // capitalize each word
                .replace(/\bId\b/g, '')                     // remove the word 'Id' by replacing it with an empty string
                .trim()                                     // remove any extra spaces from the end
                + ':';                                      // add colon at the end

            let input;

            if (key === 'level') {
                input = createSelect(key, ['I', 'II', 'III']);
            } 
            else if (key === 'department_code') {
                input = createSelect(key, departments);
            }
            else if (key === 'hop_id') {
                input = createSelect(key, hops);
            } 
            else if (key === 'dean_id') {
                input = createSelect(key, deans);
            } 
            else {
                input = document.createElement('input');
                input.type = 'text';
                input.name = key;
                input.required = true;
            }

            formGroup.appendChild(label);
            formGroup.appendChild(input);
            formFields.appendChild(formGroup);
        });

        resolve();
    });
}

// Add these validation functions at the top of the file
const validationRules = {
    // Function to check for invalid special characters in text
    hasInvalidSpecialChars: (text) => {
        // Allow letters, numbers, spaces, dots, commas, hyphens, and parentheses
        const invalidCharsRegex = /[^a-zA-Z0-9\s.,\-()]/;
        return invalidCharsRegex.test(text);
    },

    // Function to validate that email ends with @newinti.edu.my
    isValidEmail: (email) => {
        const emailRegex = /^[a-zA-Z0-9._%+-]+@newinti\.edu\.my$/;
        return emailRegex.test(email);
    },

    // Function to validate IC number (12 digits only)
    isValidICNumber: (ic) => {
        return /^\d{12}$/.test(ic);
    }
};

// Add this validation function
function validateFormData(table, formData) {
    const errors = [];

    if (table === 'lecturers') {
        // Validate lecturer name
        if (validationRules.hasInvalidSpecialChars(formData.name)) {
            errors.push("Lecturer name contains invalid special characters");
        }

        if (!validationRules.isValidEmail(formData.email)) {
            errors.push("Email must end with @newinti.edu.my");
        }
        
        if (!validationRules.isValidICNumber(formData.ic_no)) {
            errors.push("IC number must contain exactly 12 digits");
        }

        if (!validationRules.hasInvalidSpecialChars(formData.hop)) {
            errors.push("HOP name contains invalid special characters");
        }

        if (!validationRules.hasInvalidSpecialChars(formData.dean)) {
            errors.push("Dean name contains invalid special characters");
        }
    }
    return errors;
}

// Add this function to handle pagination
function updateTable(page) {
    const tableElement = document.getElementById('lecturersTable');
    if (!tableElement) return;

    const rows = Array.from(tableElement.querySelectorAll('tbody tr'));
    // Only consider rows that match the search
    const filteredRows = rows.filter(row => row.dataset.searchMatch !== 'false');
    const totalPages = Math.ceil(filteredRows.length / RECORDS_PER_PAGE);
    
    // Update page numbers
    const container = tableElement.closest('.tab-content');
    const currentPageSpan = container.querySelector('.current-page');
    const totalPagesSpan = container.querySelector('.total-pages');
    
    if (currentPageSpan) currentPageSpan.textContent = page;
    if (totalPagesSpan) totalPagesSpan.textContent = totalPages;
    
    // First hide all rows
    rows.forEach(row => row.style.display = 'none');
    
    // Then show only the filtered rows for the current page
    filteredRows.slice((page - 1) * RECORDS_PER_PAGE, page * RECORDS_PER_PAGE)
        .forEach(row => row.style.display = '');
    
    // Update pagination buttons
    const prevBtn = container.querySelector('.prev-btn');
    const nextBtn = container.querySelector('.next-btn');
    if (prevBtn) prevBtn.disabled = page === 1;
    if (nextBtn) nextBtn.disabled = page === totalPages || totalPages === 0;
}
