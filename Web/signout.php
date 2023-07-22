<?php

// Check if the form was submitted
if (isset($_POST["logout"])) {
   // Send request to Flask backend
   $url = 'http://localhost:5000/logout';
   $ch = curl_init($url);
   curl_setopt($ch, CURLOPT_POST, 1);
   curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
   $response = curl_exec($ch);
   curl_close($ch);
   echo "Response from Flask: " . $response;
}

?>
