document.addEventListener('DOMContentLoaded', function () {
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
            'practicalWeeks', 'blendedWeeks', 'lectureHours', 
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
                        <label for="subjectLevel${count}">Program Level:</label>
                        <select id="subjectLevel${count}" name="subjectLevel${count}" required>
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
                        <label for="blendedWeeks${count}">E-Learning Weeks:</label>
                        <input type="number" id="blendedWeeks${count}" name="blendedWeeks${count}" readonly min="1" required />
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
                        <label for="startDate${count}">Teaching Period Start:</label>
                        <input type="date" id="startDate${count}" name="startDate${count}" required />
                    </div>
                    <div class="form-group">
                        <label for="endDate${count}">Teaching Period End:</label>
                        <input type="date" id="endDate${count}" name="endDate${count}" required />
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
        const subjectLevelField = document.getElementById(`subjectLevel${count}`);
        const subjectCodeField = document.getElementById(`subjectCode${count}`);
        
        // Listen for subject level changes
        subjectLevelField.addEventListener('change', function() {
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
                            subjectCodeField.innerHTML = '<option value="">No subject available</option>';
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
        
        // Show loading overlay
        document.getElementById("loadingOverlay").style.display = "flex";

        const formData = new FormData();
        const lecturerSelect = document.getElementById('lecturerName');
        const selectedLecturerId = lecturerSelect.value;
        
        formData.append('lecturer_id', selectedLecturerId);
        formData.append('name', lecturerSelect.options[lecturerSelect.selectedIndex].text);       
        formData.append('school_centre', document.getElementById('schoolCentre').value);
        formData.append('designation',  document.getElementById('designation').value);
        formData.append('ic_number', document.getElementById('icNumber').value);

        // Add course details
        const forms = document.querySelectorAll('.course-form');
        forms.forEach((form, index) => {
            const count = index + 1;
            formData.append(`subjectLevel${count}`, document.getElementById(`subjectLevel${count}`).value);
            formData.append(`subjectCode${count}`, document.getElementById(`subjectCode${count}`).value);
            formData.append(`subjectTitle${count}`, document.getElementById(`subjectTitle${count}`).value);
            formData.append(`lectureWeeks${count}`, document.getElementById(`lectureWeeks${count}`).value);
            formData.append(`tutorialWeeks${count}`, document.getElementById(`tutorialWeeks${count}`).value);
            formData.append(`practicalWeeks${count}`, document.getElementById(`practicalWeeks${count}`).value);
            formData.append(`blendedWeeks${count}`, document.getElementById(`blendedWeeks${count}`).value);
            formData.append(`startDate${count}`, document.getElementById(`startDate${count}`).value);
            formData.append(`endDate${count}`, document.getElementById(`endDate${count}`).value);
            formData.append(`hourlyRate${count}`, document.getElementById(`hourlyRate${count}`).value);  // Add this line
            formData.append(`lectureHours${count}`, document.getElementById(`lectureHours${count}`).value || '0');
            formData.append(`tutorialHours${count}`, document.getElementById(`tutorialHours${count}`).value || '0');
            formData.append(`practicalHours${count}`, document.getElementById(`practicalHours${count}`).value || '0');
            formData.append(`blendedHours${count}`, document.getElementById(`blendedHours${count}`).value || '0');
        });

        // Send form data to server
        fetch('/poConversionResult', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById("loadingOverlay").style.display = "none";
            if (data.success) {
                window.location.href = `/poConversionResultPage`;
            } else {
                alert('Error: ' + (data.error || 'Unknown error occurred'));
            }
        })
        .catch(error => {
            document.getElementById("loadingOverlay").style.display = "none";
            console.error('Error:', error);
            alert('Error submitting form: ' + error.message);
        });
    });  
});

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
                    document.getElementById(`blendedWeeks${count}`).value = subject.blended_weeks ?? '';
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
        const startDate = document.getElementById(`startDate${formNumber}`).value;
        const endDate = document.getElementById(`endDate${formNumber}`).value;
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

// When subject level changes, update subject options
document.querySelectorAll('[id^="subjectLevel"]').forEach(select => {
    select.addEventListener('change', function() {
        const formNumber = this.id.replace('subjectLevel', '');
        updateSubjectOptions(this.value, formNumber);
    });
});

// Update subject options based on subject level
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

// Add these constants at the top of your file
const RECORDS_PER_PAGE = 20;
let currentPages = {
    'lecturers': 1,
    'lecturersFile': 1,
    'approvals': 1
};

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


// Handle select all checkbox
document.querySelectorAll('.select-all').forEach(checkbox => {
    checkbox.addEventListener('change', function() {
        const tableId = this.dataset.table;
        const table = document.getElementById(tableId);
        const checkboxes = table.querySelectorAll('.record-checkbox');
        checkboxes.forEach(box => {
            box.checked = this.checked;
        });
    });
});

// Handle delete selected
document.querySelectorAll('.delete-selected').forEach(button => {
    button.addEventListener('click', async function() {
        const tableType = this.dataset.table;
        const table = document.getElementById(tableType);
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
            const response = await fetch(`/api/delete_record/${tableType}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ ids: selectedIds })
            });

            if (response.ok) {
                // Remove deleted rows from the table
                selectedBoxes.forEach(box => box.closest('tr').remove());
                alert('Record(s) deleted successfully');
                window.location.reload(true);
            } else {
                alert('Failed to delete record(s)');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred while deleting record(s)');
        }
    });
});

function setupTableSearch() {
    document.querySelectorAll('.table-search').forEach(searchInput => {
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const tableId = this.dataset.table;
            const table = document.getElementById(tableId);
            
            if (!table) {
                console.error(`Table with id ${tableId} not found`);
                return;
            }
            
            const rows = table.querySelectorAll('tbody tr');
            
            rows.forEach(row => {
                let text = Array.from(row.querySelectorAll('td'))
                    .slice(1)
                    .map(cell => cell.textContent.trim())
                    .join(' ')
                    .toLowerCase();
                
                // Set a data attribute for search matching
                row.dataset.searchMatch = text.includes(searchTerm) ? 'true' : 'false';
            });

            // Reset to first page and update the table
            const tableType = tableId.replace('Table', '');
            currentPages[tableType] = 1;
            updateTable(tableType, 1);
        });
    });
}

// Add click event listeners for create buttons
document.querySelectorAll('.create-record').forEach(button => {
    button.addEventListener('click', function() {
        const tableType = this.dataset.table;  
        createRecord(tableType); 
    });
});

function createRecord(table) {
    const modal = document.getElementById('editModal');
    const form = document.getElementById('editForm');
    
    // Set form mode for create
    form.dataset.table = table;
    form.dataset.mode = 'create';
    
    // Use the shared helper function to create fields
    createFormFields(table, form);
    
    modal.style.display = 'block';
}

async function editRecord(table, id) {
    try {
        const response = await fetch(`/get_record/${table}/${id}`);
        const data = await response.json();

        if (data.success) {
            const modal = document.getElementById('editModal');
            const form = document.getElementById('editForm');

            form.dataset.table = table;
            form.dataset.id = id;
            form.dataset.mode = 'edit';

            // Wait for form fields (and any fetched data) to be created before continuing
            await createFormFields(table, form);

            // Now it's safe to populate the fields
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
        } else {
            console.error('Failed to get record data:', data);
            alert('Error: ' + (data.message || 'Failed to load record data'));
        }
    } catch (error) {
        console.error('Error in editRecord:', error);
        alert('Error loading record: ' + error.message);
    }
}

// Add this function to check for existing records
async function checkExistingRecord(table, value) {
    try {
        const response = await fetch(`/check_record_exists/${table}/${value}`);
        const data = await response.json();
        return data.exists;
    } catch (error) {
        console.error('Error checking record:', error);
        return false;
    }
}

function closeEditModal() {
    const modal = document.getElementById('editModal');
    modal.style.display = 'none';
}

// Update the form submission event listener
document.getElementById('editForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    const table = this.dataset.table;
    const mode = this.dataset.mode;
    const formData = new FormData();
    const originalId = this.dataset.id;  // Store the original record ID
    
    // Collect form data
    const inputs = this.querySelectorAll('input, select');

    inputs.forEach(input => {
        if (input.type === 'file') {
            const files = input.files;
            for (let file of files) {
                formData.append(input.name, file);
            }
        } else {
            formData.append(input.name, input.value);
        }
    });

    // Validate form data
    const validationErrors = await validateFormData(formData);
    if (validationErrors.length > 0) {
        alert('Validation error(s):\n' + validationErrors.join('\n'));
        return;
    }

    if (mode === 'create') {
        try {
            // Original code for other tables
            const response = await fetch(`/api/create_record/${table}`, {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            if (data.success) {
                alert('Record created successfully');
                window.location.reload(true);
            } else {
                alert(data.error || 'Failed to create record');
            }
        } catch (error) {
            alert('Error creating record: ' + error.message);
        }
        return;
    }

    // Check for duplicate primary keys when editing
    if (mode === 'edit') {
        let exists = false;
        let primaryKeyField = 'ic_no';
        let primaryKeyValue = formData.ic_no;

        // Only check for duplicates if the primary key has been changed
        const originalRecord = await fetch(`/get_record/${table}/${originalId}`).then(r => r.json());
        if (originalRecord.success && originalRecord.record[primaryKeyField] !== primaryKeyValue) {
            exists = await checkExistingRecord(table, primaryKeyValue);
            
            if (exists) {
                alert(`Cannot update record: A lecturer with this ic no already exists.`);
                return;
            }
        }

        formData.id = originalId;

        fetch(`/api/update_record/${table}/${originalId}`, {
            method: 'PUT',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert(data.message || 'Record updated successfully');
                window.location.reload(true);
            } else {
                alert('Error: ' + (data.message || 'Failed to update record'));
            }
        })
        .catch(error => {
            alert('Error: ' + error.message);
        });
    }
});

// Helper function to create a select element
function createSelect(name, options) {
    const select = document.createElement('select');
    select.name = name;
    select.required = true;

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

function createFormFields(table, form) {
    return new Promise(async (resolve) => {
        const formFields = form.querySelector('#editFormFields');
        formFields.innerHTML = '';

        const fields = ['name', 'email', 'ic_no', 'level', 'department_code', 'upload_file'];
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
            else if (key === 'upload_file') {
                input = document.createElement('input');
                input.type = 'file';
                input.name = key;
                input.accept = 'application/pdf';
                input.multiple = true;
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
function validateFormData(formData) {
    const errors = [];

    if (validationRules.hasInvalidSpecialChars(formData.get('name'))) {
        errors.push("Lecturer name contains invalid special characters");
    }

    if (!validationRules.isValidEmail(formData.get('email'))) {
        errors.push("Email must end with @newinti.edu.my");
    }
    
    if (!validationRules.isValidICNumber(formData.get('ic_no'))) {
        errors.push("IC number must contain exactly 12 digits");
    }
    
    return errors;
}

// Add this function to handle pagination
function updateTable(tableType, page) {
    const tableElement = document.getElementById(tableType + 'Table');
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

async function checkApprovalStatusAndToggleButton(approvalId) {
    try {
        const response = await fetch(`/check_requisition_status/${approvalId}`);
        if (!response.ok) throw new Error('Network response was not ok');

        const data = await response.json(); // e.g., { status: "some status string" }
        const approveBtn = document.getElementById(`approve-btn-${approvalId}`);
        const voidBtn = document.getElementById(`void-btn-${approvalId}`);

        if (approveBtn) {
            // Disable approve button if status does not contain "Program Officer"
            if (!data.status.includes("Pending Acknowledgement by PO")) {
                approveBtn.disabled = true;
                approveBtn.style.cursor = 'not-allowed';
                approveBtn.textContent = 'Approved';
                approveBtn.style.backgroundColor = 'grey';
            }
        }

        if (voidBtn) {
            // Disable void button if status contains "Rejected"
            if (data.status.includes("Rejected") || data.status.includes("Voided")) {
                voidBtn.disabled = true;
                voidBtn.style.cursor = 'not-allowed';
                voidBtn.style.backgroundColor = 'grey';
            }
        }

    } catch (error) {
        console.error('Error checking approval status:', error);
    }
}

function openSignatureModal(id) {
    selectedApprovalId = id;

    // Close void modal if open
    const voidModal = document.getElementById("void-modal");
    if (voidModal.style.display === "block") {
        voidModal.style.display = "none";
    }

    const modal = document.getElementById("signature-modal");
    modal.style.display = "block";

    const canvas = document.getElementById("signature-pad");
    signaturePad = new SignaturePad(canvas);
}

function closeSignatureModal() {
    document.getElementById("signature-modal").style.display = "none";
    if (signaturePad) {
        signaturePad.clear();
    }
}

function clearSignature() {
    if (signaturePad) {
        signaturePad.clear();
    }
}

function submitSignature() {
    if (!signaturePad || signaturePad.isEmpty()) {
        alert("Please provide a signature before submitting.");
        return;
    }

    const canvas = document.getElementById("signature-pad");
    const dataURL = canvas.toDataURL();

    // Show loading overlay before starting fetch
    document.getElementById("loadingOverlay").style.display = "flex";

    fetch(`/api/po_review_requisition/${selectedApprovalId}`, {
        method: "POST",
        body: JSON.stringify({ image: dataURL }),
        headers: { "Content-Type": "application/json" }
    })
    .then(response => {
        // Parse JSON response first, then hide loading
        return response.json().then(data => {
            document.getElementById("loadingOverlay").style.display = "none";
            if (!data.success) throw new Error(data.error || "Failed to complete approval");
            return data;
        });
    })
    .then(() => {
        alert("Approval process started successfully.");
        closeSignatureModal();  // Close modal only after success
        location.reload();
    })
    .catch(error => {
        document.getElementById("loadingOverlay").style.display = "none";
        console.error("Error during approval:", error);
        alert("An error occurred during approval: " + error.message);
    });
}

function openVoidModal(id) {
    selectedVoidId = id;

    // Close signature modal if open
    const signatureModal = document.getElementById("signature-modal");
    if (signatureModal.style.display === "block") {
        signatureModal.style.display = "none";
        if (signaturePad) {
            signaturePad.clear();
        }
    }

    const modal = document.getElementById("void-modal");
    modal.style.display = "block";
}

function closeVoidModal() {
    document.getElementById("void-modal").style.display = "none";
    clearVoidReason();
}

function clearVoidReason() {
    const textarea = document.getElementById("void-reason");
    if (textarea) {
        textarea.value = "";
    }
}

function submitVoidReason() {
    const reason = document.getElementById("void-reason").value.trim();

    if (!reason) {
        alert("Please provide a reason for voiding.");
        return;
    }

    // Show loading overlay
    document.getElementById("loadingOverlay").style.display = "flex";

    fetch(`/api/void_requisition/${selectedVoidId}`, {
        method: "POST",
        body: JSON.stringify({ reason }),
        headers: { "Content-Type": "application/json" }
    })
    .then(response => {
        return response.json().then(data => {
            document.getElementById("loadingOverlay").style.display = "none";
            if (!data.success) throw new Error(data.error || "Failed to void requisition");
            return data;
        });
    })
    .then(() => {
        alert("Requisition has been voided successfully.");
        closeVoidModal();
        location.reload();
    })
    .catch(error => {
        document.getElementById("loadingOverlay").style.display = "none";
        console.error("Error during voiding:", error);
        alert("An error occurred while voiding the requisition: " + error.message);
    });
}
