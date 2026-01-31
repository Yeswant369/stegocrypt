function switchTab(tab) {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));

    if (tab === 'encrypt') {
        document.querySelector('button[onclick="switchTab(\'encrypt\')"]').classList.add('active');
        document.getElementById('encrypt-section').classList.add('active');
    } else {
        document.querySelector('button[onclick="switchTab(\'decrypt\')"]').classList.add('active');
        document.getElementById('decrypt-section').classList.add('active');
    }
}

function updateFileName(input) {
    const parent = input.closest('.file-drop-area');
    const msg = parent.querySelector('.file-msg');
    if (input.files && input.files.length > 0) {
        msg.textContent = input.files[0].name;
        parent.style.borderColor = 'var(--accent-color)';
    } else {
        msg.textContent = 'or drag and drop here';
        parent.style.borderColor = 'var(--border-color)';
    }
}

function toggleSecretInput(type) {
    document.querySelectorAll('.toggle-btn').forEach(b => b.classList.remove('active'));
    if (type === 'text') {
        document.querySelector('button[onclick="toggleSecretInput(\'text\')"]').classList.add('active');
        document.getElementById('secret-text-input').style.display = 'block';
        document.getElementById('secret-file-input').style.display = 'none';
        // Clear file input
        document.querySelector('input[name="secret_file"]').value = '';
    } else {
        document.querySelector('button[onclick="toggleSecretInput(\'file\')"]').classList.add('active');
        document.getElementById('secret-text-input').style.display = 'none';
        document.getElementById('secret-file-input').style.display = 'block';
        // Clear text input
        document.querySelector('textarea[name="secret_text"]').value = '';
    }
}

// Drag and drop events
document.querySelectorAll('.file-drop-area').forEach(area => {
    area.addEventListener('dragover', (e) => {
        e.preventDefault();
        area.classList.add('dragover');
    });
    area.addEventListener('dragleave', () => {
        area.classList.remove('dragover');
    });
    area.addEventListener('drop', (e) => {
        e.preventDefault();
        area.classList.remove('dragover');
        const input = area.querySelector('input[type="file"]');
        if (e.dataTransfer.files.length > 0) {
            input.files = e.dataTransfer.files;
            updateFileName(input);
        }
    });
});

// Form Submissions
document.getElementById('encrypt-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const status = document.getElementById('encrypt-status');
    status.className = 'status-msg';
    status.textContent = 'Encrypting and embedding... please wait.';

    const formData = new FormData(e.target);

    try {
        const response = await fetch('/encrypt', {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'stego_image.png';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            status.textContent = 'Success! Image downloaded.';
            status.classList.add('success');
        } else {
            const errText = await response.text();
            throw new Error(errText);
        }
    } catch (err) {
        status.textContent = 'Error: ' + err.message;
        status.classList.add('error');
    }
});

document.getElementById('decrypt-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const status = document.getElementById('decrypt-status');
    status.className = 'status-msg';
    status.textContent = 'Extracting and decrypting... please wait.';

    const formData = new FormData(e.target);

    try {
        const response = await fetch('/decrypt', {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            // Get filename from header if possible, else default
            const contentDisposition = response.headers.get('Content-Disposition');
            let filename = 'extracted_secret';
            if (contentDisposition) {
                const match = contentDisposition.match(/filename="?([^"]+)"?/);
                if (match && match[1]) filename = match[1];
            }

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);

            status.textContent = 'Success! Data extracted.';
            status.classList.add('success');
        } else {
            const errText = await response.text();
            throw new Error(errText);
        }
    } catch (err) {
        status.textContent = 'Error: ' + err.message;
        status.classList.add('error');
    }
});
