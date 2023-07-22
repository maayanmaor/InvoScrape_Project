<?php

// Get the request parameters from the website
$fileName = $_GET['file_name'];
$startDate = $_GET['start_date'];
$endDate = $_GET['end_date'];
$minAmount = $_GET['min_amount'];
$maxAmount = $_GET['max_amount'];
$userEmail = $_GET['user_email'];

// Construct the URL for the Flask endpoint with the request parameters
$url = 'http://localhost:5000/getData?file_name=' . $fileName . '&start_date=' . $startDate . '&end_date=' . $endDate . '&min_amount=' . $minAmount . '&max_amount=' . $maxAmount . '&user_email=' . $userEmail;

// Forward the request to the Flask application using cURL
$ch = curl_init($url);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
$response = curl_exec($ch);
curl_close($ch);

// Return the Flask response to the website
echo $response;

?>
