$(document).ready(function () {
    var errorMessage = $('#errorMessage');

    $('#login-form').submit(function (event) {
        event.preventDefault();

        var formData = {
            email: $('#email').val(),
            password: $('#password').val()
        };

        $.ajax({
            type: 'POST',
            url: '/login',
            contentType: 'application/json',
            data: JSON.stringify(formData),
            success: function (response) {
                if (response.logged) {
                    window.location.href = '/dashboard_notes_management';
                }
            },
            error: function (error) {
                displayError(error.responseJSON.error);
            }
        });
    });
});


function displayError(errorMessage) {
    const errorContainer = $('#error-container');
    errorContainer.empty();

    const errorElement = $('<div>').addClass('p-4 mb-4 text-sm text-red-800 rounded-lg bg-red-50 dark:bg-gray-800 dark:text-red-400').attr('role', 'alert').html(`
    <span class="font-medium">Hey!</span> ${errorMessage}
  `);

    errorContainer.append(errorElement);

    setTimeout(() => {
        errorContainer.empty();
      }, 3000);
}