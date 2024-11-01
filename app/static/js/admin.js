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

// Add these constants at the top of your file
const RECORDS_PER_PAGE = 20;
let currentPages = {
    'departments': 1,
    'lecturers': 1,
    'persons': 1,
    'subjects': 1
};

document.addEventListener('DOMContentLoaded', function() {
    console.log('Admin JS loaded');
    
    // Initialize current tab
    const currentTab = document.querySelector('meta[name="current-tab"]').content;
    const tabButton = document.querySelector(`.tab-button[onclick*="${currentTab}"]`);
    if (tabButton) {
        tabButton.click();
    }
    
    setupTableSearch();
    
    
    const uploadForm = document.getElementById('uploadForm');
    console.log('Upload form found:', uploadForm);
    
    if (uploadForm) {
        uploadForm.addEventListener('submit', function(e) {
            e.preventDefault();
            console.log('Form submitted');
            
            const formData = new FormData(this);
            const file = document.getElementById('courseStructure').files[0];
            
            if (!file) {
                alert('Please select a file');
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
                    alert(data.message);
                    if (data.warnings) {
                        data.warnings.forEach(warning => {
                            alert('Warning: ' + warning);
                        });
                    }
                    window.location.reload(true);
                } else {
                    alert(data.message || 'Upload failed');
                }
            })
            .catch(error => {
                console.error('Upload error:', error);
                alert('Upload failed: ' + error.message);
            });
        });
    }

    // Add pagination handlers for each table
    ['departments', 'lecturers', 'persons', 'subjects'].forEach(tableType => {
        const container = document.getElementById(tableType);
        if (!container) return;

        const prevBtn = container.querySelector('.prev-btn');
        const nextBtn = container.querySelector('.next-btn');

        if (prevBtn) {
            prevBtn.addEventListener('click', () => {
                if (currentPages[tableType] > 1) {
                    currentPages[tableType]--;
                    updateTable(tableType, currentPages[tableType]);
                }
            });
        }

        if (nextBtn) {
            nextBtn.addEventListener('click', () => {
                const tableElement = document.getElementById(tableType + 'Table');
                const rows = Array.from(tableElement.querySelectorAll('tbody tr'));
                const filteredRows = rows.filter(row => row.dataset.searchMatch !== 'false');
                const totalPages = Math.ceil(filteredRows.length / RECORDS_PER_PAGE);

                if (currentPages[tableType] < totalPages) {
                    currentPages[tableType]++;
                    updateTable(tableType, currentPages[tableType]);
                }
            });
        }

        // Initialize table pagination
        updateTable(tableType, 1);
    });

    // Initialize tables with pagination
    ['departments', 'lecturers', 'persons', 'subjects'].forEach(table => {
        updateTable(table, 1);
    });
});

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
                window.location.reload(true);
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

    // Store current tab in session via AJAX
    fetch('/set_admin_tab', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ current_tab: tabName })
    });
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
                
                // Set form mode and ID explicitly
                form.dataset.table = table;
                form.dataset.id = id;
                form.dataset.mode = 'edit';  // Explicitly set edit mode

                // Create form fields
                createFormFields(table, form);

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
                    alert('Record deleted successfully');
                    window.location.reload();
                } else {
                    throw new Error('Failed to delete record');
                }
            })
            .catch(error => {
                console.error('Error deleting record:', error);
                alert('Error deleting record: ' + error.message);
            });
    }
}

function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            try {
                alert('Previewing file contents...');
                previewExcelContents(e.target.result);
            } catch (error) {
                alert('Error previewing file: ' + error.message);
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
                alert(data.message);
                window.location.reload(true);
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

    // Add the id to formData for edit mode
    if (mode === 'edit') {
        formData.id = id;
    }

    // Special handling for subjects
    if (table === 'subjects') {
        const endpoint = mode === 'edit' ? '/update_subject' : '/save_subject';
        fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert(data.message);
                window.location.reload(true);
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
                alert(data.message);
                window.location.reload(true);
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
    const form = document.getElementById('editForm');
    
    // Set form mode for create
    form.dataset.table = table;
    form.dataset.mode = 'create';
    
    // Use the shared helper function to create fields
    createFormFields(table, form);
    
    modal.style.display = 'block';
}

// Add this function to handle pagination
function updateTable(tableType, page) {
    const tableElement = document.getElementById(tableType + 'Table');
    if (!tableElement) return;

    const rows = Array.from(tableElement.querySelectorAll('tbody tr'));
    const filteredRows = rows.filter(row => row.dataset.searchMatch !== 'false');
    const totalPages = Math.ceil(filteredRows.length / RECORDS_PER_PAGE);
    
    // Update page numbers
    const container = tableElement.closest('.tab-content');
    const currentPageSpan = container.querySelector('.current-page');
    const totalPagesSpan = container.querySelector('.total-pages');
    
    if (currentPageSpan) currentPageSpan.textContent = page;
    if (totalPagesSpan) totalPagesSpan.textContent = totalPages;
    
    // Show/hide rows based on current page
    filteredRows.forEach((row, index) => {
        const shouldShow = index >= (page - 1) * RECORDS_PER_PAGE && index < page * RECORDS_PER_PAGE;
        row.style.display = shouldShow ? '' : 'none';
    });
    
    // Update pagination buttons
    const prevBtn = container.querySelector('.prev-btn');
    const nextBtn = container.querySelector('.next-btn');
    if (prevBtn) prevBtn.disabled = page === 1;
    if (nextBtn) nextBtn.disabled = page === totalPages || totalPages === 0;
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

// Modify the setupTableSearch function
function setupTableSearch() {
    document.querySelectorAll('.table-search').forEach(searchInput => {
        searchInput.addEventListener('input', function() {
            const tableId = this.dataset.table;
            const tableType = tableId.replace('Table', '');
            const searchText = this.value.toLowerCase();
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
                
                // Just update visibility without affecting display style
                row.classList.toggle('filtered-out', !text.includes(searchTerm));
            });

            // Reset to first page and reinitialize pagination
            setupPagination(tableId);
        });
    });
}

function setupPagination(specificTableId = null) {
    const tables = specificTableId ? [specificTableId] : ['departmentsTable', 'lecturersTable', 'personsTable', 'subjectsTable'];
    const recordsPerPage = 20;

    tables.forEach(tableId => {
        const table = document.getElementById(tableId);
        if (!table) return;

        const tbody = table.querySelector('tbody');
        // Only consider rows that aren't filtered out by search
        const rows = Array.from(tbody.querySelectorAll('tr:not(.filtered-out)'));
        const totalPages = Math.ceil(rows.length / recordsPerPage);
        
        const paginationContainer = table.parentElement.querySelector('.pagination');
        const prevBtn = paginationContainer.querySelector('.prev-btn');
        const nextBtn = paginationContainer.querySelector('.next-btn');
        const currentPageSpan = paginationContainer.querySelector('.current-page');
        const totalPagesSpan = paginationContainer.querySelector('.total-pages');

        let currentPage = 1;
        totalPagesSpan.textContent = totalPages;

        function showPage(page) {
            const start = (page - 1) * recordsPerPage;
            const end = start + recordsPerPage;

            // Hide all rows first
            tbody.querySelectorAll('tr').forEach(row => {
                row.style.display = 'none';
            });

            // Show only the rows for current page that aren't filtered out
            rows.slice(start, end).forEach(row => {
                row.style.display = '';
            });

            prevBtn.disabled = page === 1;
            nextBtn.disabled = page === totalPages;
            currentPageSpan.textContent = page;
        }

        prevBtn.addEventListener('click', () => {
            if (currentPage > 1) {
                currentPage--;
                showPage(currentPage);
            }
        });

        nextBtn.addEventListener('click', () => {
            if (currentPage < totalPages) {
                currentPage++;
                showPage(currentPage);
            }
        });

        // Initialize first page
        showPage(1);
    });
}
// Helper function to create form fields (extracted from createRecord)
function createFormFields(table, form) {
    const formFields = form.querySelector('#editFormFields');
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
                <option value="Others">Others</option>
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
}

