// Move editableFields to the global scope (outside any function)
const editableFields = {
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
    ],
    'departments': ['department_code', 'department_name'],
    'lecturers': ['name', 'email', , 'ic_no', 'level', 'department_code', 'hop_id', 'dean_id', 'upload_file'],
    'program_officers': ['name', 'email', 'department_code'], 
    'hops': ['name', 'email', 'department_code', 'dean_id'], 
    'deans': ['name', 'email', 'department_code']
};

// Add these constants at the top of your file
const RECORDS_PER_PAGE = 20;
let currentPages = {
    'subjects': 1,
    'departments': 1,
    'lecturers': 1,
    'program_officers': 1,
    'hops': 1,
    'deans': 1
};

document.addEventListener('DOMContentLoaded', function() {
    // Initialize current tab
    const currentTab = document.querySelector('meta[name="current-tab"]').content;
    const tabButton = document.querySelector(`.tab-button[onclick*="${currentTab}"]`);
    if (tabButton) {
        tabButton.click();
    }
    
    setupTableSearch();  

    // Add pagination handlers for each table
    ['subjects', 'departments', 'lecturers', 'program_officers', 'hops', 'deans'].forEach(tableType => {
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

function openSubjectTab(evt, tabName) {
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
    fetch('/set_subjectspage_tab', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ subjectspage_current_tab: tabName })
    });
}

function openUserTab(evt, tabName) {
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
    fetch('/set_userspage_tab', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ userspage_current_tab: tabName })
    });
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

            if (table === 'subjects' && data.record.levels) {
                const levelSelect = form.querySelector('#subject_levels');
                if (levelSelect) {
                    Array.from(levelSelect.options).forEach(option => {
                        option.selected = data.record.levels.includes(option.value);
                    });
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

// Add this function to check for existing records
async function checkExistingRecord(table, key, value) {
    try {
        const response = await fetch(`/check_record_exists/${table}/${key}/${value}`);
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
            if (files.length > 0) {
                fileUploaded = true;
            }
            for (let file of files) {
                formData.append(input.name, file);
            }
        } else if (input.name === 'subject_levels' && input.multiple) {
            Array.from(input.selectedOptions).forEach(option => {
                formData.append(input.name, option.value);
            });
        } else {
            formData.append(input.name, input.value);
        }
    });

    // Validate form data
    const validationErrors = validateFormData(table, formData, fileUploaded);
    if (validationErrors.length > 0) {
        alert('Validation error(s):\n' + validationErrors.join('\n'));
        return;
    }

    if (mode === 'create') {
        try {
            // Special handling for subjects
            if (table === 'subjects') {
                const response = await fetch('/save_subject', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(formData)
                });
                
                const data = await response.json();
                if (data.success) {
                    alert('Subject created successfully');
                    window.location.reload(true);
                } else {
                    alert(data.error || 'Failed to create subject');
                }
                return;
            }
    
            // Original code for other tables
            const response = await fetch(`/api/create_record/${table}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
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
        let primaryKeyField;
        let primaryKeyValue;
        
        switch (table) {
            case 'subjects':
                primaryKeyField = 'subject_code';
                primaryKeyValue = formData.subject_code;
                break;
            case 'departments':
                primaryKeyField = 'department_code';
                primaryKeyValue = formData.department_code;
                break;
            case 'lecturers':
                primaryKeyField = 'ic_no';
                primaryKeyValue = formData.ic_no;
                break;
            case 'program_officers':
                primaryKeyField = 'email';
                primaryKeyValue = formData.email;
                break;         
            case 'hops':
                primaryKeyField = 'email';
                primaryKeyValue = formData.email;
                break;  
            case 'deans':
                primaryKeyField = 'email';
                primaryKeyValue = formData.email;
                break;  
        }

        // Only check for duplicates if the primary key has been changed
        const originalRecord = await fetch(`/get_record/${table}/${originalId}`).then(r => r.json());
        if (originalRecord.success && originalRecord.record[primaryKeyField] !== primaryKeyValue) {
            exists = await checkExistingRecord(table, primaryKeyField, primaryKeyValue);
            
            if (exists) {
                alert(`Cannot update record: A ${table.slice(0, -1)} with this ${primaryKeyField.replace(/_/g, ' ')} already exists.`);
                return;
            }
        }
    }

    // Add the id to formData for edit mode
    if (mode === 'edit') {
        formData.id = originalId;
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
            ? `/api/create_record/${table}` 
            : `/api/update_record/${table}/${originalId}`;

        const options = {
            method: mode === 'create' ? 'POST' : 'PUT',
            body: formData  // send FormData directly
        };

        try {
            const response = await fetch(url, options);
            const data = await response.json();
            if (data.success) {
                alert(data.message);
                window.location.reload(true);
            } else {
                alert('Error: ' + (data.message || 'Unknown error occurred'));
            }
        } catch (error) {
            alert('Error: ' + error.message);
        }
    }
});

// Helper function to create a select element
function createSelect(name, options, includeNA = false) {
    const select = document.createElement('select');
    select.name = name;
    select.required = true;
    
    if (includeNA) {
        const naOption = document.createElement('option');
        naOption.value = 'N/A';
        naOption.textContent = 'N/A';
        select.appendChild(naOption);
    }

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

// Helper function to fetch departments
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

function createFormFields(table, form) {
    return new Promise(async (resolve) => {
        const formFields = form.querySelector('#editFormFields');
        formFields.innerHTML = '';
        const fields = editableFields[table] || [];

        // Fetch departments if needed
        const needsDepartments = (table === 'lecturers' || table === 'program_officers' || table === 'hops' || table === 'deans') && fields.includes('department_code');
        const needsHops = (table === 'lecturers' && fields.includes('hop_id'));
        const needsDeans = (table === 'lecturers' && fields.includes('dean_id')) || (table === 'hops' && fields.includes('dean_id'));

        const departments = needsDepartments ? await getDepartments() : [];
        const hops = needsHops ? await getHops() : [];
        const deans = needsDeans ? await getDeans() : [];

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
            
            // Determine input type
            if (key === 'level') {
                input = createSelect(key, ['I', 'II', 'III']);
            } 
            else if (key === 'department_code' && departments.length > 0) {
                input = createSelect(key, departments, false);
            }
            else if (key === 'hop_id' && hops.length > 0) {
                input = createSelect(key, hops, true);
            }            
            else if (key === 'dean_id' && deans.length > 0) {
                 input = createSelect(key, deans, false);
            }
            else if (key === 'upload_file') {
                input = document.createElement('input');
                input.type = 'file';
                input.name = key;
                input.accept = 'application/pdf';
                input.multiple = true;
            }
            else if (table === 'subjects' && (key.includes('hours') || key.includes('weeks'))) {
                input = document.createElement('input');
                input.type = 'number';
                input.name = key;
                input.required = true;
            } else {
                input = document.createElement('input');
                input.type = 'text';
                input.name = key;
                input.required = true;
            }
            
            formGroup.appendChild(label);
            formGroup.appendChild(input);
            formFields.appendChild(formGroup);
        });

        // Add subject levels select for subjects table
        if (table === 'subjects') {
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
        }

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
    },

    // Function to validate positive integers
    isPositiveInteger: (value) => {
        return Number.isInteger(Number(value)) && Number(value) >= 0;
    }
};

// Add this validation function
function validateFormData(table, formData) {
    const errors = [];

    switch (table) {
        case 'subjects':
            // Validate subject code and title
            if (!fileUploaded && validationRules.hasInvalidSpecialChars(formData.subject_code)) {
                errors.push("Subject code contains invalid special characters");
            }
            if (!fileUploaded && validationRules.hasInvalidSpecialChars(formData.subject_title)) {
                errors.push("Subject title contains invalid special characters");
            }

            // Validate hours and weeks
            const numericFields = [
                'lecture_hours', 'tutorial_hours', 'practical_hours', 'blended_hours',
                'lecture_weeks', 'tutorial_weeks', 'practical_weeks', 'blended_weeks'
            ];

            numericFields.forEach(field => {
                if (!fileUploaded && !validationRules.isPositiveInteger(formData[field])) {
                    errors.push(`${field.replace(/_/g, ' ')} must be a positive integer`);
                }
            });
            break;
            
        case 'departments':
            // Convert department code to uppercase
            formData.department_code = formData.department_code.toUpperCase();
            
            // Check department name for special characters
            if (!fileUploaded && validationRules.hasInvalidSpecialChars(formData.department_name)) {
                errors.push("Department name contains invalid special characters");
            }
            break;

        case 'lecturers':
            // Validate lecturer name
            if (!fileUploaded && validationRules.hasInvalidSpecialChars(formData.name)) {
                errors.push("Lecturer name contains invalid special characters");
            }

            if (!fileUploaded && !validationRules.isValidEmail(formData.email)) {
                errors.push("Email must end with @newinti.edu.my");
            }
            
            if (!fileUploaded && !validationRules.isValidICNumber(formData.ic_no)) {
                errors.push("IC number must contain exactly 12 digits");
            }
            break;

        case 'program_officers':
        case 'hops':
        case 'deans':
            // Validate email format
            if (!fileUploaded && !validationRules.isValidEmail(formData.email)) {
                errors.push("Email must end with @newinti.edu.my");
            }
            break;
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
