async function checkApprovalStatusAndToggleButton(approvalId) {
    try {
        const response = await fetch(`/check_claim_status/${approvalId}`);
        if (!response.ok) throw new Error('Network response was not ok');

        const data = await response.json(); 
        const approveBtn = document.getElementById(`approve-btn-${approvalId}`);
        const voidBtn = document.getElementById(`void-btn-${approvalId}`);

        if (approveBtn) {
            // Disable approve button if status does not contain "Lecturer"
            if (!data.status.includes("Pending Acknowledgement by Lecturer")) {
                approveBtn.disabled = true;
                approveBtn.style.cursor = 'not-allowed';
                approveBtn.textContent = 'Approved';
                approveBtn.style.backgroundColor = 'grey';
            }
        }

        if (voidBtn) {
            // Disable void button if status contains "Rejected"
            if (data.status.includes("Rejected") || data.status.includes("Voided")) {
                voidBtn.disabled = true;
                voidBtn.style.cursor = 'not-allowed';
                voidBtn.style.backgroundColor = 'grey';
            }
        }

    } catch (error) {
        console.error('Error checking approval status:', error);
    }
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

function submitSignature() {

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

function submitVoidReason() {

}