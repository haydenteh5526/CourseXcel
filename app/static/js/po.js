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

    function todayLocalISO() {
        const d = new Date();
        const y = d.getFullYear();
        const m = String(d.getMonth() + 1).padStart(2, '0');
        const day = String(d.getDate()).padStart(2, '0');
        return `${y}-${m}-${day}`;   // e.g., 2025-08-26
    }

    function addCourseForm(count) {
        const todayStr = todayLocalISO();

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
                        <input type="date" id="startDate${count}" name="startDate${count}" min="${todayStr}" required />
                    </div>
                    <div class="form-group">
                        <label for="endDate${count}">Teaching Period End:</label>
                        <input type="date" id="endDate${count}" name="endDate${count}" min="${todayStr}" required />
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label for="hourlyRate${count}">Rate per hour (RM):</label>
                        <select id="hourlyRate${count}" name="hourlyRate${count}" required>
                            <option value="">Select Rate</option>
                        </select>
                    </div>
                </div>
            </div>
        `;
        courseFormsContainer.insertAdjacentHTML('beforeend', courseFormHtml);
        attachFormListeners(count);
        populateRateOptions(count);
    }

    function updateCourseButtons() {
        if (courseCount >= 4) {
            addCourseBtn.textContent = "Maximum Reached (4)";
            addCourseBtn.disabled = true;
        } else {
            addCourseBtn.textContent = `Add Course Details (${courseCount + 1})`;
            addCourseBtn.disabled = false;
        }
    }

    // Initialize with one course form by default
    addCourseForm(courseCount);
    updateCourseButtons();

    addCourseBtn.addEventListener('click', function () {
        if (courseCount >= 4) {
            alert("You can only add up to 4 courses.");
            return;
        }
        courseCount++;
        addCourseForm(courseCount);
        updateCourseButtons();
    });

    // Modify the submit button event listener
    submitAllBtn.addEventListener('click', async function(e) {
        e.preventDefault();
        
        if (!validateLecturerDetails() || !validateRequiredFields()) {
            return;
        }

        const lecturerId = document.getElementById('lecturerName').value;

        // Fetch already assigned subject codes for the lecturer
        const response = await fetch(`/get_assigned_subject/${lecturerId}`);
        const result = await response.json();

        if (!result.success) {
            alert("Failed to fetch assigned subjects.");
            return;
        }

        const assignedCodes = result.subject_codes;

        // Collect subject codes from the current form
        const forms = document.querySelectorAll('.course-form');
        const duplicates = [];
        const currentCodes = [];

        forms.forEach((form, index) => {
            const count = index + 1;
            const code = document.getElementById(`subjectCode${count}`).value.trim();
            if (assignedCodes.includes(code)) {
                duplicates.push(code);
            }
            currentCodes.push(code);
        });

        // If duplicates found, block submission
        if (duplicates.length > 0) {
            alert(`The following subject(s) already assigned to this lecturer:\n${duplicates.join(', ')}`);
            return;
        }
        
        // Proceed with form submission
        document.getElementById("loadingOverlay").style.display = "flex";

        const formData = new FormData();
        formData.append('department_code', document.getElementById('departmentCode').value);
        formData.append('lecturer_id', lecturerId);
        formData.append('name', document.getElementById('lecturerName').selectedOptions[0].text);
        formData.append('designation',  document.getElementById('designation').value);
        formData.append('ic_number', document.getElementById('icNumber').value);

        // Add course details
        forms.forEach((form, index) => {
            const count = index + 1;
            formData.append(`subjectLevel${count}`, document.getElementById(`subjectLevel${count}`).value);
            formData.append(`subjectCode${count}`, document.getElementById(`subjectCode${count}`).value);
            formData.append(`subjectTitle${count}`, document.getElementById(`subjectTitle${count}`).value);
            formData.append(`lectureWeeks${count}`, document.getElementById(`lectureWeeks${count}`).value || '0');
            formData.append(`tutorialWeeks${count}`, document.getElementById(`tutorialWeeks${count}`).value || '0');
            formData.append(`practicalWeeks${count}`, document.getElementById(`practicalWeeks${count}`).value || '0');
            formData.append(`blendedWeeks${count}`, document.getElementById(`blendedWeeks${count}`).value || '0'); 
            formData.append(`startDate${count}`, document.getElementById(`startDate${count}`).value);
            formData.append(`endDate${count}`, document.getElementById(`endDate${count}`).value);
            formData.append(`hourlyRate${count}`, document.getElementById(`hourlyRate${count}`).value);  
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
            alert('Error submitting form: ' + error.message);
        });
    });  
});

// Function to remove the last added course form
function removeCourseForm(count) {
    const formToRemove = document.getElementById(`courseForm${count}`);

    if (formToRemove) {
        if (courseCount <= 1) {
            alert("At least one course is required.");
            return;
        }
        formToRemove.remove();
        courseCount--;
        reorderForms();
        updateCourseButtons();
    }
}

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

function attachFormListeners(count) {
    const startDate = document.getElementById(`startDate${count}`);
    const endDate   = document.getElementById(`endDate${count}`);
    const today = new Date().toLocaleDateString('en-CA');

    if (startDate && endDate) {
        // Ensure min attributes exist
        if (!startDate.min) startDate.min = today;
        if (!endDate.min) endDate.min = today;

        const clampToMin = (el) => {
            if (el.value && el.min && el.value < el.min) el.value = el.min;
        };

        // Keep end >= start
        const syncEndMin = () => {
            endDate.min = startDate.value || today;
            clampToMin(endDate);
        };

        // Guard manual typing & picker selection
        startDate.addEventListener('input',  () => { clampToMin(startDate); syncEndMin(); });
        startDate.addEventListener('change', syncEndMin);
        endDate  .addEventListener('input',  () => clampToMin(endDate));
        endDate  .addEventListener('change', () => clampToMin(endDate));

        // Initial sync
        syncEndMin();
    }

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

function populateRateOptions(count) {
    fetch('/get_rate_amounts')
        .then(response => response.json())
        .then(data => {
            const rateSelect = document.getElementById(`hourlyRate${count}`);
            if (data.success && data.rates.length > 0) {
                data.rates.forEach(rate => {
                    const option = document.createElement('option');
                    option.value = rate.amount;
                    option.textContent = rate.amount;
                    rateSelect.appendChild(option);
                });
            } else {
                rateSelect.innerHTML = '<option value="">No rates available</option>';
            }
        })
        .catch(error => {
            console.error('Error fetching rates:', error);
            const rateSelect = document.getElementById(`hourlyRate${count}`);
            rateSelect.innerHTML = '<option value="">Error loading rates</option>';
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

// Validation function
function validateLecturerDetails() {
    const departmentCode = document.getElementById('departmentCode').value;
    const lecturerSelect = document.getElementById('lecturerName');

    if (!departmentCode) {
        alert('Please select a School/Centre');
        return false;
    }

    if (!lecturerSelect.value) {
        alert('Please select a lecturer');
        return false;
    }

    return true;
}

// Validation function
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

// Move editableFields to the global scope (outside any function)
const editableFields = {
    'subjects': [
        'subject_code',
        'subject_title',
        'subject_level',
        'head_id',
        'lecture_hours',
        'tutorial_hours',
        'practical_hours',
        'blended_hours',
        'lecture_weeks',
        'tutorial_weeks',
        'practical_weeks',
        'blended_weeks'
    ],
    'lecturers': ['name', 'email', , 'ic_no', 'level', 'department_id', 'upload_file']
};

// Add these constants at the top of your file
const RECORDS_PER_PAGE = 20;
let currentPages = {
    'subjects': 1,
    'lecturers': 1,
    'lecturersFile': 1,
    'requisitionApprovals': 1,
    'claimApprovals': 1
};

function initTableFiltersWithSearch(statusSelectorId, searchInputId) {
    const statusFilter = document.getElementById(statusSelectorId);
    const searchInput = document.getElementById(searchInputId);

    if (!statusFilter || !searchInput) return;

    const tableId = searchInput.dataset.table; 
    const rows = document.querySelectorAll(`#${tableId} tbody tr`);

    function applyFilters() {
        const selectedStatus = statusFilter.value.toLowerCase();
        const searchTerm = searchInput.value.toLowerCase();

        rows.forEach(row => {
            const status = row.getAttribute("data-status")?.toLowerCase() || '';
            const text = row.textContent.toLowerCase();

            const matchStatus = !selectedStatus || status.includes(selectedStatus);
            const matchSearch = !searchTerm || text.includes(searchTerm);

            const shouldShow = matchStatus && matchSearch;
            row.style.display = shouldShow ? "" : "none";
        });
    }

    statusFilter.addEventListener("change", applyFilters);
    searchInput.addEventListener("input", applyFilters);
}

async function checkApprovalStatusAndToggleButton(approvalId) {
    try {
        const response = await fetch(`/check_requisition_status/${approvalId}`);
        if (!response.ok) throw new Error('Network response was not ok');

        const data = await response.json(); // e.g., { status: "some status string" }
        const approveBtn = document.getElementById(`approve-btn-${approvalId}`);
        const voidBtn = document.getElementById(`void-btn-${approvalId}`);

        if (approveBtn) {
            // Disable approve button if status does not contain "PO"
            if (!data.status.includes("Pending Acknowledgement by PO")) {
                approveBtn.disabled = true;
                approveBtn.style.cursor = 'not-allowed';
                approveBtn.textContent = 'Approved';
                approveBtn.style.backgroundColor = 'grey';
            }
        }

        if (voidBtn) {
            // Disable void button if status contains "Rejected"
            if (data.status.includes("Rejected") || data.status.includes("Voided") || data.status.includes("Completed")) {
                voidBtn.disabled = true;
                voidBtn.style.cursor = 'not-allowed';
                voidBtn.style.backgroundColor = 'grey';
            }
        }

    } catch (error) {
        console.error('Error checking approval status:', error);
    }
}

function submitRequisitionSignature() {
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
        window.location.reload(true);
    })
    .catch(error => {
        document.getElementById("loadingOverlay").style.display = "none";
        console.error("Error during approval:", error);
        alert("An error occurred during approval: " + error.message);
    });
}

function submitVoidRequisitionReason() {
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
