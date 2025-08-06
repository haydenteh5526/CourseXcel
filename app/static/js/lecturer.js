const editableFields = {
    'lecturerAttachments': ['upload_attachment']
};

// Add these constants at the top of your file
const RECORDS_PER_PAGE = 20;
let currentPages = {
    claimDetails: 1,
    lecturerAttachments: 1
};

function openRecordTab(evt, tabName) {
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
    fetch('/set_recordspage_tab', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ recordspage_current_tab: tabName })
    });
}

document.addEventListener('DOMContentLoaded', function () {
    const claimFormsContainer = document.getElementById('claimFormsContainer');
    const addRowBtn = document.getElementById('addRowBtn');
    const doneBtn = document.getElementById('doneBtn');
    let rowCount = 1;

    // Make removeRow function globally accessible
    window.removeRow = function(count) {
        const rowToRemove = document.getElementById(`row${count}`);
        if (rowToRemove) {
            rowToRemove.remove();
            rowCount--;
            reorderRows();
            updateRowButtons();
        }
    }

    function addRow(count) {
        const rowHtml = `
            <div id="row${count}" class="claim-form">
                ${count > 1 ? '<button type="button" class="close-btn" onclick="removeRow(' + count + ')">×</button>' : ''}
                <h3>Claim Details (${count})</h3>
                <div class="claim-form-row">
                    <div class="form-group">
                        <label for="subjectCode${count}">Subject Code:</label>
                        <select id="subjectCode${count}" name="subjectCode${count}" required>
                            <option value="">Select Subject Code</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="date${count}">Date:</label>
                        <input type="date" id="date${count}" name="date${count}" required />
                    </div>
                    <div class="form-group">
                        <label for="lectureHours${count}">Lecture Hours:</label>
                        <select id="lectureHours${count}" name="lectureHours${count}" required>
                            <option value="">Select</option>
                            ${[...Array(10)].map((_, i) => `<option value="${i+1}">${i+1}</option>`).join('')}
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="tutorialHours${count}">Tutorial Hours:</label>
                        <select id="tutorialHours${count}" name="tutorialHours${count}" required>
                            <option value="">Select</option>
                            ${[...Array(10)].map((_, i) => `<option value="${i+1}">${i+1}</option>`).join('')}
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="practicalHours${count}">Practical Hours:</label>
                        <select id="practicalHours${count}" name="practicalHours${count}" required>
                            <option value="">Select</option>
                            ${[...Array(10)].map((_, i) => `<option value="${i+1}">${i+1}</option>`).join('')}
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="blendedHours${count}">Blended Hours:</label>
                        <select id="blendedHours${count}" name="blendedHours${count}" required>
                            <option value="">Select</option>
                            ${[...Array(10)].map((_, i) => `<option value="${i+1}">${i+1}</option>`).join('')}
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="remarks${count}">Remarks:</label>
                        <input type="text" id="remarks${count}" name="remarks${count}" required />
                    </div>
                </div>
                <input type="hidden" id="startDateHidden${count}" />
                <input type="hidden" id="endDateHidden${count}" />
                <input type="hidden" id="unclaimedLectureHidden${count}" />
                <input type="hidden" id="unclaimedTutorialHidden${count}" />
                <input type="hidden" id="unclaimedPracticalHidden${count}" />
                <input type="hidden" id="unclaimedBlendedHidden${count}" />
                <input type="hidden" id="hourlyRateHidden${count}" />
            </div>
        `;
        claimFormsContainer.insertAdjacentHTML('beforeend', rowHtml);
    }

    function updateRowButtons() {
        if (rowCount >= 40) {
            addRowBtn.textContent = "Maximum Reached (40)";
            addRowBtn.disabled = true;
        } else {
            addRowBtn.textContent = `Add Row (${rowCount + 1})`;
            addRowBtn.disabled = false;
        }
    }

    // Initialize with one course form by default
    addRow(rowCount);
    updateRowButtons();

    addRowBtn.addEventListener('click', function () {
        if (rowCount >= 40) {
            alert("You can only add up to 40 claim details.");
            return;
        }
        rowCount++;
        addRow(rowCount);
        updateRowButtons();
    });

    // Modify the done button event listener
    doneBtn.addEventListener('click', async function(e) {
        e.preventDefault();

        // Add subject details validation before proceeding
       if (!validateSubjectDetails() || !validateDateFields() || !validateHoursFields()) {
            return;
        }

        // Show loading overlay
        document.getElementById("loadingOverlay").style.display = "flex";

        const formData = new FormData();
        formData.append('subject_level', document.getElementById('subjectLevel').value);
        formData.append('hourly_rate', document.getElementById('hourlyRateHidden1').value);

        // Add course details
        const forms = document.querySelectorAll('.claim-form');
        forms.forEach((form, index) => {
            const count = index + 1;
            formData.append(`subjectCode${count}`, document.getElementById(`subjectCode${count}`).value);
            formData.append(`date${count}`, document.getElementById(`date${count}`).value);
            formData.append(`lectureHours${count}`, document.getElementById(`lectureHours${count}`).value || '0');
            formData.append(`tutorialHours${count}`, document.getElementById(`tutorialHours${count}`).value || '0');
            formData.append(`practicalHours${count}`, document.getElementById(`practicalHours${count}`).value || '0');
            formData.append(`blendedHours${count}`, document.getElementById(`blendedHours${count}`).value || '0');
            formData.append(`remarks${count}`, document.getElementById(`remarks${count}`).value);
        });

        // Send form data to server
        fetch('/lecturerConversionResult', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById("loadingOverlay").style.display = "none";
            if (data.success) {
                window.location.href = `/lecturerConversionResultPage`;
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
function removeRow(count) {
    const rowToRemove = document.getElementById(`row${count}`);

    if (rowToRemove) {
        if (rowCount <= 1) {
            alert("At least one claim detail is required.");
            return;
        }
        rowToRemove.remove();
        rowCount--;
        reorderRows();
        updateRowButtons();
    }
}

// Add a new function to reorder the forms after removal
function reorderRows() {
    const forms = document.querySelectorAll('.claim-form');
    forms.forEach((form, index) => {
        const newCount = index + 1;
        form.id = `row${newCount}`;
        
        // Update the close button
        const closeBtn = form.querySelector('.close-btn');
        if (closeBtn) {
            closeBtn.onclick = () => removeRow(newCount);
        }
        
        // Update the heading
        const heading = form.querySelector('h3');
        heading.textContent = `Claim Details (${newCount})`;
        
        // Update all input IDs and labels
        updateFormElements(form, newCount);
    });
}

// When subject level changes, update subject options
document.getElementById('subjectLevel').addEventListener('change', function () {
    const selectedLevel = this.value;

    fetch(`/get_subjects/${selectedLevel}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Find all subjectCode fields that match pattern "subjectCode[0-9]+"
                const subjectSelects = document.querySelectorAll('.claim-form select[id^="subjectCode"]');

                subjectSelects.forEach(subjectSelect => {
                    // Clear existing options
                    subjectSelect.innerHTML = '<option value="">Select Subject Code</option>';

                    // Append new options
                    data.subjects.forEach(subject => {
                        const option = document.createElement('option');
                        option.value = subject.subject_code;
                        option.textContent = `${subject.subject_code} - ${subject.subject_title}`;
                        subjectSelect.appendChild(option);
                    });
                });
            } else {
                console.error('Error loading subjects:', data.message);
            }
        })
        .catch(error => console.error('Error:', error));
});

document.addEventListener('change', function (e) {
    if (e.target && e.target.matches('select[id^="subjectCode"]')) {
        const subjectCode = e.target.value;
        const id = e.target.id;  // e.g., "subjectCode3"
        const count = id.replace('subjectCode', '');

        if (!subjectCode) return;

        fetch(`/get_subject_info/${subjectCode}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    document.getElementById(`startDateHidden${count}`).value = data.start_date || '';
                    document.getElementById(`endDateHidden${count}`).value = data.end_date || '';
                    document.getElementById(`unclaimedLectureHidden${count}`).value = data.unclaimed_lecture || '';
                    document.getElementById(`unclaimedTutorialHidden${count}`).value = data.unclaimed_tutorial || '';
                    document.getElementById(`unclaimedPracticalHidden${count}`).value = data.unclaimed_practical || '';
                    document.getElementById(`unclaimedBlendedHidden${count}`).value = data.unclaimed_blended || '';
                    document.getElementById(`hourlyRateHidden${count}`).value = data.hourly_rate || '';
                } else {
                    alert('Failed to load subject info');
                }
            })
            .catch(err => console.error('Error:', err));
    }
});

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
function validateSubjectDetails() {
    const subjectLevel = document.getElementById('subjectLevel').value;

    if (!subjectLevel) {
        alert('Please select a Program Level');
        return false;
    }

    return true;
}

// Validation function
function validateDateFields() {
    const forms = document.querySelectorAll('.claim-form');

    // Malaysia today midnight
    const now = new Date();
    const malaysiaOffset = 8 * 60;
    const localOffset = now.getTimezoneOffset();
    const malaysiaTime = new Date(now.getTime() + (malaysiaOffset + localOffset) * 60000);
    malaysiaTime.setHours(0, 0, 0, 0);

    for (let i = 0; i < forms.length; i++) {
        const formNumber = i + 1;

        const subjectCode = document.getElementById(`subjectCode${formNumber}`).value;
        if (!subjectCode) {
            alert(`Course ${formNumber}: Please select a Subject Code.`);
            return false;
        }

        const startDateStr = document.getElementById(`startDateHidden${formNumber}`).value;
        const endDateStr = document.getElementById(`endDateHidden${formNumber}`).value;
        const dateInput = document.getElementById(`date${formNumber}`);

        if (!startDateStr || !endDateStr) {
            alert(`Course ${formNumber}: Missing subject start or end date.`);
            return false;
        }

        const startDate = new Date(startDateStr);
        const endDate = new Date(endDateStr);
        const selectedDate = new Date(dateInput.value);
        startDate.setHours(0, 0, 0, 0);
        endDate.setHours(0, 0, 0, 0);
        selectedDate.setHours(0, 0, 0, 0);

        if (!dateInput.value) {
            alert(`Course ${formNumber}: Please fill in the date.`);
            return false;
        }

        if (selectedDate < startDate) {
            alert(`Course ${formNumber}: Date is before subject start (${startDateStr}).`);
            return false;
        }

        if (selectedDate > endDate) {
            alert(`Course ${formNumber}: Date is after subject end (${endDateStr}).`);
            return false;
        }

        if (selectedDate > malaysiaTime) {
            alert(`Course ${formNumber}: Date cannot be in the future.`);
            return false;
        }
    }

    return true;
}

function validateHoursFields() {
    const forms = document.querySelectorAll('.claim-form');

    for (let i = 0; i < forms.length; i++) {
        const count = i + 1;

        const lecture = parseInt(document.getElementById(`lectureHours${count}`).value || '0', 10);
        const tutorial = parseInt(document.getElementById(`tutorialHours${count}`).value || '0', 10);
        const practical = parseInt(document.getElementById(`practicalHours${count}`).value || '0', 10);
        const blended = parseInt(document.getElementById(`blendedHours${count}`).value || '0', 10);

        const maxLecture = parseInt(document.getElementById(`unclaimedLectureHidden${count}`).value || '0', 10);
        const maxTutorial = parseInt(document.getElementById(`unclaimedTutorialHidden${count}`).value || '0', 10);
        const maxPractical = parseInt(document.getElementById(`unclaimedPracticalHidden${count}`).value || '0', 10);
        const maxBlended = parseInt(document.getElementById(`unclaimedBlendedHidden${count}`).value || '0', 10);

        if (lecture > maxLecture) {
            alert(`Course ${count}: Lecture Hours (${lecture}) exceed unclaimed limit (${maxLecture}).`);
            return false;
        }
        if (tutorial > maxTutorial) {
            alert(`Course ${count}: Tutorial Hours (${tutorial}) exceed unclaimed limit (${maxTutorial}).`);
            return false;
        }
        if (practical > maxPractical) {
            alert(`Course ${count}: Practical Hours (${practical}) exceed unclaimed limit (${maxPractical}).`);
            return false;
        }
        if (blended > maxBlended) {
            alert(`Course ${count}: Blended Hours (${blended}) exceed unclaimed limit (${maxBlended}).`);
            return false;
        }
    }

    return true;
}

async function checkApprovalStatusAndToggleButton(approvalId) {
    try {
        const response = await fetch(`/check_claim_status/${approvalId}`);
        if (!response.ok) throw new Error('Network response was not ok');

        const data = await response.json(); 
        const approveBtn = document.getElementById(`approve-btn-${approvalId}`);
        const voidBtn = document.getElementById(`void-btn-${approvalId}`);

        if (approveBtn) {
            // Disable approve button if status does not contain "Lecturer"
            if (!data.status.includes("Pending Acknowledgement by Lecturer")) {
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

function submitClaimSignature() {
    if (!signaturePad || signaturePad.isEmpty()) {
        alert("Please provide a signature before submitting.");
        return;
    }

    const canvas = document.getElementById("signature-pad");
    const dataURL = canvas.toDataURL();

    // Show loading overlay before starting fetch
    document.getElementById("loadingOverlay").style.display = "flex";

    fetch(`/api/lecturer_review_claim/${selectedApprovalId}`, {
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

function submitVoidClaimReason() {
    const reason = document.getElementById("void-reason").value.trim();

    if (!reason) {
        alert("Please provide a reason for voiding.");
        return;
    }

    // Show loading overlay
    document.getElementById("loadingOverlay").style.display = "flex";

    fetch(`/api/void_claim/${selectedVoidId}`, {
        method: "POST",
        body: JSON.stringify({ reason }),
        headers: { "Content-Type": "application/json" }
    })
    .then(response => {
        return response.json().then(data => {
            document.getElementById("loadingOverlay").style.display = "none";
            if (!data.success) throw new Error(data.error || "Failed to void claim");
            return data;
        });
    })
    .then(() => {
        alert("Claim has been voided successfully.");
        closeVoidModal();
        location.reload();
    })
    .catch(error => {
        document.getElementById("loadingOverlay").style.display = "none";
        console.error("Error during voiding:", error);
        alert("An error occurred while voiding the claim: " + error.message);
    });
}