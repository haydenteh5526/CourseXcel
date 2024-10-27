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
