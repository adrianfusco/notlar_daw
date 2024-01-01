document.addEventListener('DOMContentLoaded', function() {
    const profileForm = document.querySelector('#profile-form');
    const feedbackMessage = document.querySelector('#feedback-message');
    
    profileForm.addEventListener('submit', function(event) {
        event.preventDefault();

        // Create a FormData object from the form
        const formData = new FormData(profileForm);

        // Send a POST request to the server
        fetch('/update_profile', {
            method: 'POST',
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            if (data.name) {
                // Display success message in green
                feedbackMessage.textContent = 'Profile updated successfully';
                feedbackMessage.style.color = 'green';

                // Reload the page after a successful update
                setTimeout(function() {
                    window.location.reload(true);
                }, 1000); // Reload after 1 second (adjust delay as needed)
            } else {
                // Display error message from the server response in red
                feedbackMessage.textContent = data.message || 'Failed to update profile';
                feedbackMessage.style.color = 'red';
            }
        })
        .catch(error => {
            console.error(error);
            feedbackMessage.textContent = 'An error occurred while updating the profile';
            feedbackMessage.style.color = 'red';
        });
    });
});
