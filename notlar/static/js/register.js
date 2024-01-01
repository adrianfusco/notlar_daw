$(document).ready(function () {
    $('#registration-form').submit(function (event) {
        event.preventDefault();

        const formData = $(this).serializeArray();
        const data = {};
        $.map(formData, function (field) {
            data[field.name] = field.value;
        });

        $.ajax({
            type: 'POST',
            url: '/register',
            contentType: 'application/json',
            data: JSON.stringify(data),
            success: function (result) {
                displaySuccess(result.message);

                setTimeout(function () {
                    $('[data-modal-hide="registration-modal"]').click();
                    $('[data-modal-target="authentication-modal"]').click();
                }, 2000);

            },
            error: function (error) {
                if (error.status === 400) {
                    const errorMessage = error.responseJSON.message;
                    displayError(errorMessage);
                }
                else {
                    displayError('An error occurred while processing your request.');
                }
            },
        });
    });

    function displayError(errorMessage) {
        const errorContainer = $('#error-container');
        errorContainer.empty();

        const errorElement = $('<div>').addClass('p-4 mb-4 text-sm text-red-800 rounded-lg bg-red-50 dark:bg-gray-800 dark:text-red-400').attr('role', 'alert').html(`
        <span class="font-medium">Hey!</span> ${errorMessage}
      `);

        errorContainer.append(errorElement);
    }

    function displaySuccess(successMessage) {
        const successContainer = $('#success-container');
        successContainer.empty();

        const successElement = $('<div>').addClass('p-4 mb-4 text-sm text-green-800 rounded-lg bg-green-50 dark:bg-gray-800 dark:text-green-400').attr('role', 'alert').html(`
        <span class="font-medium">Welcome!</span> ${successMessage}
      `);

        successContainer.append(successElement);
    }

});