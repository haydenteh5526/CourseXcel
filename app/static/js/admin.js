document.addEventListener('DOMContentLoaded', function() {
    openTab(event, 'admins'); // Open the Admins tab by default
    loadAllTables();
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
    const tables = ['admins', 'departments', 'lecturers', 'persons', 'programs', 'subjects'];
    tables.forEach(table => loadTable(table));
}

function loadTable(table) {
    const tableElement = document.getElementById(`${table}Table`);
    if (!tableElement) {
        console.error(`Table element not found: ${table}Table`);
        return;
    }
    
    tableElement.innerHTML = '<div class="alert alert-info">Loading...</div>';
    
    fetch(`/api/${table}`)
        .then(response => response.json())
        .then(data => {
            console.log(`Loaded ${table} data:`, data); // Add this for debugging
            if (data && data.length > 0) {
                const thead = document.createElement('thead');
                const headerRow = document.createElement('tr');
                
                // Create headers
                Object.keys(data[0]).forEach(key => {
                    const th = document.createElement('th');
                    th.textContent = key;
                    headerRow.appendChild(th);
                });
                
                // Add Actions header
                const actionsHeader = document.createElement('th');
                actionsHeader.textContent = 'Actions';
                headerRow.appendChild(actionsHeader);
                
                thead.appendChild(headerRow);
                
                // Create table body
                const tbody = document.createElement('tbody');
                data.forEach(item => {
                    const row = document.createElement('tr');
                    Object.values(item).forEach(value => {
                        const td = document.createElement('td');
                        td.textContent = value;
                        row.appendChild(td);
                    });
                    
                    // Add action buttons
                    const actionsTd = document.createElement('td');
                    actionsTd.innerHTML = `
                        <button onclick="editItem('${table}', '${item.id}')">Edit</button>
                        <button onclick="deleteItem('${table}', '${item.id}')">Delete</button>
                    `;
                    row.appendChild(actionsTd);
                    
                    tbody.appendChild(row);
                });
                
                // Clear and update table
                tableElement.innerHTML = '';
                tableElement.appendChild(thead);
                tableElement.appendChild(tbody);
            } else {
                tableElement.innerHTML = '<div class="alert alert-info">No data available</div>';
            }
        })
        .catch(error => {
            console.error(`Error loading ${table}:`, error); // Add this for debugging
            tableElement.innerHTML = `<div class="alert alert-danger">Error loading data: ${error.message}</div>`;
        });
}

function createRecord(table) {
    // Implement create functionality
    console.log(`Creating new record in ${table}`);
    // You can open a modal or redirect to a new page for creating a record
}

function editRecord(table, id) {
    // Implement edit functionality
    console.log(`Editing record ${id} in ${table}`);
    // You can open a modal or redirect to a new page for editing a record
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

document.getElementById('uploadForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const formData = new FormData();
    const fileInput = document.getElementById('courseStructure');
    const levelSelect = document.getElementById('courseLevel');
    const statusDiv = document.getElementById('uploadStatus');
    
    formData.append('file', fileInput.files[0]);
    formData.append('level', levelSelect.value);
    
    // Show loading message
    statusDiv.innerHTML = '<div class="alert alert-info">Uploading and processing...</div>';
    
    fetch('/admin/upload-course-structure', methods=['POST'])
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Show success message
                statusDiv.innerHTML = `<div class="alert alert-success">${data.message}</div>`;
                
                // Clear the form
                fileInput.value = '';
                levelSelect.value = '';
                
                // Refresh the subjects table if it exists
                if (document.getElementById('subjectsTable')) {
                    loadTable('subjects');
                }
            } else {
                // Show error message
                statusDiv.innerHTML = `<div class="alert alert-danger">Error: ${data.error}</div>`;
            }
        })
        .catch(error => {
            console.error('Upload error:', error);
            statusDiv.innerHTML = `<div class="alert alert-danger">Error: ${error.message}</div>`;
        });
});
