
const checkbox = document.getElementById('enabled_context');
const radioButtons = document.querySelectorAll('input[name="model"]');

window.onload = function () {
    const isChecked = localStorage.getItem('enabled_context');
    checkbox.checked = isChecked === 'true';

    const selectedModel = localStorage.getItem('selected_model');
    if (selectedModel) {
        document.querySelector(`input[name="model"][value="${selectedModel}"]`).checked = true;
    }
};

checkbox.addEventListener('change', function () {
    localStorage.setItem('enabled_context', checkbox.checked);
});

radioButtons.forEach(radio => {
    radio.addEventListener('change', function () {
        if (radio.checked) {
            localStorage.setItem('selected_model', radio.value);
        }
    });
});



