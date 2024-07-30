
const checkbox = document.getElementById('enabled_context');
const radioButtons = document.querySelectorAll('input[name="model"]');
const enableRag = document.getElementById('enabled_rag');

window.onload = function () {
    const isChecked = localStorage.getItem('enabled_context');
    checkbox.checked = isChecked === 'true';

    const enableRagChecked = localStorage.getItem('enabled_rag');
    enableRag.checked = enableRagChecked === 'true';

    const selectedModel = localStorage.getItem('selected_model');
    if (selectedModel) {
        document.querySelector(`input[name="model"][value="${selectedModel}"]`).checked = true;
    }
};

checkbox.addEventListener('change', function () {
    localStorage.setItem('enabled_context', checkbox.checked);
    localStorage.setItem('enabled_rag', enableRag.checked);
});

radioButtons.forEach(radio => {
    radio.addEventListener('change', function () {
        if (radio.checked) {
            localStorage.setItem('selected_model', radio.value);
        }
    });
});



