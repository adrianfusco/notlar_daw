function updateProfile(event) {
    event.preventDefault();

    const form = document.getElementById('updateProfileForm');
    const actionUrl = form.getAttribute('data-action-url');
    const errorContainer = $('#error-container');
    const formData = new FormData(form);

    $.ajax({
        url: actionUrl,
        type: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        success: function (data) {
            const successContainer = $('#success-container');
            const errorContainer = $('#error-container');

            if (data.error) {
                displayError(data.error);
            } else {
                clearError(errorContainer);

                const successElement = $('<div>').addClass('p-4 mb-4 text-sm text-green-800 rounded-lg bg-green-50 dark:bg-green-800 dark:text-green-400').attr('role', 'alert').html(`
                    <span class="font-medium">✓ - </span> Profile updated successfully
                `);

                successContainer.empty().append(successElement);

                setTimeout(() => {
                    successContainer.empty();
                }, 5000);

                console.log("Profile updated successfully:", data);
            }
        },
        error: function (error) {
            displayError(error.responseJSON.error);
        }
    });
}

function displayError(errorMessage) {
    const errorContainer = $('#error-container');
    errorContainer.empty();

    const errorElement = $('<div>').addClass('p-4 mb-4 text-sm text-red-800 rounded-lg bg-red-50 dark:bg-gray-800 dark:text-red-400').attr('role', 'alert').html(`
    <span class="font-medium">X - </span> ${errorMessage}
  `);

    errorContainer.append(errorElement);

    setTimeout(() => {
        errorContainer.empty();
      }, 5000);
}

function clearError(container) {
    if (container) {
        container.empty();
    }
}
