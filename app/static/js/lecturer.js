document.addEventListener('DOMContentLoaded', function () {
    const claimFormsContainer = document.getElementById('claimFormsContainer');
    const addRowBtn = document.getElementById('addRowBtn');
    const saveAllBtn = document.getElementById('saveAllBtn');
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
            <div id="row${count}" class="course-form">
                ${count > 1 ? '<button type="button" class="close-btn" onclick="removeRow(' + count + ')">×</button>' : ''}
                <h3>Claim Details (${count})</h3>
                <div class="form-row">
                    <div class="form-group">
                        <label for="date${count}">Date:</label>
                        <input type="date" id="date${count}" name="date${count}" required />
                    </div>
                    <div class="form-group">
                        <label for="subjectLevel${count}">Program Level:</label>
                        <select id="subjectLevel${count}" name="subjectLevel${count}" required>
                            <option value="">Select Program Level</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="subjectCode${count}">Subject Code:</label>
                        <select id="subjectCode${count}" name="subjectCode${count}" required>
                            <option value="">Select Subject Code</option>
                        </select>
                    </div>
                </div>
                <div class="form-row hours-row">
                    <div class="form-group">
                        <label for="lectureHours${count}">Lecture Hours:</label>
                        <input type="number" id="lectureHours${count}" name="lectureHours${count}" min="1" required />
                    </div>
                    <div class="form-group">
                        <label for="tutorialHours${count}">Tutorial Hours:</label>
                        <input type="number" id="tutorialHours${count}" name="tutorialHours${count}" min="1" required />
                    </div>
                    <div class="form-group">
                        <label for="practicalHours${count}">Practical Hours:</label>
                        <input type="number" id="practicalHours${count}" name="practicalHours${count}" min="1" required />
                    </div>
                    <div class="form-group">
                        <label for="blendedHours${count}">Blended Hours:</label>
                        <input type="number" id="blendedHours${count}" name="blendedHours${count}" min="1" required />
                    </div>
                </div>
            </div>
        `;
        claimFormsContainer.insertAdjacentHTML('beforeend', rowHtml);
        attachFormListeners(count);
    }

    function attachFormListeners(count) {
        const subjectLevelField = document.getElementById(`subjectLevel${count}`);
        const subjectCodeField = document.getElementById(`subjectCode${count}`);
        
        // Listen for subject level changes
        subjectLevelField.addEventListener('change', function() {
            const selectedLevel = this.value;
            if (selectedLevel) {
                fetch(`/get_lecturer_subjects/${selectedLevel}`)
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
    }

    // Function to remove the last added course form
    function removeRow(count) {
        const rowToRemove = document.getElementById(`row${count}`);
        if (rowToRemove) {
            rowToRemove.remove();
            rowCount--;
            // Reorder the remaining forms
            reorderRows();
            updateRowButtons();
        }
    }

    // Function to update add/remove buttons visibility
    function updateRowButtons() {
        addRowBtn.textContent = `Add Row (${rowCount + 1})`;
        addRowBtn.style.display = 'inline-block';
    }

    // Initialize with one course form by default
    addRow(rowCount);
    updateRowButtons();

    addRowBtn.addEventListener('click', function () {
        rowCount++;
        addRow(rowCount);
        updateRowButtons();
    });

    // Add a new function to reorder the forms after removal
    function reorderRows() {
        const forms = document.querySelectorAll('.course-form');
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
            heading.textContent = `Course Details (${newCount})`;
            
            // Update all input IDs and labels
            updateFormElements(form, newCount);
        });
    }

    // Modify the save button event listener
    saveAllBtn.addEventListener('click', async function(e) {
        e.preventDefault();

        // Add existing validation check
        if (!validateRequiredFields()) {
            return;
        }
        
        // Show loading overlay
        document.getElementById("loadingOverlay").style.display = "flex";

        const formData = new FormData();
        
        // Add course details
        const forms = document.querySelectorAll('.course-form');
        forms.forEach((form, index) => {
            const count = index + 1;
            formData.append(`subjectLevel${count}`, document.getElementById(`subjectLevel${count}`).value);
            formData.append(`subjectCode${count}`, document.getElementById(`subjectCode${count}`).value);
            formData.append(`date${count}`, document.getElementById(`date${count}`).value);
            formData.append(`lectureHours${count}`, document.getElementById(`lectureHours${count}`).value || '0');
            formData.append(`tutorialHours${count}`, document.getElementById(`tutorialHours${count}`).value || '0');
            formData.append(`practicalHours${count}`, document.getElementById(`practicalHours${count}`).value || '0');
            formData.append(`blendedHours${count}`, document.getElementById(`blendedHours${count}`).value || '1');
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

    // Get today's date in Malaysia time (GMT+8)
    const now = new Date();
    const malaysiaOffset = 8 * 60; // +8 hours in minutes
    const localOffset = now.getTimezoneOffset(); // e.g., -480 for GMT+8
    const malaysiaTime = new Date(now.getTime() + (malaysiaOffset + localOffset) * 60000);
    malaysiaTime.setHours(0, 0, 0, 0); // Normalize to midnight Malaysia time

    for (let i = 0; i < forms.length; i++) {
        const formNumber = i + 1;
        const dateValue = document.getElementById(`date${formNumber}`).value;

        if (!dateValue) {
            alert(`Course ${formNumber}: Please fill in the date`);
            return false;
        }

        const selectedDate = new Date(dateValue);
        selectedDate.setHours(0, 0, 0, 0); // Normalize input to midnight

        if (selectedDate > malaysiaTime) {
            alert(`Course ${formNumber}: Date cannot be in the future (Malaysia time)`);
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
    fetch(`/get_lecturer_subjects/${level}`)
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