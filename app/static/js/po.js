// Global configs
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
    'lecturers': ['name', 'email', 'ic_no', 'level', 'department_id']
};

// Pagination constants
const RECORDS_PER_PAGE = 20;
let currentPages = {
    'subjects': 1,
    'lecturers': 1,
    'requisitionApprovals': 1,        
    'requisitionAttachments': 1,
    'claimApprovals': 1,
    'claimAttachments': 1,
    'claimDetails': 1
};

// Format today as YYYY-MM-DD (local)
function todayLocalISO() {
    const d = new Date();
    const y = d.getFullYear();
    const m = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    return `${y}-${m}-${day}`; // e.g., 2025-08-26
}

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

            // When cleared: reset & lock fields
            if (!selectedValue) {
                designationField.value = '';
                icNumberField.value = '';
                designationField.readOnly = true;
                icNumberField.readOnly = true;
                return;
            }
            
            try {
                console.log("[PO] Fetch initiated:", `/get_lecturer_details/${encodeURIComponent(selectedValue)}`);
                const response = await fetch(`/get_lecturer_details/${selectedValue}`);
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const data = await response.json();
                console.log("[PO] Fetch success response received:", data);

                if (data.success && data.lecturer) {
                    // Auto-populate and lock fields if an existing lecturer
                    designationField.value = data.lecturer.level || '';
                    icNumberField.value = data.lecturer.ic_no || '';
                    designationField.readOnly = true;
                    icNumberField.readOnly = true;
                } else {
                    console.warn("[PO] Lecturer data not found or invalid:", data.message || "No details available.");
                    alert('Error fetching lecturer details: ' + (data.message || 'Unknown error.'));
                    designationField.value = '';
                    icNumberField.value = '';
                }
            } catch (error) {
                console.error("[PO] Error fetching lecturer details:", error);
                alert('Error fetching lecturer details: ' + error.message);
                designationField.value = '';
                icNumberField.value = '';
            }      
        });
    }

    // Remove a course card
    window.removeCourseForm = function(count) {
        const formToRemove = document.getElementById(`courseForm${count}`);
        if (formToRemove) {
            formToRemove.remove();
            courseCount--;
            reorderForms();
            updateCourseButtons();
        }
    }

    // Render a new course form card
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
                        <label for="blendedWeeks${count}">Blended Weeks:</label>
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
        // Wire up freshly added inputs
        attachFormListeners(count);
        populateRateOptions(count);
    }

    // Add/disable Add button depending on count
    function updateCourseButtons() {
        if (courseCount >= 4) {
            addCourseBtn.textContent = "Maximum Reached (4)";
            addCourseBtn.disabled = true;
        } else {
            addCourseBtn.textContent = `Add Course (${courseCount + 1})`;
            addCourseBtn.disabled = false;
        }
    }

    // Initial render with one course card
    addCourseForm(courseCount);
    updateCourseButtons();

    // Click: append another course card
    addCourseBtn.addEventListener('click', function () {
        if (courseCount >= 4) {
            alert("You can only add up to 4 courses.");
            return;
        }
        courseCount++;
        addCourseForm(courseCount);
        updateCourseButtons();
    });

    // Submit all courses for the selected lecturer
    submitAllBtn.addEventListener('click', async function(e) {
        e.preventDefault();

        // Validate lecturer and course blocks before building FormData
        if (!validateLecturerDetails() || !validateRequiredFields()) {
            return;
        }

        // Attachments
        const attachmentsInput = document.getElementById('upload_requisition_attachment');
        const attachments = attachmentsInput.files;

        const forms = document.querySelectorAll('.course-form');
        const lecturerSelect = document.getElementById('lecturerName');
        const lecturerId = lecturerSelect.value;
        const lecturerName = lecturerSelect.selectedOptions[0].text;

        // Fetch existing assigned subjects (with latest end date) for the lecturer
        let latestEndsByCode = {};
        try {
            console.log("[PO] Fetch initiated:", `/get_assigned_subject/${lecturerId}`);
            const response = await fetch(`/get_assigned_subject/${lecturerId}`);
            const result = await response.json();
            
            if (!result.success) {
                console.warn("[PO] Failed to fetch assigned subjects:", result.message);
                alert("Failed to fetch assigned subjects.");
                return;
            }

            // result.assigned: an array of objects: { subject_code, end_date }
            latestEndsByCode = (result.assigned || []).reduce((acc, item) => {
                if (item && item.subject_code) {
                    acc[item.subject_code] = item.end_date || null;
                }
                return acc;
            }, {});
            console.log("[PO] Assigned subjects loaded successfully:", latestEndsByCode);
        } catch (error) {
            console.error("[PO] Error fetching assigned subjects:", error);
            alert("Error fetching assigned subjects: " + error.message);
            return;
        }

        // Compare currently selected codes vs assigned ones with date logic
        const duplicates = [];
        const currentCodes = [];
        forms.forEach((form, index) => {
            const count = index + 1;
            const code = document.getElementById(`subjectCode${count}`).value.trim();
            const startDateStr = document.getElementById(`startDate${count}`).value;

            currentCodes.push(code);

            // If we have a latest end date on record for this code, compare dates
            const latestEndStr = latestEndsByCode[code] || null;

            // Only treat as duplicate if:
            //   - latestEndStr exists AND
            //   - startDate is a valid date AND
            //   - startDate <= latestEnd
            if (latestEndStr) {
                const startTs = Date.parse(startDateStr);
                const endTs = Date.parse(latestEndStr);

                // If either parse fails, be conservative and mark duplicate only if basic code match without valid dates
                if (!Number.isNaN(startTs) && !Number.isNaN(endTs)) {
                    if (startTs <= endTs) {
                        duplicates.push(`${code} (Existing end date: ${latestEndStr})`);
                    }
                } else {
                    // Fallback behavior if dates are malformed: consider it duplicate to be safe
                    duplicates.push(`${code} (date compare unavailable)`);
                }
            }
        });

        // If duplicates found, block submission
        if (duplicates.length > 0) {
            alert(
                `The following subject(s) are already assigned to "${lecturerName}":\n${duplicates.join(', ')}\n\n` + 
                `Please change the teaching period start date.`
            );
            return;
        }

        // Confirm submission
        const confirmSubmission = confirm(
            `You are about to submit ${attachments.length} attachment(s) and ${forms.length} course(s) for "${lecturerName}".\n` +
            "Please double-check all details before submitting, as you may need to void and resubmit if something is wrong.\n\n" +
            "Do you want to proceed?"
        );
        if (!confirmSubmission) {
            return; // User clicked Cancel
        }
        
        // Show loading overlay
        document.getElementById("loadingOverlay").style.display = "flex";

        const formData = new FormData();
        formData.append('department_code', document.getElementById('departmentCode').value);
        formData.append('lecturer_id', lecturerId);
        formData.append('name', lecturerName);
        formData.append('designation',  document.getElementById('designation').value);
        formData.append('ic_number', document.getElementById('icNumber').value);

        // Add each course block values
        forms.forEach((form, index) => {
            const count = index + 1;
            formData.append(`subjectLevel${count}`, document.getElementById(`subjectLevel${count}`).value);
            formData.append(`subjectCode${count}`, document.getElementById(`subjectCode${count}`).value);
            formData.append(`subjectTitle${count}`, document.getElementById(`subjectTitle${count}`).value);
            formData.append(`lectureWeeks${count}`, document.getElementById(`lectureWeeks${count}`).value || '0');
            formData.append(`tutorialWeeks${count}`, document.getElementById(`tutorialWeeks${count}`).value || '0');
            formData.append(`practicalWeeks${count}`, document.getElementById(`practicalWeeks${count}`).value || '0');
            formData.append(`blendedWeeks${count}`, document.getElementById(`blendedWeeks${count}`).value || '0'); 
            formData.append(`lectureHours${count}`, document.getElementById(`lectureHours${count}`).value || '0');
            formData.append(`tutorialHours${count}`, document.getElementById(`tutorialHours${count}`).value || '0');
            formData.append(`practicalHours${count}`, document.getElementById(`practicalHours${count}`).value || '0');
            formData.append(`blendedHours${count}`, document.getElementById(`blendedHours${count}`).value || '0');
            formData.append(`startDate${count}`, document.getElementById(`startDate${count}`).value);
            formData.append(`endDate${count}`, document.getElementById(`endDate${count}`).value);
            formData.append(`hourlyRate${count}`, document.getElementById(`hourlyRate${count}`).value);  
        });

        // Append attachments
        for (let i = 0; i < attachments.length; i++) {
            formData.append('upload_requisition_attachment', attachments[i]);
        }

        // Send form data to server
        console.log("[PO] Fetch initiated:", '/requisitionFormConversionResult');
        fetch('/requisitionFormConversionResult', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            console.log("[PO] Fetch success response received");
            document.getElementById("loadingOverlay").style.display = "none";

            if (data.success) {
                console.log("[PO] Requisition form submitted successfully. Redirecting...");
                window.location.href = `/requisitionFormConversionResultPage`;
            } else {
                console.error("[PO] Requisition submission failed:", data.error || data.message);
                alert('Error: ' + (data.error || 'Unknown error occurred'));
            }
        })
        .catch(error => {
            document.getElementById("loadingOverlay").style.display = "none";
            console.error("[PO] Error occurred during requisition form submission:", error);
            alert('Error submitting form: ' + error.message);
        });
    });  
});

// Remove the last added course form
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

// Reorder the forms after removal
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

// Attach listeners to a specific course block
function attachFormListeners(count) {
    const startDate = document.getElementById(`startDate${count}`);
    const endDate   = document.getElementById(`endDate${count}`);
    const today = new Date().toLocaleDateString('en-CA');

    if (startDate && endDate) {
        // Ensure min attributes exist
        if (!startDate.min) startDate.min = today;
        if (!endDate.min) endDate.min = today;

        // Clamp value to min if user types an earlier date
        const clampToMin = (el) => {
            if (el.value && el.min && el.value < el.min) el.value = el.min;
        };

        // Keep end >= start
        const syncEndMin = () => {
            endDate.min = startDate.value || today;
            clampToMin(endDate);
        };

        startDate.addEventListener('input', () => { clampToMin(startDate); syncEndMin(); });
        startDate.addEventListener('change', syncEndMin);
        endDate.addEventListener('input', () => clampToMin(endDate));
        endDate.addEventListener('change', () => clampToMin(endDate));

        // Initial sync
        syncEndMin();
    }

    // Load subject codes for specific subject level
    const subjectLevelField = document.getElementById(`subjectLevel${count}`);
    const subjectCodeField = document.getElementById(`subjectCode${count}`);
    
    // Listen for subject level changes
    subjectLevelField.addEventListener('change', function() {
        const selectedLevel = this.value;
        if (selectedLevel) {
            console.log("[PO] Fetch initiated:", `/get_subjects_by_level/${encodeURIComponent(selectedLevel)}`);
            fetch(`/get_subjects_by_level/${selectedLevel}`)
                .then(response => response.json())
                .then(data => {                        
                    console.log("[PO] Fetch success response received:", data);

                    if (data.success && data.subjects && data.subjects.length > 0) {
                        subjectCodeField.innerHTML = '<option value="">Select Subject Code</option>';
                        
                        data.subjects.forEach(subject => {
                            const option = document.createElement('option');
                            option.value = subject.subject_code;
                            option.textContent = `${subject.subject_code} - ${subject.subject_title}`;
                            subjectCodeField.appendChild(option);
                        });
                        console.log(`[PO] ${data.subjects.length} subjects loaded successfully for level "${selectedLevel}".`);
                    } else {
                        console.warn("[PO] No subjects available or data empty for selected level.");
                        subjectCodeField.innerHTML = '<option value="">No subject available</option>';
                        clearSubjectFields(count);
                    }
                })
                .catch(error => {
                    console.error("[PO] Error fetching subjects by level:", error);
                    subjectCodeField.innerHTML = '<option value="">Error loading subjects</option>';
                    clearSubjectFields(count);
                    alert("An error occurred while loading subjects. Please try again later.");
                });
        } else {
            console.log("[PO] Subject level cleared — resetting subject code field and clearing details.");
            subjectCodeField.innerHTML = '<option value="">Select Subject Code</option>';
            clearSubjectFields(count);
        }
    });

    // When subject code changes: fetch details & fill read-only fields
    populateSubjectFields(count);
}

// Fill title/hours/weeks after selecting subject code
function populateSubjectFields(count) {
    const subjectSelect = document.getElementById(`subjectCode${count}`);
    if (!subjectSelect) {
        console.warn(`[PO] Subject select element not found for count: ${count}`);
        return;
    }

    subjectSelect.addEventListener('change', function() {
        const selectedSubjectCode = this.value;
        if (!selectedSubjectCode) {
            console.log(`[PO] No subject selected for row ${count}. Clearing fields.`);
            clearSubjectFields(count);
            return;
        }
        
        console.log("[PO] Fetch initiated:", `/get_subject_details/${encodeURIComponent(selectedSubjectCode)}`);
        fetch(`/get_subject_details/${selectedSubjectCode}`)
            .then(response => response.json())
            .then(data => {   
                console.log("[PO] Fetch success response received:", data);                 
                if (data.success && data.subject) {
                    const subject = data.subject;
                    console.log(`[PO] Populating subject fields for ${selectedSubjectCode}.`);

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
                    console.warn(`[PO] No subject data found for ${selectedSubjectCode}. Message: ${data.message || 'N/A'}`);
                    clearSubjectFields(count);
                }
            })
            .catch(error => {
                console.error("[PO] Error fetching subject details:", error);
                clearSubjectFields(count);
                alert("An error occurred while loading subject details. Please try again later.");
            });
    });
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
    console.log("[PO] Fetch initiated:", `/get_subjects_by_level/${level}`);
    fetch(`/get_subjects_by_level/${level}`)
        .then(response => response.json())
        .then(data => {
            console.log("[PO] Fetch success response received");
            const subjectSelect = document.getElementById(`subjectCode${formNumber}`);

            if (data.success) {
                subjectSelect.innerHTML = '<option value="">Select Subject Code</option>';
                
                data.subjects.forEach(subject => {
                    const option = document.createElement('option');
                    option.value = subject.subject_code;
                    option.textContent = `${subject.subject_code} - ${subject.subject_title}`;
                    subjectSelect.appendChild(option);
                });
                console.log(`[PO] ${data.subjects.length} subjects loaded successfully.`);
            } else {
                console.warn("[PO] No subjects available or data invalid for selected level.");
                subjectSelect.innerHTML = '<option value="">No subject available</option>';
            }
        })
        .catch(error => {
            console.error("[PO] Error fetching subjects:", error);
            const subjectSelect = document.getElementById(`subjectCode${formNumber}`);
            if (subjectSelect) {
                subjectSelect.innerHTML = '<option value="">Error loading subjects</option>';
            }
            alert("An error occurred while loading the subject list. Please try again later.");
        });
}

// Populate active rate amounts for a given card
function populateRateOptions(count) {
    console.log("[PO] Fetch initiated:", `/api/get_rate_amounts`);
    fetch('/get_rate_amounts')
        .then(response => response.json())
        .then(data => {
            const rateSelect = document.getElementById(`hourlyRate${count}`);
            if (data.success && data.rates.length > 0) {
                console.log(`[PO] ${data.rates.length} rate options loaded successfully.`);
                rateSelect.innerHTML = '<option value="">Select Hourly Rate</option>';

                data.rates.forEach(rate => {
                    const option = document.createElement('option');
                    option.value = rate.amount;
                    option.textContent = rate.amount;
                    rateSelect.appendChild(option);
                });
            } else {
                console.warn("[PO] No rates available or empty response received.");
                rateSelect.innerHTML = '<option value="">No rates available</option>';
            }
        })
        .catch(error => {
            console.error("[PO] Error fetching rates:", error);
            const rateSelect = document.getElementById(`hourlyRate${count}`);
            if (rateSelect) {
                rateSelect.innerHTML = '<option value="">Error loading rates</option>';
            }
            alert("An error occurred while loading rate options. Please try again later.");
        });
}

// Clear dependent subject fields for a given card
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

// Update form element IDs and labels
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
    const lecturerSelect = document.getElementById('lecturerName').value;

    if (!departmentCode) {
        alert('Please select a School/Centre');
        return false;
    }

    if (!lecturerSelect) {
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
            alert("Please make sure to fill in all required fields.");
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

// Check requisition status and disable/enable buttons accordingly
async function checkApprovalStatusAndToggleButton(approvalId) {
    try {
        console.log("[PO] Fetch initiated:", `/check_requisition_status/${approvalId}`);
        const response = await fetch(`/check_requisition_status/${approvalId}`);
        if (!response.ok) {
            throw new Error(`Network response was not ok (status ${response.status})`);
        }

        const data = await response.json();
        console.log("[PO] Fetch success response received:", data);

        const approveBtn = document.getElementById(`approve-btn-${approvalId}`);
        const voidBtn = document.getElementById(`void-btn-${approvalId}`);

        if (approveBtn) {
            // Disable approve button if status does not contain
            if (!data.status.includes("Pending Acknowledgement by PO")) {
                approveBtn.disabled = true;
                approveBtn.style.cursor = 'not-allowed';
                approveBtn.style.backgroundColor = 'grey';
            }
        }

        if (voidBtn) {
            // Disable void button if status contains
            if (data.status.includes("Rejected") || data.status.includes("Voided") || data.status.includes("Completed")) {
                voidBtn.disabled = true;
                voidBtn.style.cursor = 'not-allowed';
                voidBtn.style.backgroundColor = 'grey';
            }
        }

    } catch (error) {
        console.error("[PO] Error checking approval status:", error);
        alert("An error occurred while checking approval status. Please try again later.");
    }
}

// Submit signature image for approval
function submitRequisitionSignature() {
    // Ensure signaturePad exists and has content
    if (!signaturePad || signaturePad.isEmpty()) {
        alert("Please provide a signature before submitting.");
        return;
    }

    const canvas = document.getElementById("signature-pad");
    const dataURL = canvas.toDataURL();

    // Show loading overlay
    document.getElementById("loadingOverlay").style.display = "flex";
    console.log("[PO] Fetch initiated:", `/api/po_review_requisition/${selectedApprovalId}`);

    fetch(`/api/po_review_requisition/${selectedApprovalId}`, {
        method: "POST",
        body: JSON.stringify({ image: dataURL }),
        headers: { "Content-Type": "application/json" }
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("loadingOverlay").style.display = "none";

        if (!data.success) {
            console.warn("[PO] Requisition signature submission failed:", data.error || "Unknown error");
            throw new Error(data.error || "Failed to complete approval");
        }

        console.log("[PO] Requisition signature submitted successfully:", data);
        alert("Approval process started successfully.");
        closeSignatureModal(); // Close modal only after success
        location.reload();
    })
    .catch(error => {
        document.getElementById("loadingOverlay").style.display = "none";
        console.error("[PO] Error occurred during requisition approval submission:", error);
        alert("An error occurred during approval: " + error.message);
    });
}

// Submit void reason
function submitVoidRequisitionReason() {
    const reason = document.getElementById("void-reason").value.trim();

    if (!reason) {
        alert("Please provide a reason for voiding.");
        return;
    }

    // Show loading overlay
    document.getElementById("loadingOverlay").style.display = "flex";
    console.log("[PO] Fetch initiated:", `/api/void_requisition/${selectedVoidId}`);

    fetch(`/api/void_requisition/${selectedVoidId}`, {
        method: "POST",
        body: JSON.stringify({ reason }),
        headers: { "Content-Type": "application/json" }
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("loadingOverlay").style.display = "none";

        if (!data.success) {
            console.warn("[PO] Void requisition failed:", data.error || "Unknown error");
            throw new Error(data.error || "Failed to void requisition");
        }

        console.log("[PO] Requisition voided successfully:", data);
        alert("Requisition has been voided successfully.");
        closeVoidModal();
        location.reload();
    })
    .catch(error => {
        document.getElementById("loadingOverlay").style.display = "none";
        console.error("[PO] Error occurred during void requisition submission:", error);
        alert("An error occurred while voiding the requisition: " + error.message);
    });
}
