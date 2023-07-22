<?php
error_reporting(E_ALL);
ini_set('display_errors', 1);

// Function to send a GET request to the Flask backend
function sendGetRequest($url) {
  $ch = curl_init($url);
  curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
  $response = curl_exec($ch);
  curl_close($ch);
  return $response;
}

// Function to send a POST request to the Flask backend
function sendPostRequest($url, $data) {
  $ch = curl_init($url);
  curl_setopt($ch, CURLOPT_POST, 1);
  curl_setopt($ch, CURLOPT_POSTFIELDS, http_build_query($data));
  curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
  $response = curl_exec($ch);
  curl_close($ch);
  return $response;
}

// Handle GET request
if ($_SERVER["REQUEST_METHOD"] == "GET") {
  // Send a GET request to Flask backend and retrieve the response
  $url = 'http://localhost:5000/register';
  $response = sendGetRequest($url);

  // Output the response from Flask backend
  echo $response;
} 
// Handle POST request
elseif ($_SERVER["REQUEST_METHOD"] == "POST") {
  // Get form data
  $fullname = $_POST["fullname"];
  $companyname = $_POST["companyname"];
  $email = $_POST["email"];
  $password = $_POST["password"];

  // Validate form data
  $errors = array();
  if (empty($fullname)) {
    $errors[] = "Full name is required";
  }
  if (empty($companyname)) {
    $errors[] = "Company name is required";
  }
  if (empty($email)) {
    $errors[] = "Email is required";
  } elseif (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
    $errors[] = "Invalid email format";
  }
  if (empty($password)) {
    $errors[] = "Password is required";
  }

  // If there are no errors, send user data to Flask backend and handle the response
  if (empty($errors)) {
    $url = 'http://localhost:5000/register';
    $data = array(
      'fullname' => $fullname,
      'companyname' => $companyname,
      'email' => $email,
      'password' => $password
    );
    $response = sendPostRequest($url, $data);

    // Output the response from Flask backend
    echo $response;
  } else {
    $error_message = implode('<br>', $errors);
    // Redirect to the signup page with the error message as a query parameter
    header("Location: signup.html?error=$error_message");
    exit;
  }
}
?>
