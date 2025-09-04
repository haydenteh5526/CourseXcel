// Global Config
const RECORDS_PER_PAGE = 20;
let currentPages = {
    claimDetails: 1,
    claimAttachments: 1
};

// Format today as YYYY-MM-DD (local)
function todayLocalISO() {
    const d = new Date();
    const y = d.getFullYear();
    const m = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    return `${y}-${m}-${day}`;   // e.g., 2025-08-26
}

document.addEventListener('DOMContentLoaded', function () {
    const claimFormsContainer = document.getElementById('claimFormsContainer');
    const addRowBtn = document.getElementById('addRowBtn');
    const doneBtn = document.getElementById('doneBtn');
    let rowCount = 1;

    // Remove a claim row
    window.removeRow = function(count) {
        const rowToRemove = document.getElementById(`row${count}`);
        if (rowToRemove) {
            rowToRemove.remove();
            rowCount--;
            reorderRows();
            updateRowButtons();
        }
    }

    // Render a new claim form row
    function addRow(count) {
        const todayStr = todayLocalISO();

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
                        <input type="date" id="date${count}" name="date${count}" max="${todayStr}" required />
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
                <input type="hidden" id="subjectIdHidden${count}" name="subjectIdHidden${count}" />
                <input type="hidden" id="requisitionIdHidden${count}" name="requisitionIdHidden${count}" />
                <input type="hidden" id="rateIdHidden${count}" name="rateIdHidden${count}" />
                <input type="hidden" id="startDateHidden${count}" name="startDateHidden${count}"/>
                <input type="hidden" id="endDateHidden${count}" name="endDateHidden${count}" />
                <input type="hidden" id="unclaimedLectureHidden${count}" name="unclaimedLectureHidden${count}" />
                <input type="hidden" id="unclaimedTutorialHidden${count}" name="unclaimedTutorialHidden${count}" />
                <input type="hidden" id="unclaimedPracticalHidden${count}" name="unclaimedPracticalHidden${count}" />
                <input type="hidden" id="unclaimedBlendedHidden${count}" name="unclaimedBlendedHidden${count}" />
            </div>
        `;
        claimFormsContainer.insertAdjacentHTML('beforeend', rowHtml);
        // Wire date clamping for the new row
        attachFormListeners(count);

        // Populate subject codes for the selected level
        const selectedLevel = document.getElementById('subjectLevel').value;
        if (selectedLevel) {
            fetch(`/get_subjects/${selectedLevel}`)
                .then(response => response.json())
                .then(data => {
                    if (data.success && data.subjects && data.subjects.length > 0) {
                        const subjectSelect = document.getElementById(`subjectCode${count}`);
                        subjectSelect.innerHTML = '<option value="">Select Subject Code</option>';
                        data.subjects.forEach(s => {
                            const option = document.createElement('option');
                            option.value = s.value;    // "subject_id:requisition_id"
                            option.textContent = s.label;
                            subjectSelect.appendChild(option);
                        });
                    }
                    else {
                        subjectSelect.innerHTML = '<option value="">No subject available</option>';
                    }
                })
                .catch(error => {
                    console.error('Error fetching subjects:', error);
                });
        }
    }

    // Add/disable Add button depending on rowCount
    function updateRowButtons() {
        if (rowCount >= 40) {
            addRowBtn.textContent = "Maximum Reached (40)";
            addRowBtn.disabled = true;
        } else {
            addRowBtn.textContent = `Add Row (${rowCount + 1})`;
            addRowBtn.disabled = false;
        }
    }

    // Initial render with one claim row
    addRow(rowCount);
    updateRowButtons();

    // Click: append another claim row
    addRowBtn.addEventListener('click', function () {
        if (rowCount >= 40) {
            alert("You can only add up to 40 claim details.");
            return;
        }
        rowCount++;
        addRow(rowCount);
        updateRowButtons();
    });

    // Submit all claim details and attachments
    doneBtn.addEventListener('click', async function(e) {
        e.preventDefault();

        // Validate subject details, dates, hours
       if (!validateSubjectDetails() || !validateDateFields() || !validateHoursFields()) {
            return;
        }

        // Validate attachments
        const attachmentsInput = document.getElementById('upload_claim_attachment');
        const attachments = attachmentsInput.files;

        if (!attachments || attachments.length === 0) {
            alert("Please attach at least one PDF file before submitting.");
            return;
        }

        const forms = document.querySelectorAll('.claim-form');

        // Confirmation before sending
        const confirmSubmission = confirm(
            `You are about to submit ${attachments.length} attachment(s) and ${forms.length} claim detail(s).\n` +
            "Please double-check all details before submitting, as you may need to void and resubmit if something is wrong.\n\n" +
            "Do you want to proceed?"
        );
        if (!confirmSubmission) {
            return; // User clicked Cancel
        }

        // Show loading overlay
        document.getElementById("loadingOverlay").style.display = "flex";

        const formData = new FormData();
        formData.append('subject_level', document.getElementById('subjectLevel').value);

        // Append claim rows
        forms.forEach((form, index) => {
            const count = index + 1;

            formData.append(`subjectIdHidden${count}`, document.getElementById(`subjectIdHidden${count}`).value);
            formData.append(`requisitionIdHidden${count}`, document.getElementById(`requisitionIdHidden${count}`).value);
            formData.append(`rateIdHidden${count}`, document.getElementById(`rateIdHidden${count}`).value);

            const optText = document.getElementById(`subjectCode${count}`).selectedOptions[0]?.textContent || "";
            const subjectCodeOnly = optText.split(" - ")[0] || "";
            formData.append(`subjectCodeText${count}`, subjectCodeOnly);

            formData.append(`date${count}`, document.getElementById(`date${count}`).value);
            formData.append(`lectureHours${count}`, document.getElementById(`lectureHours${count}`).value || '0');
            formData.append(`tutorialHours${count}`, document.getElementById(`tutorialHours${count}`).value || '0');
            formData.append(`practicalHours${count}`, document.getElementById(`practicalHours${count}`).value || '0');
            formData.append(`blendedHours${count}`, document.getElementById(`blendedHours${count}`).value || '0');
            formData.append(`remarks${count}`, document.getElementById(`remarks${count}`).value);
        });

        // Append attachments
        for (let i = 0; i < attachments.length; i++) {
            formData.append('upload_claim_attachment', attachments[i]);
        }

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

// Remove the last added claim row
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

// Reorder the rows after removal
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
function clearAllFields() {
    const totalForms = document.querySelectorAll('.claim-form');
    totalForms.forEach((form, index) => {
        const count = index + 1;

        // Reset subject code dropdown
        const subjectSelect = document.getElementById(`subjectCode${count}`);
        if (subjectSelect) subjectSelect.innerHTML = '<option value="">Select Subject Code</option>';

        // Reset date
        const dateInput = document.getElementById(`date${count}`);
        if (dateInput) dateInput.value = '';

        // Reset hours dropdowns
        ['lectureHours', 'tutorialHours', 'practicalHours', 'blendedHours'].forEach(hourType => {
            const input = document.getElementById(`${hourType}${count}`);
            if (input) input.value = '';
        });

        // Reset remarks
        const remarksInput = document.getElementById(`remarks${count}`);
        if (remarksInput) remarksInput.value = '';

        // Reset hidden fields
        ['subjectIdHidden', 'requisitionIdHidden', 'rateIdHidden', 'startDateHidden', 'endDateHidden', 
        'unclaimedLectureHidden', 'unclaimedTutorialHidden', 'unclaimedPracticalHidden', 'unclaimedBlendedHidden'].forEach(hiddenId => {
            const hiddenInput = document.getElementById(`${hiddenId}${count}`);
            if (hiddenInput) hiddenInput.value = '';
        });
    });
}

// Load subject codes for specific subject level
document.getElementById('subjectLevel').addEventListener('change', function () {
    const selectedLevel = this.value;
    const subjectSelects = document.querySelectorAll('select[id^="subjectCode"]');

    if (selectedLevel) {
        // Reset other fields
        clearAllFields();

        fetch(`/get_subjects/${selectedLevel}`)
            .then(response => response.json())
            .then(data => {
                if (data.success && data.subjects && data.subjects.length > 0) {
                    subjectSelects.forEach(subjectSelect => {
                        subjectSelect.innerHTML = '<option value="">Select Subject Code</option>';
                        data.subjects.forEach(s => {
                            const option = document.createElement('option');
                            option.value = s.value;    // "subject_id:requisition_id"
                            option.textContent = s.label;
                            subjectSelect.appendChild(option);
                        });
                    });
                } else {
                    subjectSelects.forEach(subjectSelect => {
                        subjectSelect.innerHTML = '<option value="">No subject available</option>';
                    });
                    console.error('Error loading subjects:', data.message);
                }
            })
            .catch(error => {
                subjectSelects.forEach(subjectSelect => {
                    subjectSelect.innerHTML = '<option value="">Error loading subjects</option>';
                });
                console.error('Error fetching subjects:', error);
            });
    } else {
        // If "Select Subject Level" chosen, clear all fields
        clearAllFields();
    }
});

// Load subject info for specific subject code
document.addEventListener('change', function (e) {
    if (e.target && e.target.matches('select[id^="subjectCode"]')) {
        const value = e.target.value;            // e.g. "12:345"
        if (!value) return;

        const row = e.target.closest('.claim-form');
        const count = row.id.replace('row', ''); // "row3" -> "3"

        const [subjectIdStr, requisitionIdStr] = value.split(':');
        const subject_id = Number(subjectIdStr);
        const requisition_id = Number(requisitionIdStr);
        if (!subject_id || !requisition_id) return;

        fetch(`/get_subject_info?subject_id=${subject_id}&requisition_id=${requisition_id}`)
        .then(r => r.json())
        .then(data => {
            if (!data.success) { alert('Failed to load subject info'); return; }

            // Store IDs for submit
            document.getElementById(`subjectIdHidden${count}`).value = subject_id;
            document.getElementById(`requisitionIdHidden${count}`).value = requisition_id;
            document.getElementById(`rateIdHidden${count}`).value = data.rate_id ?? '';
            document.getElementById(`startDateHidden${count}`).value = data.start_date || '';
            document.getElementById(`endDateHidden${count}`).value = data.end_date || '';
            document.getElementById(`unclaimedLectureHidden${count}`).value = data.unclaimed_lecture ?? '';
            document.getElementById(`unclaimedTutorialHidden${count}`).value = data.unclaimed_tutorial ?? '';
            document.getElementById(`unclaimedPracticalHidden${count}`).value = data.unclaimed_practical ?? '';
            document.getElementById(`unclaimedBlendedHidden${count}`).value = data.unclaimed_blended ?? '';
        })
        .catch(err => console.error(err));
    }
});

function ensureHidden(id){
    let el = document.getElementById(id);
    if(!el){
        el = document.createElement('input');
        el.type = 'hidden';
        el.id = id;
        el.name = id; // so it posts with the form
        // append to the current row:
        const row = document.getElementById('row' + id.match(/\d+$/)[0]);
        row.appendChild(el);
    }
    return el;
}

// Wire date max clamp for a given row
function attachFormListeners(count) {
    const dateField = document.getElementById(`date${count}`);
    if (dateField) {
        const today = new Date().toLocaleDateString('en-CA'); // YYYY-MM-DD
        if (!dateField.max) dateField.max = today;

        // Clamp manual typing or picker selection
        const clampToMax = () => {
            if (dateField.value && dateField.value > dateField.max) {
                dateField.value = dateField.max;
            }
        };
        dateField.addEventListener('input', clampToMax);
        dateField.addEventListener('change', clampToMax);
        clampToMax(); // initial
    }
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

    // Helper: parse 'YYYY-MM-DD' into a local Date without TZ shifts
    const parseYMD = (s) => {
        if (!s) return null;
        const [y, m, d] = s.split('-').map(Number);
        if (!y || !m || !d) return null;
        return new Date(y, m - 1, d, 0, 0, 0, 0);
    };

    // Malaysia midnight "today"
    const now = new Date();
    const malaysiaOffsetMins = 8 * 60;
    const localOffsetMins = -now.getTimezoneOffset(); // minutes east of UTC
    // Convert "now" to Malaysia local time by shifting by (MY - local) minutes
    const malaysiaNow = new Date(now.getTime() + (malaysiaOffsetMins - localOffsetMins) * 60 * 1000);
    const malaysiaToday = new Date(malaysiaNow.getFullYear(), malaysiaNow.getMonth(), malaysiaNow.getDate());

    for (let i = 0; i < forms.length; i++) {
        const formNumber = i + 1;

        // Must have a selected subject row (composite)
        const subjectValue = document.getElementById(`subjectCode${formNumber}`).value;
        const subjectId = document.getElementById(`subjectIdHidden${formNumber}`)?.value;
        const requisitionId = document.getElementById(`requisitionIdHidden${formNumber}`)?.value;

        if (!subjectValue || !subjectId || !requisitionId) {
            alert(`Course ${formNumber}: Please select a Subject Code.`);
            return false;
        }

        // Required hidden bounds (for this exact LecturerSubject)
        const startDateStr = document.getElementById(`startDateHidden${formNumber}`)?.value;
        const endDateStr = document.getElementById(`endDateHidden${formNumber}`)?.value;
        const dateInput = document.getElementById(`date${formNumber}`);

        if (!dateInput?.value) {
            alert(`Claim Detail ${formNumber}: Please fill in the date.`);
            return false;
        }
        if (!startDateStr || !endDateStr) {
            alert(`Claim Detail ${formNumber}: Missing subject start or end date — reselect the Subject.`);
            return false;
        }

        const startDate = parseYMD(startDateStr);
        const endDate = parseYMD(endDateStr);
        const selectedDate = parseYMD(dateInput.value);

        if (!startDate || !endDate || !selectedDate) {
            alert(`Course ${formNumber}: Invalid date format. Please reselect date/subject.`);
            return false;
        }

        // Clamp checks (inclusive)
        if (selectedDate < startDate) {
            alert(`Claim Detail ${formNumber}: Date is before subject start (${startDateStr}).`);
            return false;
        }
        if (selectedDate > endDate) {
            alert(`Claim Detail ${formNumber}: Date is after subject end (${endDateStr}).`);
            return false;
        }

        // No future dates (Malaysia today)
        if (selectedDate > malaysiaToday) {
            alert(`Claim Detail ${formNumber}: Date cannot be in the future (Malaysia time).`);
            return false;
        }
    }
    return true;
}

// Validation function
function validateHoursFields() {
    const forms = document.querySelectorAll('.claim-form');
    const subjectClaims = {}; // key = "subjectId:requisitionId"

    for (let i = 0; i < forms.length; i++) {
        const count = i + 1;

        const subjectCodeCombo = document.getElementById(`subjectCode${count}`).value; // "subjectId:requisitionId"
        if (!subjectCodeCombo) continue;

        const subjectId = document.getElementById(`subjectIdHidden${count}`).value;
        const requisitionId = document.getElementById(`requisitionIdHidden${count}`).value;
        const subjectCode = document.getElementById(`subjectCode${count}`).selectedOptions[0]?.textContent.split(" - ")[0] || ""; 

        if (!subjectId || !requisitionId) {
            alert(`Course ${count}: Missing subject linkage.`);
            return false;
        }

        const key = `${subjectId}:${requisitionId}`;

        const lecture = parseInt(document.getElementById(`lectureHours${count}`).value || '0', 10);
        const tutorial = parseInt(document.getElementById(`tutorialHours${count}`).value || '0', 10);
        const practical = parseInt(document.getElementById(`practicalHours${count}`).value || '0', 10);
        const blended = parseInt(document.getElementById(`blendedHours${count}`).value || '0', 10);

        const maxLecture = parseInt(document.getElementById(`unclaimedLectureHidden${count}`).value || '0', 10);
        const maxTutorial = parseInt(document.getElementById(`unclaimedTutorialHidden${count}`).value || '0', 10);
        const maxPractical = parseInt(document.getElementById(`unclaimedPracticalHidden${count}`).value || '0', 10);
        const maxBlended = parseInt(document.getElementById(`unclaimedBlendedHidden${count}`).value || '0', 10);

        if (!subjectClaims[key]) {
            subjectClaims[key] = {
                subjectCode,
                lecture: 0, tutorial: 0, practical: 0, blended: 0,
                maxLecture, maxTutorial, maxPractical, maxBlended
            };
        }

        subjectClaims[key].lecture += lecture;
        subjectClaims[key].tutorial += tutorial;
        subjectClaims[key].practical += practical;
        subjectClaims[key].blended += blended;
    }

    for (const [key, c] of Object.entries(subjectClaims)) {
        if (c.lecture > c.maxLecture) { alert(`Subject ${c.subjectCode}: Total Lecture Hours ${c.lecture} exceed unclaimed limit ${c.maxLecture}.`); return false; }
        if (c.tutorial > c.maxTutorial) { alert(`Subject ${c.subjectCode}: Total Tutorial Hours ${c.tutorial} exceed unclaimed limit ${c.maxTutorial}.`); return false; }
        if (c.practical > c.maxPractical) { alert(`Subject ${c.subjectCode}: Total Practical Hours ${c.practical} exceed unclaimed limit ${c.maxPractical}.`); return false; }
        if (c.blended > c.maxBlended) { alert(`Subject ${c.subjectCode}: Total Blended Hours ${c.blended} exceed unclaimed limit ${c.maxBlended}.`); return false; }
    }
    return true;
}

// Check claim status and disable/enable buttons accordingly
async function checkApprovalStatusAndToggleButton(approvalId) {
    try {
        const response = await fetch(`/check_claim_status/${approvalId}`);
        if (!response.ok) throw new Error('Network response was not ok');

        const data = await response.json(); 
        const approveBtn = document.getElementById(`approve-btn-${approvalId}`);
        const voidBtn = document.getElementById(`void-btn-${approvalId}`);

        if (approveBtn) {
            // Disable approve button if status does not contain
            if (!data.status.includes("Pending Acknowledgement by Lecturer")) {
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
        console.error('Error checking approval status:', error);
    }
}

// Submit signature image for approval
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

// Submit void reason
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