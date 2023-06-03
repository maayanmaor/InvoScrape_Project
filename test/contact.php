<?php
error_reporting(E_ALL);
ini_set('display_errors', 1);
$response = array('success' => false);

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $name = $_POST['name'];
    $email = $_POST['email'];
    $subject = $_POST['subject'];
    $message = $_POST['message'];

    // Set up the request data
    $data = array(
        'name' => $name,
        'email' => $email,
        'subject' => $subject,
        'message' => $message
    );

    // Send the request to the Flask server
    $url = 'http://localhost:5000/contact'; 
    $ch = curl_init($url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_POST, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, $data);

    // Execute the request
    $result = curl_exec($ch);

    // Check if the request was successful
    if ($result !== false) {
        $response = json_decode($result, true);
    } else {
        $response['error_message'] = 'Failed to send the email. Please try again.';
    }

    // Close the cURL handle
    curl_close($ch);
}

echo json_encode($response);
?>
