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

// Format today as YYYY-MM-DD (local)
function todayLocalISO() {
    const d = new Date();
    const y = d.getFullYear();
    const m = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    return `${y}-${m}-${day}`; // e.g., 2025-08-26
}

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
                Swal.fire({
                    icon: 'warning',
                    title: 'No File Selected',
                    text: 'Please select a file before proceeding.',
                    confirmButtonColor: '#f39c12'
                });
                return;
            }

            // Show loading overlay
            document.getElementById("loadingOverlay").style.display = "flex";

            const formData = new FormData(this);
            console.log("[ADMIN] Fetch initiated:", '/upload_subjects');

            fetch('/upload_subjects', {
                method: 'POST',
                body: formData
            })
            .then(response =>  response.json())
            .then(data => {
                console.log("[ADMIN] Fetch success response received");
                document.getElementById("loadingOverlay").style.display = "none";

                if (data.success) {
                    Swal.fire({
                        icon: 'success',
                        title: 'Upload Successful',
                        text: data.message,
                        confirmButtonColor: '#3085d6',
                        timer: 2000,
                        showConfirmButton: false
                    }).then(() => {
                        if (data.warnings && data.warnings.length > 0) {
                            data.warnings.forEach(warning => {
                                console.warn("[ADMIN] Warning:", warning);
                                Swal.fire({
                                    icon: 'warning',
                                    title: 'Warning',
                                    text: warning,
                                    confirmButtonColor: '#f39c12'
                                });
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

                        // Refresh page after all alerts are done
                        location.reload();
                    });
                }
                else {
                    // Show errors
                    console.error("[ADMIN] Upload failed:", data.message);

                    let errorHtml = '';
                    if (data.errors && data.errors.length > 0) {
                        errorHtml = `
                            <div style="max-height:200px; overflow-y:auto; text-align:left;">
                                <ul>${data.errors.map(err => `<li>${err}</li>`).join('')}</ul>
                            </div>`;
                    }

                    Swal.fire({
                        icon: 'error',
                        title: 'Upload Failed',
                        html: `
                            <p>${data.message || 'Upload failed.'}</p>
                            ${errorHtml}
                        `,
                        confirmButtonColor: '#d33',
                        width: '50rem',
                        scrollbarPadding: false
                    });
                }
            })
            .catch(error => {
                document.getElementById("loadingOverlay").style.display = "none";
                console.error("[ADMIN] Error occurred:", error);
                Swal.fire({
                    icon: 'error',
                    title: 'Unexpected Error',
                    text: 'Upload failed: ' + error.message,
                    confirmButtonColor: '#d33'
                });
            });

            // Prevent attaching listener multiple times
            uploadCourseStructure.dataset.listenerAttached = "true";
        });
    }
}


// Change Rate Status (Active <-> Inactive)
async function changeRateStatus(table, id) {
    try {
        // Verify record exists before attempting update
        console.log("[ADMIN] Fetch initiated:", `/get_record/${table}/${id}`);
        const check = await fetch(`/get_record/${table}/${id}`);
        const data = await check.json();

        if (!data.success) {
            console.error("[ADMIN] Failed to fetch record:", data.message);
            Swal.fire({
                icon: 'error',
                title: 'Record Not Found',
                text: data.message || 'Failed to load record data.',
                confirmButtonColor: '#d33'
            });
            return;
        }
        const result = await Swal.fire({
            icon: 'question',
            title: 'Change Rate Status?',
            text: 'Are you sure you want to change this rate status?',
            showCancelButton: true,
            confirmButtonText: 'Yes, change it',
            cancelButtonText: 'Cancel',
            confirmButtonColor: '#3085d6',
            cancelButtonColor: '#aaa'
        });

        if (!result.isConfirmed) {
            console.log("[ADMIN] Rate status change cancelled by user.");
            return;
        }

        document.getElementById("loadingOverlay").style.display = "flex";

        // PUT request to toggle status
        console.log("[ADMIN] Fetch initiated:", `/api/change_rate_status/${id}`);
        const res = await fetch(`/api/change_rate_status/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' }
        });

        document.getElementById("loadingOverlay").style.display = "none";

        if (res.ok) {
            const json = await res.json();
            console.log("[ADMIN] Rate status successfully updated:", json);

            Swal.fire({
                icon: 'success',
                title: 'Status Updated',
                text: `Rate status changed to ${json.status ? 'Active' : 'Inactive'}.`,
                timer: 1500,
                showConfirmButton: false
            }).then(() => {
                location.reload();
            });
        } else {
            const err = await res.json().catch(() => ({}));
            console.error("[ADMIN] Failed to update rate status:", err.error || 'Unknown error');
            Swal.fire({
                icon: 'error',
                title: 'Update Failed',
                text: err.error || 'Failed to update rate status.',
                confirmButtonColor: '#d33'
            });
        }
    } catch (e) {
        document.getElementById("loadingOverlay").style.display = "none";
        console.error("[ADMIN] Error in changeRateStatus:", e);
        Swal.fire({
            icon: 'error',
            title: 'Unexpected Error',
            text: 'Error: ' + e.message,
            confirmButtonColor: '#d33'
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
                Swal.fire({
                    icon: 'warning',
                    title: 'No File Selected',
                    text: 'Please select a file before proceeding.',
                    confirmButtonColor: '#f39c12'
                });
                return;
            }

            document.getElementById("loadingOverlay").style.display = "flex";

            const formData = new FormData(this);
            console.log("[ADMIN] Fetch initiated:", '/upload_lecturers');

            fetch('/upload_lecturers', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                console.log("[ADMIN] Fetch success response received");
                document.getElementById("loadingOverlay").style.display = "none";

                if (data.success) {
                    Swal.fire({
                        icon: 'success',
                        title: 'Upload Successful',
                        text: data.message,
                        confirmButtonColor: '#3085d6',
                        timer: 2000,
                        showConfirmButton: false
                    }).then(() => {
                        if (data.warnings && data.warnings.length > 0) {
                            data.warnings.forEach(warning => {
                                console.warn("[ADMIN] Warning:", warning);
                                Swal.fire({
                                    icon: 'warning',
                                    title: 'Warning',
                                    text: warning,
                                    confirmButtonColor: '#f39c12'
                                });
                            });
                        }

                        // Update timestamp if at least 1 record processed
                        if (data.message.includes('Successfully processed')) {
                            const currentDate = new Date();
                            const formattedDate = currentDate.toLocaleString('en-GB', {
                                weekday: 'short', year: '2-digit', month: 'short', day: '2-digit',
                                hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: true
                            });
                            localStorage.setItem('lecturerLastUploaded', formattedDate);
                        }

                        // Refresh page after all alerts are done
                        location.reload();
                    });
                } else {
                    console.error("[ADMIN] Upload failed:", data.message);
                    
                    let errorHtml = '';
                    if (data.errors && data.errors.length > 0) {
                        errorHtml = `
                            <div style="max-height:200px; overflow-y:auto; text-align:left;">
                                <ul>${data.errors.map(err => `<li>${err}</li>`).join('')}</ul>
                            </div>`;
                    }

                    Swal.fire({
                        icon: 'error',
                        title: 'Upload Failed',
                        html: `
                            <p>${data.message || 'Upload failed.'}</p>
                            ${errorHtml}
                        `,
                        confirmButtonColor: '#d33',
                        width: '50rem',
                        scrollbarPadding: false
                    });
                }
            })
            .catch(error => {
                document.getElementById("loadingOverlay").style.display = "none";
                console.error("[ADMIN] Error occurred:", error);
                Swal.fire({
                    icon: 'error',
                    title: 'Unexpected Error',
                    text: 'Upload failed: ' + error.message,
                    confirmButtonColor: '#d33'
                });
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
                Swal.fire({
                    icon: 'warning',
                    title: 'No File Selected',
                    text: 'Please select a file before proceeding.',
                    confirmButtonColor: '#f39c12'
                });
                return;
            }

            document.getElementById("loadingOverlay").style.display = "flex";

            const formData = new FormData(this);
            console.log("[ADMIN] Fetch initiated:", '/upload_heads');

            fetch('/upload_heads', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                console.log("[ADMIN] Fetch success response received");
                document.getElementById("loadingOverlay").style.display = "none";

                if (data.success) {
                    Swal.fire({
                        icon: 'success',
                        title: 'Upload Successful',
                        text: data.message,
                        confirmButtonColor: '#3085d6',
                        timer: 2000,
                        showConfirmButton: false
                    }).then(() => {
                        if (data.warnings && data.warnings.length > 0) {
                            data.warnings.forEach(warning => {
                                console.warn("[ADMIN] Warning:", warning);
                                Swal.fire({
                                    icon: 'warning',
                                    title: 'Warning',
                                    text: warning,
                                    confirmButtonColor: '#f39c12'
                                });
                            });
                        }

                        // Update timestamp if at least 1 record processed
                        if (data.message.includes('Successfully processed')) {
                            const currentDate = new Date();
                            const formattedDate = currentDate.toLocaleString('en-GB', {
                                weekday: 'short', year: '2-digit', month: 'short', day: '2-digit',
                                hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: true
                            });
                            localStorage.setItem('headLastUploaded', formattedDate);
                        }

                        // Refresh page after all alerts are done
                        location.reload();
                    });
                } else {
                    console.error("[ADMIN] Upload failed:", data.message);

                    let errorHtml = '';
                    if (data.errors && data.errors.length > 0) {
                        errorHtml = `
                            <div style="max-height:200px; overflow-y:auto; text-align:left;">
                                <ul>${data.errors.map(err => `<li>${err}</li>`).join('')}</ul>
                            </div>`;
                    }

                    Swal.fire({
                        icon: 'error',
                        title: 'Upload Failed',
                        html: `
                            <p>${data.message || 'Upload failed.'}</p>
                            ${errorHtml}
                        `,
                        confirmButtonColor: '#d33',
                        width: '50rem',
                        scrollbarPadding: false
                    });
                }
            })
            .catch(error => {
                document.getElementById("loadingOverlay").style.display = "none";
                console.error("[ADMIN] Error occurred during upload:", error);
                Swal.fire({
                    icon: 'error',
                    title: 'Unexpected Error',
                    text: 'Upload failed: ' + error.message,
                    confirmButtonColor: '#d33'
                });
            });

        });
        uploadHeadList.dataset.listenerAttached = "true";
    }
}

async function checkApprovalPeriodAndToggleButton(approvalId) {
    try {
        console.log("[Admin] Fetch initiated:", `/check_requisition_period/${approvalId}`);
        const response = await fetch(`/check_requisition_period/${approvalId}`);
        if (!response.ok) {
            throw new Error(`Network response was not ok (status ${response.status})`);
        }

        const data = await response.json();
        console.log("[Admin] Fetch success response received:", data);

        const voidBtn = document.getElementById(`void-btn-${approvalId}`);

        if (voidBtn) {
            if (data.expired) {
                voidBtn.disabled = true;
                voidBtn.style.cursor = 'not-allowed';
                voidBtn.style.backgroundColor = 'grey';
            }
        }

    } catch (error) {
        console.error("[Admin] Error checking approval period:", error);
        Swal.fire({
            icon: 'error',
            title: 'Error Occurred',
            text: 'An error occurred while checking the approval period. Please try again later.',
            confirmButtonColor: '#d33'
        });
    }
}

// Submit void reason
function submitVoidRequisitionReason() {
    const reason = document.getElementById("void-reason").value.trim();

    if (!reason) {
        Swal.fire({
            icon: 'warning',
            title: 'Missing Reason',
            text: 'Please provide a reason for voiding this requisition.',
            confirmButtonColor: '#f39c12'
        });
        return;
    }

    // Show loading overlay
    document.getElementById("loadingOverlay").style.display = "flex";
    console.log("[Admin] Fetch initiated:", `/api/admin_void_requisition/${selectedVoidId}`);

    fetch(`/api/admin_void_requisition/${selectedVoidId}`, {
        method: "POST",
        body: JSON.stringify({ reason }),
        headers: { "Content-Type": "application/json" }
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("loadingOverlay").style.display = "none";

        if (!data.success) {
            console.warn("[Admin] Void requisition failed:", data.error || "Unknown error");
            Swal.fire({
                icon: 'error',
                title: 'Failed to Void Requisition',
                text: data.error || 'Unknown error occurred. Please try again.',
                confirmButtonColor: '#d33'
            });
            return;
        }

        console.log("[Admin] Requisition voided successfully:", data);
        Swal.fire({
            icon: 'success',
            title: 'Requisition Voided',
            text: 'The requisition has been successfully voided.',
            timer: 1500,
            showConfirmButton: false
        }).then(() => {
            closeVoidModal();
            location.reload();
        });
    })
    .catch(error => {
        document.getElementById("loadingOverlay").style.display = "none";
        console.error("[Admin] Error occurred during void requisition submission:", error);
        Swal.fire({
            icon: 'error',
            title: 'Error Occurred',
            text: 'An error occurred while voiding the requisition: ' + error.message,
            confirmButtonColor: '#d33'
        });
    });
}

function validateReportDetails() {
    const reportType = document.getElementById('reportType').value;
    const startDate = document.getElementById('startDate').value;
    const endDate = document.getElementById('endDate').value;

    if (!reportType || !startDate || !endDate) {
        Swal.fire({
            icon: 'warning',
            title: 'Incomplete Fields',
            text: 'Please make sure to select all required fields.',
            confirmButtonColor: '#f39c12'
        });
        return false;
    }

    // Check date order
    if (new Date(endDate) < new Date(startDate)) {
        Swal.fire({
            icon: 'error',
            title: 'Invalid Date Range',
            text: 'End date cannot be before the start date.',
            confirmButtonColor: '#d33'
        });
        return false;
    }

    return true;
}
