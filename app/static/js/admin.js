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
    'departments': 1,
    'lecturers': 1,
    'lecturersFile': 1,
    'heads': 1,
    'programOfficers': 1,
    'others': 1,
    'requisitionApprovals': 1,
    'claimApprovals': 1
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
    ['subjects', 'departments', 'lecturers', 'lecturersFile', 'heads', 'programOfficers', 'others', 'requisitionApprovals', 'claimApprovals'].forEach(tableType => {
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
