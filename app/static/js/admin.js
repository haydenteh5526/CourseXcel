// Define which fields are editable per table type
const editableFields = {
    'subjects': [
        'subject_code',
        'subject_title',
        'subject_level',
        'head_id',
        'lecture_hours',
        'tutorial_hours',
        'practical_hours',
        'blended_hours',
        'lecture_weeks',
        'tutorial_weeks',
        'practical_weeks',
        'blended_weeks'
    ],
    'rates': ['amount', 'status'],
    'departments': ['department_code', 'department_name', 'dean_name', 'dean_email'],
    'lecturers': ['name', 'email', 'ic_no', 'level', 'department_id'],
    'heads': ['name', 'email', 'level', 'department_id'],
    'programOfficers': ['name', 'email', 'department_id'],
    'others': ['name', 'email', 'role']
};

// Pagination constants
const RECORDS_PER_PAGE = 20; // max rows per page
let currentPages = {
    'subjects': 1,
    'rates': 1,
    'departments': 1,
    'lecturers': 1,
    'heads': 1,
    'programOfficers': 1,
    'others': 1,
    'requisitionApprovals': 1,
    'requisitionAttachments': 1,
    'claimApprovals': 1,
    'claimAttachments': 1,
    'claimDetails': 1
};

// Table Filters (Department + Status)
function initTableFilters(deptSelectorId, statusSelectorId) {
    const departmentFilter = document.getElementById(deptSelectorId);
    const statusFilter = document.getElementById(statusSelectorId);
    if (!departmentFilter || !statusFilter) return;

    const tableId = departmentFilter.dataset.tableId; // table ID is linked via data attribute
    const rows = document.querySelectorAll(`#${tableId} tbody tr`);

    // Mark all rows as searchable initially
    rows.forEach(row => {
        row.dataset.searchMatch = 'true';
    });

    function applyFilters() {
        const selectedDept = departmentFilter.value.toLowerCase();
        const selectedStatus = statusFilter.value.toLowerCase();

        rows.forEach(row => {
            // Row has data attributes for department and status
            const dept = row.getAttribute("data-department")?.toLowerCase() || '';
            const status = row.getAttribute("data-status")?.toLowerCase() || '';

            // Match logic (blank filter = match all)
            const matchDept = !selectedDept || dept === selectedDept;
            const matchStatus = !selectedStatus || status.includes(selectedStatus);

            // Show/hide rows
            row.style.display = (matchDept && matchStatus) ? "" : "none";
        });
    }

    // Attach listeners
    departmentFilter.addEventListener("change", applyFilters);
    statusFilter.addEventListener("change", applyFilters);

    // Initial run to respect default selections
    applyFilters();
}

// Course Structure Upload Form
function setupCourseStructureForm() {
    const uploadCourseStructure = document.getElementById('uploadCourseStructure');
    if (uploadCourseStructure && !uploadCourseStructure.dataset.listenerAttached) {
        uploadCourseStructure.addEventListener('submit', function (e) {
            e.preventDefault();

            // Ensure file is selected
            const file = document.getElementById('courseStructure').files[0];
            if (!file) {
                alert('Please select a file');
                return;
            }

            // Show loading overlay
            document.getElementById("loadingOverlay").style.display = "flex";

            const formData = new FormData(this);
            fetch('/upload_subjects', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById("loadingOverlay").style.display = "none";
                if (data.success) {
                    alert(data.message);

                    // Show warnings if any
                    if (data.warnings) {
                        data.warnings.forEach(warning => {
                            alert('Warning: ' + warning);
                        });
                    }

                    // Update timestamp if at least 1 record processed
                    if (data.message.includes('Successfully processed')) {
                        const currentDate = new Date();
                        const formattedDate = currentDate.toLocaleString('en-GB', {
                            weekday: 'short', year: '2-digit', month: 'short', day: '2-digit',
                            hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: true
                        });
                        localStorage.setItem('csLastUploaded', formattedDate);
                    }
                    
                    // Refresh page to show updates
                    window.location.reload(true);
                } else {
                    // Show errors
                    alert(data.message || 'Upload failed');
                    if (data.errors) {
                        data.errors.forEach(error => {
                            alert('Error: ' + error);
                        });
                    }
                }
            })
            .catch(error => {
                document.getElementById("loadingOverlay").style.display = "none";
                alert('Upload failed: ' + error.message);
            });

            // Prevent attaching listener multiple times
            uploadCourseStructure.dataset.listenerAttached = "true";
        });
    }
}

// Lecturer Upload Form
function setupLecturerForm() {
    const uploadLecturerList = document.getElementById('uploadLecturerList');    
    if (uploadLecturerList && !uploadLecturerList.dataset.listenerAttached) {
        uploadLecturerList.addEventListener('submit', function(e) {
            e.preventDefault();

            // Ensure file is selected
            const file = document.getElementById('lecturerList').files[0];
            if (!file) {
                alert('Please select a file');
                return;
            }

            document.getElementById("loadingOverlay").style.display = "flex";

            const formData = new FormData(this);
            fetch('/upload_lecturers', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById("loadingOverlay").style.display = "none";
                if (data.success) {
                    alert(data.message);

                    // Show warnings if any
                    if (data.warnings) {
                        data.warnings.forEach(warning => alert('Warning: ' + warning));
                    }

                    // Update timestamp if at least 1 lecturer processed
                    if (data.message.includes('Successfully processed')) {
                        const currentDate = new Date();
                        const formattedDate = currentDate.toLocaleString('en-GB', {
                            weekday: 'short', year: '2-digit', month: 'short', day: '2-digit',
                            hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: true
                        });
                        localStorage.setItem('lecturerLastUploaded', formattedDate);
                    }
                    
                    window.location.reload(true);
                } else {
                    alert(data.message || 'Upload failed.');
                    if (data.errors) {
                        data.errors.forEach(error => {
                            alert('Error: ' + error);
                        });
                    }
                }
            })
            .catch(error => {
                document.getElementById("loadingOverlay").style.display = "none";
                alert('Upload failed: ' + error.message);
            });

        });
        uploadLecturerList.dataset.listenerAttached = "true";
    }
}

// Head Upload Form
function setupHeadForm() {
    const uploadHeadList = document.getElementById('uploadHeadList');    
    if (uploadHeadList && !uploadHeadList.dataset.listenerAttached) {
        uploadHeadList.addEventListener('submit', function(e) {
            e.preventDefault();

            const file = document.getElementById('headList').files[0];
            if (!file) {
                alert('Please select a file');
                return;
            }

            document.getElementById("loadingOverlay").style.display = "flex";

            const formData = new FormData(this);
            fetch('/upload_heads', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById("loadingOverlay").style.display = "none";
                if (data.success) {
                    alert(data.message);
                    if (data.warnings) {
                        data.warnings.forEach(warning => alert('Warning: ' + warning));
                    }

                    // Update timestamp if at least 1 head processed
                    if (data.message.includes('Successfully processed')) {
                        const currentDate = new Date();
                        const formattedDate = currentDate.toLocaleString('en-GB', {
                            weekday: 'short', year: '2-digit', month: 'short', day: '2-digit',
                            hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: true
                        });
                        localStorage.setItem('headLastUploaded', formattedDate);
                    }
                    
                    window.location.reload(true);
                } else {
                    alert(data.message || 'Upload failed');
                    if (data.errors) {
                        data.errors.forEach(error => {
                            alert('Error: ' + error);
                        });
                    }
                }
            })
            .catch(error => {
                document.getElementById("loadingOverlay").style.display = "none";
                alert('Upload failed: ' + error.message);
            });

        });
        uploadHeadList.dataset.listenerAttached = "true";
    }
}

// Change Rate Status (Active <-> Inactive)
async function changeRateStatus(table, id) {
    try {
        // Verify record exists before attempting update
        const check = await fetch(`/get_record/${table}/${id}`);
        const data = await check.json();
        if (!data.success) {
            alert(data.message || 'Failed to load record data.');
            return;
        }

        if (!confirm('Change this rate status?')) return;

        document.getElementById("loadingOverlay").style.display = "flex";

        // PUT request to toggle status
        const res = await fetch(`/api/change_rate_status/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' }
        });

        document.getElementById("loadingOverlay").style.display = "none";

        if (res.ok) {
            const json = await res.json();
            alert(`Status updated: ${json.status ? 'Active' : 'Inactive'}`);
            window.location.reload(true);
        } else {
            const err = await res.json().catch(() => ({}));
            alert(err.error || 'Failed to update status');
        }
    } catch (e) {
        document.getElementById("loadingOverlay").style.display = "none";
        console.error('Error in changeRateStatus:', e);
        alert('Error: ' + e.message);
    }
}

function validateReportDetails() {
    const reportType = document.getElementById('reportType').value;
    const startDate = document.getElementById(`startDate`).value;
    const endDate = document.getElementById(`endDate`).value;

    if (!reportType || !startDate || !endDate) {
        alert("Please make sure to fill in all required fields");
        return false;
    }    

    return true;
}
