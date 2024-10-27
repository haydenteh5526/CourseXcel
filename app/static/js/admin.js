function openTab(tabName) {
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
    currentTarget.className += " active";
}

// Add CRUD functions here
function createRecord(table) {
    // Implement create functionality
}

function editRecord(table, id) {
    // Implement edit functionality
}

function deleteRecord(table, id) {
    // Implement delete functionality
}
