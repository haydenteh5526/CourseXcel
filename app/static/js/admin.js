// Move editableFields to the global scope (outside any function)
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
    'lecturers': ['name', 'email', , 'ic_no', 'level', 'department_id', 'upload_file'],
    'heads': ['name', 'email', 'level', 'department_id'],
    'programOfficers': ['name', 'email', 'department_id'],
    'others': ['name', 'email', 'role']
};

// Add these constants at the top of your file
const RECORDS_PER_PAGE = 20;
let currentPages = {
    'subjects': 1,
    'rates': 1,
    'departments': 1,
    'lecturers': 1,
    'lecturerFiles': 1,
    'lecturerAttachments': 1,
    'claimDetails': 1,
    'heads': 1,
    'programOfficers': 1,
    'others': 1,
    'requisitionApprovals': 1,
    'claimApprovals': 1
};

function initTableFilters(deptSelectorId, statusSelectorId) {
    const departmentFilter = document.getElementById(deptSelectorId);
    const statusFilter = document.getElementById(statusSelectorId);

    const tableId = departmentFilter.dataset.tableId;
    const rows = document.querySelectorAll(`#${tableId} tbody tr`);

    // Mark all as searchable by default
    rows.forEach(row => {
        row.dataset.searchMatch = 'true';
    });

    function applyFilters() {
        const selectedDept = departmentFilter.value.toLowerCase();
        const selectedStatus = statusFilter.value.toLowerCase();

        rows.forEach(row => {
            const dept = row.getAttribute("data-department")?.toLowerCase() || '';
            const status = row.getAttribute("data-status")?.toLowerCase() || '';

            const matchDept = !selectedDept || dept === selectedDept;
            const matchStatus = !selectedStatus || status.includes(selectedStatus);

            row.style.display = (matchDept && matchStatus) ? "" : "none";
        });
    }

    departmentFilter.addEventListener("change", applyFilters);
    statusFilter.addEventListener("change", applyFilters);
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


function setupCourseStructureForm() {
    const uploadCourseStructure = document.getElementById('uploadCourseStructure');
    if (uploadCourseStructure && !uploadCourseStructure.dataset.listenerAttached) {
        uploadCourseStructure.addEventListener('submit', function (e) {
            e.preventDefault();

            const file = document.getElementById('courseStructure').files[0];
            if (!file) {
                alert('Please select a file');
                return;
            }

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
                    if (data.warnings) {
                        data.warnings.forEach(warning => {
                            alert('Warning: ' + warning);
                        });
                    }

                    // Only update timestamp if records were processed (not 0)
                    if (!data.message.includes('processed 0 subject(s)')) {
                        const currentDate = new Date();
                        const formattedDate = currentDate.toLocaleString('en-GB', {
                            weekday: 'short', year: '2-digit', month: 'short', day: '2-digit',
                            hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: true
                        });
                        localStorage.setItem('csLastUploaded', formattedDate);
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

            uploadCourseStructure.dataset.listenerAttached = "true";
        });
    }
}

function setupLecturerForm() {
    const uploadLecturerList = document.getElementById('uploadLecturerList');    
    if (uploadLecturerList && !uploadLecturerList.dataset.listenerAttached) {
        uploadLecturerList.addEventListener('submit', function(e) {
            e.preventDefault();

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
                    if (data.warnings) {
                        data.warnings.forEach(warning => alert('Warning: ' + warning));
                    }

                    // Only update timestamp if > 0 lecturers processed
                    if (!data.message.includes('processed 0 lecturer(s)')) {
                        const currentDate = new Date();
                        const formattedDate = currentDate.toLocaleString('en-GB', {
                            weekday: 'short', year: '2-digit', month: 'short', day: '2-digit',
                            hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: true
                        });
                        localStorage.setItem('lecturerLastUploaded', formattedDate);
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
        uploadLecturerList.dataset.listenerAttached = "true";
    }
}

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

                    // Only update timestamp if > 0 heads processed
                    if (!data.message.includes('processed 0 head(s)')) {
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

async function changeRateStatus(table, id) {
    try {
        // (Optional) verify the record exists
        const check = await fetch(`/get_record/${table}/${id}`);
        const data = await check.json();
        if (!data.success) {
            alert(data.message || 'Failed to load record data');
            return;
        }

        if (!confirm('Change this rate status?')) return;

        document.getElementById("loadingOverlay").style.display = "flex";

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
