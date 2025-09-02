document.addEventListener("DOMContentLoaded", function() {
    const titleElement = document.getElementById('page-title');
    const currentUrl = window.location.href;

    if (currentUrl.includes('admin')) {
        titleElement.textContent = 'Admin - CourseXcel';
    } else if (currentUrl.includes('lecturer')) {
        titleElement.textContent = 'Lecturer - CourseXcel';
    } else if (currentUrl.includes('po')) {
        titleElement.textContent = 'Program Officer - CourseXcel';
    } else {
        titleElement.textContent = 'CourseXcel';
    }
});

function togglePassword(inputId, button) {
    var input = document.getElementById(inputId);
    var icon = button.querySelector('i');

    if (input.type === 'password') {
        input.type = 'text';
        icon.classList.remove('fa-eye');
        icon.classList.add('fa-eye-slash');
    } else {
        input.type = 'password';
        icon.classList.remove('fa-eye-slash');
        icon.classList.add('fa-eye');
    }
}

function showChangePasswordModal() {
    const modal = document.getElementById('changePasswordModal');
    document.getElementById('new_password').value = '';
    document.getElementById('confirm_password').value = '';
    modal.style.display = 'block';
}

function closeChangePasswordModal() {
    const modal = document.getElementById('changePasswordModal');
    document.getElementById('new_password').value = '';
    document.getElementById('confirm_password').value = '';
    modal.style.display = 'none';
}

function submitChangePassword(role) {
    const password = document.getElementById('new_password').value;
    const confirmPassword = document.getElementById('confirm_password').value;

    if (password !== confirmPassword) {
        alert('Passwords do not match');
        return;
    }

    const data = {
        new_password: password,
        role: role
    };

    fetch('/api/change_password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Password changed successfully');
            document.getElementById('changePasswordForm').reset();
            closeChangePasswordModal();
        } else {
            alert(data.message || 'Failed to change password');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error changing password');
    });
}

function redirectHome(event) {
    event.preventDefault(); // Prevent default link behavior

    const logoLink = event.currentTarget; // The anchor tag clicked
    const poHomeUrl = logoLink.getAttribute('data-po-home');
    const lecturerHomeUrl = logoLink.getAttribute('data-lecturer-home');
    const adminHomeUrl = logoLink.getAttribute('data-admin-home');

    const currentUrl = window.location.href;

    if (currentUrl.includes('admin')) {
        window.location.href = adminHomeUrl;
    } else if (currentUrl.includes('lecturer')) {
        window.location.href = lecturerHomeUrl;
    } else if (currentUrl.includes('po')) {
        window.location.href = poHomeUrl;
    } 
}

function redirectLogout(event) {
    event.preventDefault(); // Prevent default link behavior

    const logoutButton = event.currentTarget;
    const poLogoutUrl = logoutButton.getAttribute('data-po-logout');
    const lecturerLogoutUrl = logoutButton.getAttribute('data-lecturer-logout');
    const adminLogoutUrl = logoutButton.getAttribute('data-admin-logout');

    const currentUrl = window.location.href;

    if (currentUrl.includes('admin')) {
        window.location.href = adminLogoutUrl;
    } else if (currentUrl.includes('lecturer')) {
        window.location.href = lecturerLogoutUrl;
    } else if (currentUrl.includes('po')) {
        window.location.href = poLogoutUrl;
    }
}

const pageKey = 'lastActiveTab_' + window.location.pathname;

function openAdminSubjectsTab(evt, tabName) {
    const tabContent = document.getElementsByClassName("tab-content");
    const tabButtons = document.getElementsByClassName("tab-button");

    Array.from(tabContent).forEach(tab => tab.style.display = "none");
    Array.from(tabButtons).forEach(button => button.classList.remove("active"));

    document.getElementById(tabName).style.display = "block";
    evt.currentTarget.classList.add("active");

    // Store current tab in localStorage (page-specific)
    localStorage.setItem(pageKey, tabName);

    // store in session via AJAX if you want server-side persistence
    fetch('/set_adminSubjectsPage_tab', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ adminSubjectsPage_currentTab: tabName })
    });
}

function openAdminUsersTab(evt, tabName) {
    const tabContent = document.getElementsByClassName("tab-content");
    const tabButtons = document.getElementsByClassName("tab-button");

    Array.from(tabContent).forEach(tab => tab.style.display = "none");
    Array.from(tabButtons).forEach(button => button.classList.remove("active"));

    document.getElementById(tabName).style.display = "block";
    evt.currentTarget.classList.add("active");

    // Store current tab in localStorage (page-specific)
    localStorage.setItem(pageKey, tabName);

    // store in session via AJAX if you want server-side persistence
    fetch('/set_adminUsersPage_tab', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ adminUsersPage_currentTab: tabName })
    });
}

function openAdminApprovalsTab(evt, tabName) {
    const tabContent = document.getElementsByClassName("tab-content");
    const tabButtons = document.getElementsByClassName("tab-button");

    Array.from(tabContent).forEach(tab => tab.style.display = "none");
    Array.from(tabButtons).forEach(button => button.classList.remove("active"));

    document.getElementById(tabName).style.display = "block";
    evt.currentTarget.classList.add("active");

    // Store current tab in localStorage (page-specific)
    localStorage.setItem(pageKey, tabName);

    // store in session via AJAX if you want server-side persistence
    fetch('/set_adminApprovalsPage_tab', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ adminApprovalsPage_currentTab: tabName })
    });
}

// When opening a tab
function openPoRecordsTab(evt, tabName) {
    const tabContent = document.getElementsByClassName("tab-content");
    const tabButtons = document.getElementsByClassName("tab-button");

    Array.from(tabContent).forEach(tab => tab.style.display = "none");
    Array.from(tabButtons).forEach(button => button.classList.remove("active"));

    document.getElementById(tabName).style.display = "block";
    evt.currentTarget.classList.add("active");

    // Store current tab in localStorage (page-specific)
    localStorage.setItem(pageKey, tabName);

    // Optional: store in session via AJAX if you want server-side persistence
    fetch('/set_poRecordsPage_tab', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ poRecordsPage_currentTab: tabName })
    });
}

function openPoApprovalsTab(evt, tabName) {
    const tabContent = document.getElementsByClassName("tab-content");
    const tabButtons = document.getElementsByClassName("tab-button");

    Array.from(tabContent).forEach(tab => tab.style.display = "none");
    Array.from(tabButtons).forEach(button => button.classList.remove("active"));

    document.getElementById(tabName).style.display = "block";
    evt.currentTarget.classList.add("active");

    // Store current tab in localStorage (page-specific)
    localStorage.setItem(pageKey, tabName);

    // store in session via AJAX if you want server-side persistence
    fetch('/set_poApprovalsPage_tab', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ poApprovalsPage_currentTab: tabName })
    });
}

function openLecturerRecordsTab(evt, tabName) {
    const tabContent = document.getElementsByClassName("tab-content");
    const tabButtons = document.getElementsByClassName("tab-button");

    Array.from(tabContent).forEach(tab => tab.style.display = "none");
    Array.from(tabButtons).forEach(button => button.classList.remove("active"));

    document.getElementById(tabName).style.display = "block";
    evt.currentTarget.classList.add("active");

    // Store current tab in localStorage (page-specific)
    localStorage.setItem(pageKey, tabName);

    // Optional: store in session via AJAX if you want server-side persistence
    fetch('/set_lecturerRecordsPage_tab', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ lecturerRecordsPage_currentTab: tabName })
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

function initApprovalsFiltersWithSearch(statusSelectorId, searchInputId) {
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

function initTableFiltersWithSearch(lecturerSelectorId, searchInputId) {
    const lecturerFilter = document.getElementById(lecturerSelectorId);
    const searchInput = document.getElementById(searchInputId);

    if (!lecturerFilter || !searchInput) return;

    const tableId = searchInput.dataset.table; 
    const rows = document.querySelectorAll(`#${tableId} tbody tr`);

    function applyFilters() {
        const selectedLecturer = lecturerFilter.value.toLowerCase();
        const searchTerm = searchInput.value.toLowerCase();

        rows.forEach(row => {
            const lecturer = row.getAttribute("data-lecturer")?.toLowerCase() || '';
            const text = row.textContent.toLowerCase();

            const matchLecturer = !selectedLecturer || lecturer.includes(selectedLecturer);
            const matchSearch = !searchTerm || text.includes(searchTerm);

            const shouldShow = matchLecturer && matchSearch;
            row.style.display = shouldShow ? "" : "none";
        });
    }

    lecturerFilter.addEventListener("change", applyFilters);
    searchInput.addEventListener("input", applyFilters);
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
            document.getElementById("loadingOverlay").style.display = "flex"; // or "block"

            const response = await fetch(`/api/delete_record/${tableType}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ ids: selectedIds })
            });
            
            document.getElementById("loadingOverlay").style.display = "none";

            if (response.ok) {
                // Remove deleted rows from the table
                selectedBoxes.forEach(box => box.closest('tr').remove());
                alert(`${selectedIds.length} record${deletedCount > 1 ? 's' : ''} deleted successfully`);
                window.location.reload(true);
            } else {
                const data = await response.json();
                alert(data.error || 'Failed to delete record(s)');
            }
        } catch (error) {
            document.getElementById("loadingOverlay").style.display = "none";
            alert('An error occurred while deleting record(s)');
        }
    });
});

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
                        const isMultiple = input.multiple;

                        if (isMultiple) {
                            const selectedValues = typeof value === 'string' ? value.split(',').map(v => v.trim()) : value;

                            Array.from(input.options).forEach(option => {
                                option.selected = selectedValues.includes(option.value);
                            });
                        } else {
                            Array.from(input.options).forEach(option => {
                                option.selected = option.value === String(value);
                            });
                        }
                    }
                    else {
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

function createFormFields(table, form) {
    return new Promise(async (resolve) => {
        const formFields = form.querySelector('#editFormFields');
        formFields.innerHTML = '';
        const fields = editableFields[table] || [];

        const needsHeads = (table === 'subjects' && fields.includes('head_id'));
        const needsDepartments = (table === 'lecturers' || table === 'heads' || table === 'programOfficers') && fields.includes('department_id');

        const heads = needsHeads ? await getHeads() : [];
        const departments = needsDepartments ? await getDepartments() : [];

        fields.forEach(key => {
            const formGroup = document.createElement('div');
            formGroup.className = 'form-group';
            
            const label = document.createElement('label');
            label.textContent = key
                .replace(/_/g, ' ')                        // replace underscores with spaces
                .replace(/\b\w/g, c => c.toUpperCase())    // capitalize each word
                .replace(/\bId\b/g, '')                    // remove the word 'Id' by replacing it with an empty string
                .trim()                                    // remove any extra spaces from the end
                + ':';                                     // add colon at the end

            let input;
            
            // Determine input type
            if (table === 'subjects' && key === 'subject_level') {
                input = createSelect(key, ['Certificate', 'Foundation', 'Diploma', 'Degree', 'Others']);
            } 
            else if (table === 'rates' && key === 'status') {
                input = createSelect(key, [
                    { label: 'Active',   value: '1' },
                    { label: 'Inactive', value: '0' }
                ]);
                }
            else if (key === 'head_id') {
                if (heads.length > 0) {
                    input = createSelect(key, heads);
                } else {
                    // If no heads exist, show a prompt to add one
                    input = createSelect(key, [
                        { label: '-', value: '' }
                    ]);
                    
                    const helperText = document.createElement('small');
                    helperText.style.display = 'block';
                    helperText.style.marginTop = '1px';
                    helperText.style.color = '#6c757d';
                    helperText.textContent = 'Please add a head to the database before proceeding.';

                    formGroup.appendChild(label);
                    formGroup.appendChild(input);
                    formGroup.appendChild(helperText);
                    formFields.appendChild(formGroup);
                    return; // prevent adding twice
                }
            } 
            else if (key === 'department_id' && departments.length > 0) {
                input = createSelect(key, departments);
            }  
            else if (table === 'lecturers' && key === 'level') {
                input = createSelect(key, ['I', 'II', 'III']);
            }   

            else if (table === 'heads' && key === 'level') {
                input = createSelect(key, ['Certificate', 'Foundation', 'Diploma', 'Degree', 'Others'], true);

                const helperText = document.createElement('small');
                helperText.style.display = 'block';
                helperText.style.marginTop = '1px';
                helperText.style.color = '#6c757d';
                helperText.textContent = 'Hold Ctrl / Cmd to select multiple options';

                formGroup.appendChild(label);
                formGroup.appendChild(input);
                formGroup.appendChild(helperText);
                formFields.appendChild(formGroup);
                return; // prevent adding twice
            }
   
            else if (key === 'upload_file' || key === 'upload_attachment') {
                input = document.createElement('input');
                input.type = 'file';
                input.name = key;
                input.accept = 'application/pdf';
                input.multiple = true;

                const helperText = document.createElement('small');
                helperText.style.display = 'block';
                helperText.style.marginTop = '1px';
                helperText.style.color = '#6c757d';
                helperText.textContent = 'Support selecting multiple files';

                formGroup.appendChild(label);
                formGroup.appendChild(input);
                formGroup.appendChild(helperText);
                formFields.appendChild(formGroup);
                return; // prevent adding twice

            }
            else if (table === 'subjects' && (key.includes('hours') || key.includes('weeks'))) {
                input = document.createElement('input');
                input.type = 'number';
                input.name = key;
                input.required = true;
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

// Helper function to create a select element
function createSelect(name, options, multiple = false, selectedValues = []) {
    const select = document.createElement('select');
    select.name = name;
    if (multiple) {
        select.multiple = true;
        select.size = options.length > 5 ? 5 : options.length;
    } else {
        select.required = true;
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
        if (selectedValues.includes(option.value)) {
            option.selected = true;
        }
        select.appendChild(option);
    });

    return select;
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
        } 
        else if (input.tagName === 'SELECT' && input.multiple) {
            const selected = Array.from(input.selectedOptions).map(opt => opt.value).join(', ');
            formData.append(input.name, selected);
        } 
        else {
            formData.append(input.name, input.value);
        }
    });

    // Validate form data
    const validationErrors = await validateFormData(table, formData);
    if (validationErrors.length > 0) {
        alert('Validation error(s):\n' + validationErrors.join('\n'));
        return;
    }

    if (mode === 'create') {
        try {
            document.getElementById("loadingOverlay").style.display = "flex"; // or "block"

            // Original code for other tables
            const response = await fetch(`/api/create_record/${table}`, {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            document.getElementById("loadingOverlay").style.display = "none";
            
            if (data.success) {
                alert('Record created successfully');
                window.location.reload(true);
            } else {
                alert(data.error || 'Failed to create record');
            }
        } catch (error) {
            document.getElementById("loadingOverlay").style.display = "none";
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
            case 'heads':    
            case 'programOfficers':
            case 'others':
                primaryKeyField = 'email';
                primaryKeyValue = formData.email;
                break;      
        }

        // Only check for duplicates if the primary key has been changed
        const originalRecord = await fetch(`/get_record/${table}/${originalId}`).then(r => r.json());
        if (originalRecord.success && originalRecord.record[primaryKeyField] !== primaryKeyValue) {
            exists = await checkExistingRecord(table, primaryKeyValue);
            
            if (exists) {
                alert(`Cannot update record: A ${table.slice(0, -1)} with this ${primaryKeyField.replace(/_/g, ' ')} already exists.`);
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
            document.getElementById("loadingOverlay").style.display = "none";
            if (data.success) {
                alert(data.message || 'Record updated successfully');

                // Before reload
                const pageKey = 'lastActiveTab_' + window.location.pathname;
                const currentTab = document.querySelector('.tab-button.active').getAttribute('onclick').match(/'(\w+)'/)[1];
                localStorage.setItem(pageKey, currentTab);

                // Then reload
                window.location.reload();

            } else {
                alert('Error: ' + (data.message || 'Failed to update record'));
            }
        })
        .catch(error => {
            document.getElementById("loadingOverlay").style.display = "none";
            alert('Error: ' + error.message);
        });
    }
});

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
async function validateFormData(table, formData) {
    const errors = [];

    switch (table) {
        case 'subjects':
            // Validate subject code and title
            if (validationRules.hasInvalidSpecialChars(formData.get('subject_code'))) {
                errors.push("Subject code contains invalid special characters");
            }
            if (validationRules.hasInvalidSpecialChars(formData.get('subject_title'))) {
                errors.push("Subject title contains invalid special characters");
            }

            // Validate hours and weeks
            const numericFields = [
                'lecture_hours', 'tutorial_hours', 'practical_hours', 'blended_hours',
                'lecture_weeks', 'tutorial_weeks', 'practical_weeks', 'blended_weeks'
            ];

            numericFields.forEach(field => {
                if (!validationRules.isPositiveInteger(formData.get(field))) {
                    errors.push(`${field.replace(/_/g, ' ')} must be a positive integer`);
                }
            });
            break;
        
       case 'rates':
            if (!validationRules.isPositiveInteger(formData.get('amount'))) {
                errors.push('Amount must be a positive integer');
            }
            break;

        case 'departments':
            // Convert department code to uppercase
            formData.set('department_code', formData.get('department_code').toUpperCase());
            
            // Check department name for special characters 
            if (validationRules.hasInvalidSpecialChars(formData.get('department_name'))) {
                errors.push("Department name contains invalid special characters");
            }

            if (validationRules.hasInvalidSpecialChars(formData.get('dean_name'))) {
                errors.push("Dean name contains invalid special characters");
            }

            if (!validationRules.isValidEmail(formData.get('dean_email'))) {
                errors.push("Email must end with @newinti.edu.my");
            }
            break;

        case 'lecturers':
            // Validate lecturer name
            if (validationRules.hasInvalidSpecialChars(formData.get('name'))) {
                errors.push("Lecturer name contains invalid special characters");
            }

            if (!validationRules.isValidEmail(formData.get('email'))) {
                errors.push("Email must end with @newinti.edu.my");
            }
            
            if (!validationRules.isValidICNumber(formData.get('ic_no'))) {
                errors.push("IC number must contain exactly 12 digits");
            }
            break;

        case 'heads':
        case 'programOfficers':
        case 'others':
            // Validate email format
            if (!validationRules.isValidEmail(formData.get('email'))) {
                errors.push("Email must end with @newinti.edu.my");
            }
            break;
    }

    return errors;
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

// Helper function to fetch heads
async function getHeads() {
    try {
        const response = await fetch('/get_heads');
        const data = await response.json();
        if (data.success) {
            return data.heads.map(head => ({
                value: head.head_id,
                label: `${head.name}`
            }));
        }
        return [];
    } catch (error) {
        console.error('Error fetching heads:', error);
        return [];
    }
}

// Helper function to fetch departments
async function getDepartments() {
    try {
        const response = await fetch('/get_departments');
        const data = await response.json();
        if (data.success) {
            return data.departments.map(dept => ({
                value: dept.department_id,
                label: `${dept.department_code} - ${dept.department_name}`
            }));
        }
        return [];
    } catch (error) {
        console.error('Error fetching departments:', error);
        return [];
    }
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
