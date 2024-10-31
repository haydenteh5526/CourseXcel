// Move editableFields to the global scope (outside any function)
const editableFields = {
    'departments': ['department_code', 'department_name'],
    'lecturers': ['lecturer_name', 'level', 'department_code', 'ic_no'],
    'persons': ['email', 'department_code'],
    'subjects': [
        'subject_code',
        'subject_title',
        'lecture_hours',
        'tutorial_hours',
        'practical_hours',
        'blended_hours',
        'lecture_weeks',
        'tutorial_weeks',
        'practical_weeks',
        'blended_weeks'
    ]
};

document.addEventListener('DOMContentLoaded', function() {
    console.log('Admin JS loaded');
    
    const uploadForm = document.getElementById('uploadForm');
    console.log('Upload form found:', uploadForm);
    
    if (uploadForm) {
        uploadForm.addEventListener('submit', function(e) {
            e.preventDefault();
            console.log('Form submitted');
            
            const formData = new FormData(this);
            const file = document.getElementById('courseStructure').files[0];
            
            if (!file) {
                showUploadStatus('danger', 'Please select a file');
                return;
            }
            
            fetch('/admin/upload_subjects', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                console.log('Response:', data);
                if (data.success) {
                    showUploadStatus('success', data.message);
                    if (data.warnings) {
                        data.warnings.forEach(warning => {
                            showUploadStatus('warning', warning, false);
                        });
                    }
                    refreshSubjectsTable();
                    uploadForm.reset();
                } else {
                    showUploadStatus('danger', data.message || 'Upload failed');
                }
            })
            .catch(error => {
                console.error('Upload error:', error);
                showUploadStatus('danger', 'Upload failed: ' + error.message);
            });
        });
    }
});

function initializeAdminDashboard() {
    openTab('departments'); // Open the Departments tab by default
    loadAllTables();
    setupFileUpload();
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
            alert('Please select records to delete');
            return;
        }

        if (!confirm('Are you sure you want to delete the selected records?')) {
            return;
        }

        const selectedIds = Array.from(selectedBoxes).map(box => box.dataset.id);

        try {
            const response = await fetch(`/api/delete/${tableType}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ ids: selectedIds })
            });

            if (response.ok) {
                // Remove deleted rows from the table
                selectedBoxes.forEach(box => box.closest('tr').remove());
                alert('Records deleted successfully');
            } else {
                alert('Failed to delete records');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred while deleting records');
        }
    });
});

// Tab Management
function openTab(evt, tabName) {
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
}

// Table Management
function loadAllTables() {
    const tables = ['departments', 'lecturers', 'persons', 'subjects'];
    tables.forEach(table => loadTable(table));
}

function loadTable(table) {
    const tableElement = document.getElementById(`${table}Table`);
    if (!tableElement) {
        console.error(`Table element not found: ${table}Table`);
        return;
    }
    
    showLoadingState(tableElement);
    
    // Use the new endpoint for getting data
    fetch('/admin/get-data')
        .then(response => response.json())
        .then(data => {
            if (data && data[table] && data[table].length > 0) {
                renderTable(tableElement, data[table], table);
            } else {
                showNoDataMessage(tableElement);
            }
        })
        .catch(error => {
            console.error(`Error loading ${table}:`, error);
            showErrorMessage(tableElement, error);
        });
}

function renderTable(tableElement, data, table) {
    const thead = createTableHeader(data[0]);
    const tbody = createTableBody(data, table);
    
    tableElement.innerHTML = '';
    tableElement.appendChild(thead);
    tableElement.appendChild(tbody);
}

function createTableHeader(firstRow) {
    const thead = document.createElement('thead');
    const headerRow = document.createElement('tr');
    
    // Add data columns
    Object.keys(firstRow).forEach(key => {
        const th = document.createElement('th');
        th.textContent = key;
        headerRow.appendChild(th);
    });
    
    // Add actions column
    const actionsHeader = document.createElement('th');
    actionsHeader.textContent = 'Actions';
    headerRow.appendChild(actionsHeader);
    
    thead.appendChild(headerRow);
    return thead;
}

function createTableBody(data, table) {
    const tbody = document.createElement('tbody');
    
    data.forEach(item => {
        const row = document.createElement('tr');
        
        // Add data cells
        Object.values(item).forEach(value => {
            const td = document.createElement('td');
            td.textContent = value;
            row.appendChild(td);
        });
        
        // Add action buttons
        const actionsTd = document.createElement('td');
        actionsTd.innerHTML = `
            <button onclick="editRecord('${table}', '${item.id}')">Edit</button>
            <button onclick="deleteRecord('${table}', '${item.id}')">Delete</button>
        `;
        row.appendChild(actionsTd);
        
        tbody.appendChild(row);
    });
    
    return tbody;
}

// File Upload Management
function setupFileUpload() {
    const uploadForm = document.getElementById('uploadForm');
    if (uploadForm) {
        uploadForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const courseLevel = document.getElementById('course_level').value;
            
            if (!courseLevel) {
                showUploadStatus('danger', 'Please select a course level', false);
                return;
            }
            
            fetch('/admin/upload_subjects', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showUploadStatus('success', data.message, true);
                    refreshSubjectsTable();
                    uploadForm.reset();
                } else {
                    showUploadStatus('danger', data.message || 'Upload failed', false);
                }
            })
            .catch(error => {
                console.error('Upload error:', error);
                showUploadStatus('danger', 'Upload failed: ' + error.message, false);
            });
        });
    }
}

// Utility Functions
function showUploadStatus(type, message, autoHide = true) {
    const statusDiv = document.getElementById('uploadStatus');
    if (statusDiv) {
        statusDiv.className = `alert alert-${type}`;
        statusDiv.textContent = message;
        statusDiv.style.display = 'block';
        
        if (autoHide && type === 'success') {
            setTimeout(() => {
                statusDiv.style.display = 'none';
                statusDiv.textContent = '';
            }, 3000); // Hide after 3 seconds
        }
    }
}

function showLoadingState(element) {
    element.innerHTML = '<div class="alert alert-info">Loading...</div>';
}

function showNoDataMessage(element) {
    element.innerHTML = '<div class="alert alert-info">No data available</div>';
}

function showErrorMessage(element, error) {
    element.innerHTML = `<div class="alert alert-danger">Error loading data: ${error.message}</div>`;
}

function editRecord(table, id) {
    fetch(`/get_record/${table}/${id}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const modal = document.getElementById('editModal');
                const form = document.getElementById('editForm');
                form.dataset.table = table;
                form.dataset.id = id;
                form.dataset.mode = 'edit';

                // Create form fields as before
                createRecord(table);

                // Populate the fields
                for (const [key, value] of Object.entries(data.record)) {
                    const input = form.querySelector(`[name="${key}"]`);
                    if (input) {
                        input.value = value;
                    }
                }

                // Handle subject levels if applicable
                if (table === 'subjects' && data.record.levels) {
                    const levelSelect = form.querySelector('#subject_levels');
                    if (levelSelect) {
                        data.record.levels.forEach(level => {
                            Array.from(levelSelect.options).forEach(option => {
                                if (option.value === level) {
                                    option.selected = true;
                                }
                            });
                        });
                    }
                }

                modal.style.display = 'block';
            }
        });
}

function deleteRecord(table, id) {
    if (confirm(`Are you sure you want to delete this record from ${table}?`)) {
        fetch(`/api/${table}/${id}`, { method: 'DELETE' })
            .then(response => {
                if (response.ok) {
                    loadTable(table);
                } else {
                    throw new Error('Failed to delete record');
                }
            })
            .catch(error => console.error('Error deleting record:', error));
    }
}

function refreshSubjectsTable() {
    fetch('/admin/get-data')
        .then(response => response.json())
        .then(data => {
            if (data.subjects) {
                const subjectsTab = document.querySelector('#subjects .table-responsive');
                if (subjectsTab) {
                    const table = `
                        <table class="table">
                            <thead>
                                <tr>
                                    <th><input type="checkbox" class="select-all" data-table="subjectsTable"></th>
                                    <th>Subject Code</th>
                                    <th>Subject Title</th>
                                    <th>Lecture Hours</th>
                                    <th>Tutorial Hours</th>
                                    <th>Practical Hours</th>
                                    <th>Blended Hours</th>
                                    <th>Lecture Weeks</th>
                                    <th>Tutorial Weeks</th>
                                    <th>Practical Weeks</th>
                                    <th>Blended Weeks</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${data.subjects.map(subject => `
                                    <tr>
                                        <td><input type="checkbox" class="record-checkbox" data-id="${subject.subject_code}"></td>
                                        <td>${subject.subject_code || ''}</td>
                                        <td>${subject.subject_title || ''}</td>
                                        <td>${subject.lecture_hours || 0}</td>
                                        <td>${subject.tutorial_hours || 0}</td>
                                        <td>${subject.practical_hours || 0}</td>
                                        <td>${subject.blended_hours || 0}</td>
                                        <td>${subject.lecture_weeks || 0}</td>
                                        <td>${subject.tutorial_weeks || 0}</td>
                                        <td>${subject.practical_weeks || 0}</td>
                                        <td>${subject.blended_weeks || 0}</td>
                                        <td>
                                            <button class="btn btn-sm btn-primary" onclick="editRecord('subjects', '${subject.subject_code}')">Edit</button>
                                            <button class="btn btn-sm btn-danger" onclick="deleteRecord('subjects', '${subject.subject_code}')">Delete</button>
                                        </td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    `;
                    subjectsTab.innerHTML = table;
                }
            }
        })
        .catch(error => console.error('Error refreshing subjects:', error));
}

function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            try {
                showUploadStatus('info', 'Previewing file contents...');
                previewExcelContents(e.target.result);
            } catch (error) {
                showUploadStatus('danger', 'Error previewing file: ' + error.message);
            }
        };
        reader.readAsBinaryString(file);
    }
}

function previewExcelContents(data) {
    const previewDiv = document.getElementById('filePreview');
    if (previewDiv) {
        previewDiv.innerHTML = '<h4>File Preview</h4>';
        // Add preview table here if needed
    }
}

// Update the get subjects by level function
function getSubjectsByCourseLevel(courseLevel) {  // Changed from program level
    fetch(`/get_subjects_by_level/${courseLevel}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                refreshSubjectsTable(data.subjects);
            }
        })
        .catch(error => console.error('Error:', error));
}

// Close modal when clicking the close button or outside the modal
document.querySelector('.modal-close').addEventListener('click', () => {
    document.getElementById('editModal').style.display = 'none';
});

window.addEventListener('click', (event) => {
    const modal = document.getElementById('editModal');
    if (event.target === modal) {
        modal.style.display = 'none';
    }
});

// Handle form submission
document.getElementById('editForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const table = this.dataset.table;
    const mode = this.dataset.mode;
    const id = this.dataset.id;
    const formData = {};
    
    // Collect all form data
    const inputs = this.querySelectorAll('input, select');
    inputs.forEach(input => {
        if (input.name === 'subject_levels' && input.multiple) {
            formData[input.name] = Array.from(input.selectedOptions).map(option => option.value);
        } else {
            formData[input.name] = input.value;
        }
    });

    // Special handling for subjects
    if (table === 'subjects') {
        fetch('/save_subject', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.getElementById('editModal').style.display = 'none';
                refreshSubjectsTable();
            } else {
                alert('Error: ' + (data.message || 'Unknown error occurred'));
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error: ' + error.message);
        });
    } else {
        // Original code for other tables
        const url = mode === 'create' 
            ? `/api/${table}` 
            : `/api/${table}/${id}`;
        
        fetch(url, {
            method: mode === 'create' ? 'POST' : 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.getElementById('editModal').style.display = 'none';
                loadTable(table);
            } else {
                alert('Error: ' + (data.message || 'Unknown error occurred'));
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error: ' + error.message);
        });
    }
});

// Add click event listeners for create buttons
document.querySelectorAll('.create-record').forEach(button => {
    button.addEventListener('click', function() {
        const tableType = this.dataset.table;
        
        // Special handling for persons table
        if (tableType === 'persons') {
            window.location.href = '/register';  // Redirect to registration page
        } else {
            createRecord(tableType);  // Normal modal creation for other tables
        }
    });
});

function createRecord(table) {
    console.log('Creating record for table:', table);
    const modal = document.getElementById('editModal');
    const formFields = document.getElementById('editFormFields');
    formFields.innerHTML = '';

    if (table === 'subjects') {
        const fields = editableFields[table] || [];
        fields.forEach(key => {
            const formGroup = document.createElement('div');
            formGroup.className = 'form-group';
            
            const label = document.createElement('label');
            label.textContent = key.replace(/_/g, ' ')
                                 .charAt(0).toUpperCase() + 
                                 key.slice(1).replace(/_/g, ' ');
            
            const input = document.createElement('input');
            input.type = key.includes('hours') || key.includes('weeks') ? 'number' : 'text';
            input.name = key;
            input.required = true;
            
            formGroup.appendChild(label);
            formGroup.appendChild(input);
            formFields.appendChild(formGroup);
        });

        // Add the subject levels select after other fields
        const levelGroup = document.createElement('div');
        levelGroup.className = 'form-group';
        levelGroup.innerHTML = `
            <label for="subject_levels">Subject Levels:</label>
            <select id="subject_levels" name="subject_levels" multiple required>
                <option value="Certificate">Certificate</option>
                <option value="Foundation">Foundation</option>
                <option value="Diploma">Diploma</option>
                <option value="Degree">Degree</option>
                <option value="Masters">Masters</option>
            </select>
            <small>Hold Ctrl/Cmd to select multiple levels</small>
        `;
        formFields.appendChild(levelGroup);
    } else {
        const fields = editableFields[table] || [];
        fields.forEach(key => {
            const formGroup = document.createElement('div');
            formGroup.className = 'form-group';
            
            const label = document.createElement('label');
            label.textContent = key.replace(/_/g, ' ')
                                 .charAt(0).toUpperCase() + 
                                 key.slice(1).replace(/_/g, ' ');
            
            const input = document.createElement('input');
            input.type = 'text';
            input.name = key;
            input.required = true;
            
            formGroup.appendChild(label);
            formGroup.appendChild(input);
            formFields.appendChild(formGroup);
        });
    }

    const form = document.getElementById('editForm');
    form.dataset.table = table;
    form.dataset.mode = 'create';
    modal.style.display = 'block';
}

function showChangePasswordModal() {
    const modal = document.getElementById('passwordModal');
    modal.style.display = 'block';
}

function closePasswordModal() {
    const modal = document.getElementById('passwordModal');
    modal.style.display = 'none';
}

// Add event listener for password form submission
document.getElementById('passwordForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const password = document.getElementById('new_password').value;
    const confirmPassword = document.getElementById('confirm_password').value;
    
    if (password !== confirmPassword) {
        alert('Passwords do not match!');
        return;
    }
    
    const data = {
        email: document.getElementById('user_email').value,
        new_password: password
    };
    
    fetch('/api/change_password', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Password changed successfully');
            closePasswordModal();
        } else {
            alert(data.message || 'Failed to change password');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error changing password');
    });
});