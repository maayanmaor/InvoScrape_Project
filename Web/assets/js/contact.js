document.addEventListener('DOMContentLoaded', function() {
  // Get the form element
  var form = document.getElementById('contact-form');

  // Add an event listener to the form submission
  form.addEventListener('submit', function(event) {
    event.preventDefault();

    // Get the values from the form inputs
    var name = document.getElementById('name').value;
    var email = document.getElementById('email').value;
    var subject = document.getElementById('subject').value;
    var message = document.getElementById('message').value;

    // Create a new XMLHttpRequest object
    var xhr = new XMLHttpRequest();

    // Set up the request
    xhr.open('POST', 'contact.php', true);
    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');

    // Get the loading message element
    var loadingMessage = document.getElementById('loading-message');
	var successMessage = document.getElementById('success-message');
	var errorMessage = document.getElementById('error-message');

    // Show the loading message
    loadingMessage.style.display = 'block';

    // Set up a callback function to handle the response
    xhr.onload = function() {
      // Hide the loading message
      loadingMessage.style.display = 'none';

      if (xhr.status === 200) {
        console.log(xhr.responseText); // Log the response received from the server
        var response = JSON.parse(xhr.responseText);
        console.log(response); // Log the parsed response object

        if (response.success) {
          // Display success message
          document.getElementById('success-message').textContent = response.success_message;
          document.getElementById('error-message').textContent = '';
		  successMessage.style.display = 'block';

          // Clear form inputs
          form.reset();
        } else {
          // Display error message
          document.getElementById('error-message').textContent = response.error_message;
          document.getElementById('success-message').textContent = '';
		  errorMessage.style.display = 'block';
        }
      } else {
        // Display error message
        document.getElementById('error-message').textContent = 'An error occurred. Please try again later.';
        document.getElementById('success-message').textContent = '';
		errorMessage.style.display = 'block';
      }
    };

    // Send the request with the form data
    var formData = 'name=' + encodeURIComponent(name) +
      '&email=' + encodeURIComponent(email) +
      '&subject=' + encodeURIComponent(subject) +
      '&message=' + encodeURIComponent(message);
    console.log('Form Data:', formData); // Log the form data being sent
    xhr.send(formData);
  });
});
