document.addEventListener('DOMContentLoaded', function() {
    openTab(event, 'departments'); // Open the Departments tab by default
    loadAllTables();
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
            } else {
                alert('Failed to delete records');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred while deleting records');
        }
    });
});

function openTab(evt, tabName) {
    var i, tabContent, tabButtons;
    tabContent = document.getElementsByClassName("tab-content");
    for (i = 0; i < tabContent.length; i++) {
        tabContent[i].style.display = "none";
    }
    tabButtons = document.getElementsByClassName("tab-button");
    for (i = 0; i < tabButtons.length; i++) {
        tabButtons[i].className = tabButtons[i].className.replace(" active", "");
    }
    document.getElementById(tabName).style.display = "block";
    evt.currentTarget.className += " active";
}

function loadAllTables() {
    const tables = ['departments', 'lecturers', 'persons', 'programs', 'subjects'];
    tables.forEach(table => loadTable(table));
}

function loadTable(table) {
    fetch(`/api/${table}`)
        .then(response => response.json())
        .then(data => {
            const tableElement = document.getElementById(`${table}Table`);
            tableElement.innerHTML = ''; // Clear existing content

            // Create table header
            const thead = document.createElement('thead');
            const headerRow = document.createElement('tr');
            Object.keys(data[0]).forEach(key => {
                const th = document.createElement('th');
                th.textContent = key;
                headerRow.appendChild(th);
            });
            headerRow.innerHTML += '<th>Actions</th>';
            thead.appendChild(headerRow);
            tableElement.appendChild(thead);

            // Create table body
            const tbody = document.createElement('tbody');
            data.forEach(item => {
                const row = document.createElement('tr');
                Object.values(item).forEach(value => {
                    const td = document.createElement('td');
                    td.textContent = value;
                    row.appendChild(td);
                });
                const actionsTd = document.createElement('td');
                actionsTd.innerHTML = `
                    <button onclick="editRecord('${table}', ${item.id})">Edit</button>
                    <button onclick="deleteRecord('${table}', ${item.id})">Delete</button>
                `;
                row.appendChild(actionsTd);
                tbody.appendChild(row);
            });
            tableElement.appendChild(tbody);
        })
        .catch(error => console.error('Error loading table:', error));
}

function createRecord(table) {
    // Implement create functionality
    console.log(`Creating new record in ${table}`);
    // You can open a modal or redirect to a new page for creating a record
}

function editRecord(table, id) {
    fetch(`/api/${table}/${id}`)
        .then(response => response.json())
        .then(data => {
            const modal = document.getElementById('editModal');
            const formFields = document.getElementById('editFormFields');
            formFields.innerHTML = '';

            // Define editable fields for each table
            const editableFields = {
                'departments': ['department_code', 'department_name'],
                'lecturers': ['lecturer_name', 'email_address', 'level', 'hourly_rate', 'department_code'],
                'persons': ['email', 'department_code'],
                'programs': ['program_code', 'program_name', 'level', 'department_code'],
                'subjects': ['subject_code', 'subject_title', 'program_code', 'lecturer_id']
            };

            // Only create form fields for the specified editable fields
            const fields = editableFields[table] || [];
            fields.forEach(key => {
                if (data.hasOwnProperty(key)) {
                    const formGroup = document.createElement('div');
                    formGroup.className = 'form-group';
                    
                    const label = document.createElement('label');
                    label.textContent = key.replace(/_/g, ' ')
                                         .charAt(0).toUpperCase() + 
                                         key.slice(1).replace(/_/g, ' ');
                    
                    const input = document.createElement('input');
                    input.type = 'text';
                    input.name = key;
                    input.value = data[key] || '';
                    
                    formGroup.appendChild(label);
                    formGroup.appendChild(input);
                    formFields.appendChild(formGroup);
                }
            });

            // Store table and id for form submission
            const form = document.getElementById('editForm');
            form.dataset.table = table;
            form.dataset.id = id;

            modal.style.display = 'block';
        });
}

function deleteRecord(table, id) {
    if (confirm(`Are you sure you want to delete this record from ${table}?`)) {
        fetch(`/api/${table}/${id}`, { method: 'DELETE' })
            .then(response => {
                if (response.ok) {
                    loadTable(table); // Reload the table after successful deletion
                } else {
                    throw new Error('Failed to delete record');
                }
            })
            .catch(error => console.error('Error deleting record:', error));
    }
}

// File upload functionality
document.getElementById('fileUploadForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const formData = new FormData(this);
    
    fetch('/api/upload-preload-file', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('uploadStatus').textContent = data.message;
        if (data.success) {
            loadAllTables(); // Reload all tables after successful upload
        }
    })
    .catch(error => {
        console.error('Error uploading file:', error);
        document.getElementById('uploadStatus').textContent = 'Error uploading file';
    });
});

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
    
    const formData = new FormData(this);
    const data = Object.fromEntries(formData);
    const table = this.dataset.table;
    const id = this.dataset.id;

    fetch(`/api/${table}/${id}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            document.getElementById('editModal').style.display = 'none';
            alert(data.message || 'Changes saved successfully');
            // Refresh the entire page
            window.location.reload();
        } else {
            alert('Error updating record: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error updating record');
    });
});
