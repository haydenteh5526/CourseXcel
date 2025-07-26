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
            </div>
        `;
        claimFormsContainer.insertAdjacentHTML('beforeend', rowHtml);
    }

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

    function updateRowButtons() {
        if (rowCount >= 15) {
            addRowBtn.textContent = "Maximum Reached (15)";
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
        if (rowCount >= 15) {
            alert("You can only add up to 15 claim details.");
            return;
        }
        rowCount++;
        addRow(rowCount);
        updateRowButtons();
    });

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

    // Modify the done button event listener
    doneBtn.addEventListener('click', async function(e) {
        e.preventDefault();

        // Add subject details validation before proceeding
        if (!validateSubjectDetails()) {
            return;
        }

        // Add existing validation check
        if (!validateRequiredFields()) {
            return;
        }
        
        // Show loading overlay
        document.getElementById("loadingOverlay").style.display = "flex";

        const formData = new FormData();

        // Add shared subject fields (applies to all rows)
        formData.append('subject_level', document.getElementById('subjectLevel').value);
        formData.append('subject_code', document.getElementById('subjectCode').value);
        formData.append('hourly_rate', document.getElementById('hourlyRateHidden').value);
      
        // Add course details
        const forms = document.querySelectorAll('.claim-form');
        forms.forEach((form, index) => {
            const count = index + 1;
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
            console.error('Error:', error);
            alert('Error submitting form: ' + error.message);
        });
    });  
});

// When subject level changes, update subject options
document.getElementById('subjectLevel').addEventListener('change', function() {
    const selectedLevel = this.value;
    
    fetch(`/get_subjects/${selectedLevel}`)
        .then(response => response.json())
        .then(data => {
            const subjectSelect = document.getElementById('subjectCode');
            subjectSelect.innerHTML = '<option value="">Select Subject Code</option>';
            
            if (data.success) {
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
});

document.getElementById('subjectCode').addEventListener('change', function () {
    const subjectCode = this.value;
    if (!subjectCode) return;

    fetch(`/get_subject_info/${subjectCode}`)
        .then(response => response.json())
        .then(data => {
            const startDateInput = document.getElementById('startDateHidden');
            const hourlyRateInput = document.getElementById('hourlyRateHidden');

            if (data.success) {
                startDateInput.value = data.start_date || '';
                hourlyRateInput.value = data.hourly_rate || '';
            } else {
                console.error('Failed to get subject info:', data.message);
                startDateInput.value = '';
                hourlyRateInput.value = '';
            }
        })
        .catch(err => {
            console.error('Error fetching subject info:', err);
            document.getElementById('startDateHidden').value = '';
            document.getElementById('hourlyRateHidden').value = '';
        });
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
    const subjectCode = document.getElementById('subjectCode');

    if (!subjectLevel) {
        alert('Please select a Program Level');
        return false;
    }

    if (!subjectCode.value) {
        alert('Please select a Subject Code');
        return false;
    }

    return true;
}

// Validation function
function validateRequiredFields() {
    const forms = document.querySelectorAll('.claim-form');

    // Malaysia time today at midnight
    const now = new Date();
    const malaysiaOffset = 8 * 60;
    const localOffset = now.getTimezoneOffset();
    const malaysiaTime = new Date(now.getTime() + (malaysiaOffset + localOffset) * 60000);
    malaysiaTime.setHours(0, 0, 0, 0);

    // Get start date from hidden input
    const hiddenStartDateInput = document.getElementById('hiddenStartDate');
    if (!hiddenStartDateInput || !hiddenStartDateInput.value) {
        alert('Please select a valid subject code to get the start date.');
        return false;
    }
    const startDateStr = hiddenStartDateInput.value;
    const startDate = new Date(startDateStr);
    startDate.setHours(0, 0, 0, 0);

    for (let i = 0; i < forms.length; i++) {
        const formNumber = i + 1;
        const dateInput = document.getElementById(`date${formNumber}`);

        if (!dateInput || !dateInput.value) {
            alert(`Course ${formNumber}: Please fill in the date`);
            return false;
        }

        const selectedDate = new Date(dateInput.value);
        selectedDate.setHours(0, 0, 0, 0);

        if (selectedDate < startDate) {
            alert(`Course ${formNumber}: Date cannot be earlier than the subject start date (${startDateStr}).`);
            return false;
        }

        if (selectedDate > malaysiaTime) {
            alert(`Course ${formNumber}: Date cannot be in the future (Malaysia time).`);
            return false;
        }
    }

    return true;
}

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

}