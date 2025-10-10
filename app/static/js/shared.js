// Page Title Setter on Load
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

// Toggle Password Visibility 
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

// Change Password Modal Helpers
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

// Submit Change Password to backend
function submitChangePassword(role) {
    const password = document.getElementById('new_password').value;
    const confirmPassword = document.getElementById('confirm_password').value;

    if (password !== confirmPassword) {
        alert('Passwords do not match.');
        return;
    }

    const data = {
        new_password: password,
        role: role
    };

    console.log("[SHARED] Fetch initiated:", `/api/change_password`);

    fetch('/api/change_password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        console.log("[SHARED] Fetch success response received:", data);

        if (data.success) {
            console.log("[SHARED] Password changed successfully for role:", role);
            alert('Password changed successfully.');
            document.getElementById('changePasswordForm').reset();
            closeChangePasswordModal();
        } else {
            console.warn("[SHARED] Password change failed:", data.message || "Unknown error.");
            alert(data.message || 'Failed to change password.');
        }
    })
    .catch(error => {
        console.error("[SHARED] Error occurred during password change:", error);
        alert('An error occurred while changing the password. Please try again later.');
    });
}

// Homepage Redirects
function redirectHome(event) {
    event.preventDefault(); // Prevent default link behavior

    const logoLink = event.currentTarget; // The anchor tag clicked
    const adminHomeUrl = logoLink.getAttribute('data-admin-home');
    const lecturerHomeUrl = logoLink.getAttribute('data-lecturer-home');
    const poHomeUrl = logoLink.getAttribute('data-po-home');

    const currentUrl = window.location.href;

    if (currentUrl.includes('admin')) {
        window.location.href = adminHomeUrl;
    } else if (currentUrl.includes('lecturer')) {
        window.location.href = lecturerHomeUrl;
    } else if (currentUrl.includes('po')) {
        window.location.href = poHomeUrl;
    } 
}

// Key for remembering last active tab per-page (path-specific)
const pageKey = 'lastActiveTab_' + window.location.pathname;

// Admin Tab Switchers
function openAdminSubjectsTab(evt, tabName) {
    const tabContent = document.getElementsByClassName("tab-content");
    const tabButtons = document.getElementsByClassName("tab-button");

    Array.from(tabContent).forEach(tab => tab.style.display = "none");
    Array.from(tabButtons).forEach(button => button.classList.remove("active"));

    document.getElementById(tabName).style.display = "block";
    evt.currentTarget.classList.add("active");

    // Store current tab in localStorage (page-specific)
    localStorage.setItem(pageKey, tabName);

    // store in session via AJAX
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

    // store in session via AJAX
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

    // store in session via AJAX
    fetch('/set_adminApprovalsPage_tab', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ adminApprovalsPage_currentTab: tabName })
    });
}

function openAdminReportsTab(evt, tabName) {
    const tabContent = document.getElementsByClassName("tab-content");
    const tabButtons = document.getElementsByClassName("tab-button");

    Array.from(tabContent).forEach(tab => tab.style.display = "none");
    Array.from(tabButtons).forEach(button => button.classList.remove("active"));

    document.getElementById(tabName).style.display = "block";
    evt.currentTarget.classList.add("active");

    // Store current tab in localStorage (page-specific)
    localStorage.setItem(pageKey, tabName);

    // store in session via AJAX
    fetch('/set_adminReportsPage_tab', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ adminReportsPage_currentTab: tabName })
    });
}

// PO Tab Switchers
function openPoRecordsTab(evt, tabName) {
    const tabContent = document.getElementsByClassName("tab-content");
    const tabButtons = document.getElementsByClassName("tab-button");

    Array.from(tabContent).forEach(tab => tab.style.display = "none");
    Array.from(tabButtons).forEach(button => button.classList.remove("active"));

    document.getElementById(tabName).style.display = "block";
    evt.currentTarget.classList.add("active");

    // Store current tab in localStorage (page-specific)
    localStorage.setItem(pageKey, tabName);

    // Optional: store in session via AJAX
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

    // store in session via AJAX
    fetch('/set_poApprovalsPage_tab', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ poApprovalsPage_currentTab: tabName })
    });
}

// Lecturer Tab Switchers
function openLecturerApprovalsTab(evt, tabName) {
    const tabContent = document.getElementsByClassName("tab-content");
    const tabButtons = document.getElementsByClassName("tab-button");

    Array.from(tabContent).forEach(tab => tab.style.display = "none");
    Array.from(tabButtons).forEach(button => button.classList.remove("active"));

    document.getElementById(tabName).style.display = "block";
    evt.currentTarget.classList.add("active");

    // Store current tab in localStorage (page-specific)
    localStorage.setItem(pageKey, tabName);

    // Optional: store in session via AJAX
    fetch('/set_lecturerClaimsPage_tab', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ lecturerClaimsPage_currentTab: tabName })
    });
}

// Filter table rows, mark matches, reset to page 1, and refresh pagination
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

// Binds a status dropdown and a search box to show/hide rows
function initStatusFilterWithSearch(statusSelectorId, searchInputId) {
    const statusFilter = document.getElementById(statusSelectorId);
    const searchInput = document.getElementById(searchInputId);
    if (!statusFilter || !searchInput) return;

    const tableId = searchInput.dataset.table; 
    const rows = document.querySelectorAll(`#${tableId} tbody tr`);
    const EPS = 1e-6;

    function getRowStatus(row) {
        // Prefer explicit data-status from backend (e.g., Pending/Voided/Rejected/Completed).
        let s = (row.getAttribute('data-status') || '').trim();
        if (s) return s; // e.g., "Pending", "Voided", "Rejected", "Completed"

        // Fallback: derive status from total (≈0 => Completed; otherwise Pending).
        const totalStr = row.getAttribute('data-total');
        const total = totalStr != null ? parseFloat(totalStr) : NaN;
        if (!Number.isNaN(total) && Math.abs(total) < EPS) return 'Fully Claimed';
        return 'Outstanding';
    }

    function applyFilters() {
        const selectedStatus = statusFilter.value.trim().toLowerCase(); // "", "pending", "voided", "rejected", "completed"
        const searchTerm = searchInput.value.toLowerCase();

        rows.forEach(row => {
            const rowStatus = getRowStatus(row).toLowerCase();
            const text = row.textContent.toLowerCase();

            const matchStatus = !selectedStatus || rowStatus.includes(selectedStatus);
            const matchSearch = !searchTerm || text.includes(searchTerm);

            row.style.display = (matchStatus && matchSearch) ? "" : "none";
        });
    }

    statusFilter.addEventListener("change", applyFilters);
    searchInput.addEventListener("input", applyFilters);

    // Initial run to respect default selections
    applyFilters();
}

// Binds a lecturer dropdown and a search box to show/hide rows
function initLecturerFilterWithSearch(lecturerSelectorId, searchInputId) {
    const lecturerFilter = document.getElementById(lecturerSelectorId);
    const searchInput = document.getElementById(searchInputId);
    if (!lecturerFilter || !searchInput) return;

    const tableId = lecturerFilter.dataset.tableId || searchInput.dataset.table;
    const rows = document.querySelectorAll(`#${tableId} tbody tr`);

    function applyFilters() {
        const selectedLecturer = lecturerFilter.value.trim().toLowerCase();
        const searchTerm = searchInput.value.trim().toLowerCase();

        rows.forEach(row => {
            const rowLecturer = row.getAttribute("data-lecturer")?.toLowerCase() || '';
            const text = row.textContent.toLowerCase();

            const matchLecturer = !selectedLecturer || rowLecturer === selectedLecturer;
            const matchSearch = !searchTerm || text.includes(searchTerm);

            row.style.display = (matchLecturer && matchSearch) ? "" : "none";
        });
    }

    lecturerFilter.addEventListener('change', applyFilters);
    searchInput.addEventListener('input', applyFilters);

    applyFilters();
}

// Binds a lecturer dropdown and a status dropdown to show/hide rows
function initLecturerStatusFilters(lecturerSelectorId, statusSelectorId) {
    const lecturerFilter = document.getElementById(lecturerSelectorId);
    const statusFilter = document.getElementById(statusSelectorId);
    if (!lecturerFilter || !statusFilter) return;

    const tableId = lecturerFilter.dataset.tableId || statusFilter.dataset.tableId;
    const rows = document.querySelectorAll(`#${tableId} tbody tr`);
    const EPS = 1e-9; // treat tiny totals as zero

    function getRowTotal(row) {
        const val = row.getAttribute('data-total');
        const n = val != null ? parseFloat(val) : NaN;
        return Number.isNaN(n) ? 0 : n;
    }

    function applyFilters() {
        const selectedLecturer = (lecturerFilter.value || '').trim().toLowerCase(); // exact match
        const selectedStatus = (statusFilter.value || '').trim().toLowerCase(); // '', 'fully-claimed', 'outstanding'

        rows.forEach(row => {
            const rowLecturer = (row.getAttribute('data-lecturer') || '').toLowerCase();
            const total = getRowTotal(row);
            const isFullyClaimed = Math.abs(total) < EPS;
            const normalizedStatus = isFullyClaimed ? 'fully-claimed' : 'outstanding';

            const matchLecturer = !selectedLecturer || rowLecturer === selectedLecturer;
            const matchStatus = !selectedStatus || selectedStatus === normalizedStatus;

            row.style.display = (matchLecturer && matchStatus) ? '' : 'none';
        });
    }

    lecturerFilter.addEventListener('change', applyFilters);
    statusFilter.addEventListener('change', applyFilters);

    // Initial run to respect default selections
    applyFilters();
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
            document.getElementById("loadingOverlay").style.display = "flex";
            console.log("[SHARED] Fetch initiated:", `/api/delete_record/${tableType}`);

            const response = await fetch(`/api/delete_record/${tableType}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ ids: selectedIds })
            });
            
            document.getElementById("loadingOverlay").style.display = "none";
            console.log("[ADMIN] Fetch response received.");

            if (response.ok) {
                // Remove deleted rows from the table
                selectedBoxes.forEach(box => box.closest('tr').remove());
                alert(`${selectedIds.length} record${selectedIds.length > 1 ? 's' : ''} deleted successfully`);

                // Before reload
                const pageKey = 'lastActiveTab_' + window.location.pathname;
                const currentTab = document.querySelector('.tab-button.active').getAttribute('onclick').match(/'(\w+)'/)[1];
                localStorage.setItem(pageKey, currentTab);

                // Then reload
                window.location.reload();
            } else {
                const data = await response.json();
                console.warn("[ADMIN] Deletion failed:", data.error || "Unknown error.");
                alert(data.error || 'Failed to delete record(s).');
            }
        } catch (error) {
            document.getElementById("loadingOverlay").style.display = "none";
            console.error("[ADMIN] Error occurred during deletion:", error);
            alert('An error occurred while deleting record(s): ' + error.message);
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

// Shows the modal in create mode by generating fields for the target table
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

// Fetches a record by id, builds the form fields, populates values, and opens the modal in edit mode
async function editRecord(table, id) {
    try {
        console.log("[SHARED] Fetch initiated:", `/get_record/${table}/${id}`);
        const response = await fetch(`/get_record/${table}/${id}`);
        const data = await response.json();

        if (data.success) {
            console.log("[SHARED] Fetch success response received:", data);

            const modal = document.getElementById('editModal');
            const form = document.getElementById('editForm');

            form.dataset.table = table;
            form.dataset.id = id;
            form.dataset.mode = 'edit';

            // Wait for form fields to be created before continuing
            console.log(`[SHARED] Generating form fields for table: ${table}`);
            await createFormFields(table, form);

            // Ppopulate the fields
            console.log("[SHARED] Populating record data into form fields...");
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
            console.log("[SHARED] Edit modal opened successfully for record ID:", id);
        } else {
            console.warn("[SHARED] Failed to retrieve record data:", data.message || "No data returned.");
            alert('Error: ' + (data.message || 'Failed to load record data.'));
        }
    } catch (error) {
        console.error("[SHARED] Error in editRecord:", error);
        alert('An error occurred while loading record: ' + error.message);
    }
}

// Dynamically builds form inputs for a table
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
                    // if no heads exist
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

// Create a select element
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

// Form submission event listener
document.getElementById('editForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    const table = this.dataset.table;
    const mode = this.dataset.mode;
    const formData = new FormData();
    const originalId = this.dataset.id;  // Store the original record ID
    
    // Collect form data
    const inputs = this.querySelectorAll('input, select');
    inputs.forEach(input => {
        if (input.tagName === 'SELECT' && input.multiple) {
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
            document.getElementById("loadingOverlay").style.display = "flex";
            console.log("[SHARED] Fetch initiated:", `/api/create_record/${table}`);

            const response = await fetch(`/api/create_record/${table}`, {
                method: 'POST',
                body: formData
            });       

            const data = await response.json();
            document.getElementById("loadingOverlay").style.display = "none";
            console.log("[SHARED] Fetch success response received:", data);
            
            if (data.success) {
                alert('Record created successfully');

                // Before reload
                const pageKey = 'lastActiveTab_' + window.location.pathname;
                const currentTab = document.querySelector('.tab-button.active').getAttribute('onclick').match(/'(\w+)'/)[1];
                localStorage.setItem(pageKey, currentTab);

                // Then reload
                window.location.reload();
            } else {
                console.warn("[SHARED] Record creation failed:", data.error || data.message);
                alert(data.error || 'Failed to create record.');
            }
        } catch (error) {
            document.getElementById("loadingOverlay").style.display = "none";
            console.error("[SHARED] Error creating record:", error);
            alert('Error creating record: ' + error.message);
        }
        return;
    }

    // Check for duplicate primary keys when editing
    if (mode === 'edit') {
        try {
            console.log("[SHARED] Fetch initiated:", `/get_record/${table}/${originalId}`);
            const originalRecord = await fetch(`/get_record/${table}/${originalId}`).then(r => r.json());
            let primaryKeys = [];

            // Identify primary keys for duplicate checking
            switch (table) {
                case 'subjects':
                    primaryKeys = [{ field: 'subject_code', value: formData.get('subject_code') }];
                    break;
                case 'departments':
                    primaryKeys = [
                        { field: 'department_code', value: formData.get('department_code') },
                        { field: 'dean_email', value: formData.get('dean_email') }
                    ];
                    break;
                case 'lecturers':
                    primaryKeys = [
                        { field: 'ic_no', value: formData.get('ic_no') },
                        { field: 'email', value: formData.get('email') }
                    ];
                    break;
                case 'heads':
                case 'programOfficers':
                case 'others':
                    primaryKeys = [{ field: 'email', value: formData.get('email') }];
                    break;
            }

            // Duplicate checking only if fields changed
            if (originalRecord.success) {
                for (const { field, value } of primaryKeys) {
                    if (originalRecord.record[field] !== value) {
                        const exists = await checkExistingRecord(table, field, value);
                        if (exists) {
                            alert(`Cannot update record: A ${table.slice(0, -1)} with this ${field.replace(/_/g, ' ')} already exists.`);
                            return;
                        }
                    }
                }
            }

            // Attach ID for update
            formData.set('id', originalId);

            console.log("[SHARED] Fetch initiated:", `/api/update_record/${table}/${originalId}`);
            document.getElementById("loadingOverlay").style.display = "flex";

            const response = await fetch(`/api/update_record/${table}/${originalId}`, {
                method: 'PUT',
                body: formData
            });

            const data = await response.json();
            document.getElementById("loadingOverlay").style.display = "none";
            console.log("[SHARED] Fetch success response received:", data);

            if (data.success) {
                alert('Record updated successfully.');

                const pageKey = 'lastActiveTab_' + window.location.pathname;
                const currentTab = document.querySelector('.tab-button.active')?.getAttribute('onclick')?.match(/'(\w+)'/)[1];
                if (currentTab) localStorage.setItem(pageKey, currentTab);

                window.location.reload();
            } else {
                console.warn("[SHARED] Record update failed:", data.message || "Unknown error.");
                alert('Error: ' + (data.message || 'Failed to update record.'));
            }
        } catch (error) {
            document.getElementById("loadingOverlay").style.display = "none";
            console.error("[SHARED] Error updating record:", error);
            alert('Error updating record: ' + error.message);
        }
    }
});

// Reusable helpers for validation
const validationRules = {
    // Check for invalid special characters in text
    hasInvalidSpecialChars: (text) => {
        // Allow letters, numbers, spaces, dots, commas, hyphens, and parentheses
        const invalidCharsRegex = /[^a-zA-Z0-9\s.,\-()]/;
        return invalidCharsRegex.test(text);
    },

    // Validate that email ends with @newinti.edu.my
    isValidEmail: (email) => {
        const emailRegex = /^[a-zA-Z0-9._%+-]+@newinti\.edu\.my$/;
        return emailRegex.test(email);
    },

    // Validate IC number (12 digits only)
    isValidICNumber: (ic) => {
        return /^\d{12}$/.test(ic);
    },

    // Validate positive integers
    isPositiveInteger: (value) => {
        return Number.isInteger(Number(value)) && Number(value) >= 0;
    }
};

// Validation function
async function validateFormData(table, formData) {
    const errors = [];

    switch (table) {
        case 'subjects':
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

// Queries backend to see if a record with the given primary key already exists to prevent duplicates on edit
async function checkExistingRecord(table, field, value) {
    try {
        const url = `/api/check_record_exists/${encodeURIComponent(table)}?field=${encodeURIComponent(field)}&value=${encodeURIComponent(value)}`;
        console.log("[SHARED] Fetch initiated:", url);
        const res = await fetch(url);
        const data = await res.json();
        return !!data.exists;
    } catch (err) {
        console.error("[SHARED] Error checking record existence:", err);
        return false;
    }
}

function closeEditModal() {
    const modal = document.getElementById('editModal');
    modal.style.display = 'none';
}

// Fetch heads list from backend
async function getHeads() {
    const url = '/get_heads';
    try {
        console.log("[SHARED] Fetch initiated:", url);
        const response = await fetch(url);
        const data = await response.json();

        if (data.success && Array.isArray(data.heads)) {
            console.log(`[SHARED] ${data.heads.length} head(s) retrieved successfully.`);
            return data.heads.map(head => ({
                value: head.head_id,
                label: `${head.name}`
            }));
        } else {
            console.warn("[SHARED] No heads data available or invalid response format.");
            return [];
        }
    } catch (error) {
        console.error("[SHARED] Error fetching heads:", error);
        return [];
    }
}

// Fetch departments from backend
async function getDepartments() {
    const url = '/get_departments';
    try {
        console.log("[SHARED] Fetch initiated:", url);
        const response = await fetch(url);
        const data = await response.json();

        if (data.success && Array.isArray(data.departments)) {
            console.log(`[SHARED] ${data.departments.length} department(s) retrieved successfully.`);
            return data.departments.map(dept => ({
                value: dept.department_id,
                label: `${dept.department_code} - ${dept.department_name}`
            }));
        } else {
            console.warn("[SHARED] No department data available or invalid response format.");
            return [];
        }
    } catch (error) {
        console.error("[SHARED] Error fetching departments:", error);
        return [];
    }
}

// Handle pagination
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

function fitSignatureCanvas(canvas) {
    const ratio = Math.max(window.devicePixelRatio || 1, 1);
    const rect = canvas.getBoundingClientRect();

    // Set the canvas internal pixel size to match CSS size × DPR
    canvas.width  = Math.round(rect.width  * ratio);
    canvas.height = Math.round(rect.height * ratio);

    // Scale the drawing context so 1 unit = 1 CSS pixel
    const ctx = canvas.getContext('2d');
    ctx.setTransform(ratio, 0, 0, ratio, 0, 0); // better than scale() repeatedly
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

    // Wait a frame so layout is updated and the canvas has measurable size
    requestAnimationFrame(() => {
        const canvas = document.getElementById("signature-pad"); // note: hyphen id
        fitSignatureCanvas(canvas);

        signaturePad = new SignaturePad(canvas, {
            minWidth: 0.8,
            maxWidth: 2.0,
            penColor: "#000"
        });

        // Keep it crisp if the window resizes
        window.addEventListener("resize", () => fitSignatureCanvas(canvas), { passive: true });
    });
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
