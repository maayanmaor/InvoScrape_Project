<?php
error_reporting(E_ALL);
ini_set('display_errors', 1);

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

$target_dir = "uploads/"; // The directory where uploaded files will be saved

// Generate a unique ID for the file
$unique_id = uniqid();
$target_file = $target_dir . $unique_id . '_' . basename($_FILES["file"]["name"]);

$uploadOk = 1; // Flag to indicate whether the file was uploaded successfully

// Check if the file already exists
if (file_exists($target_file)) {
    $error_message = "Sorry, a file with that name already exists.";
    $uploadOk = 0;
}

// Check the file size (not more than 5MB)
if ($_FILES["file"]["size"] > 5000000) {
    $error_message = "Sorry, your file is too large.";
    $uploadOk = 0;
}

// Only allow certain file types
$allowed_types = array("jpg", "jpeg", "png", "pdf");
$file_type = strtolower(pathinfo($target_file, PATHINFO_EXTENSION));
if (!in_array($file_type, $allowed_types)) {
    $error_message = "Sorry, only JPG, JPEG, PNG, and PDF files are allowed.";
    $uploadOk = 0;
}

// Check if the uploaded file is empty
if ($_FILES["file"]["size"] == 0) {
    $error_message = "Sorry, the uploaded file is empty, please check the chosen file.";
    $uploadOk = 0;
}

// If $uploadOk is still 1, try to upload the file and send data to Flask script
if ($uploadOk == 1) {
    if (move_uploaded_file($_FILES["file"]["tmp_name"], $target_file)) {
        // Send email and file name to Flask script, along with the unique ID
        $url = 'http://localhost:5000/add';
        $data = array(
            'email' => $_POST['email'],
            'file_name' => $_FILES["file"]["name"],
            'unique_id' => $unique_id,
            'send_email' => isset($_POST['sendEmail']) ? 'true' : 'false' // Check if the checkbox is checked
        );
        echo "Sending data to Flask script: ", json_encode($data), "<br>";
        $response = sendPostRequest($url, $data);

        // Output the response from Flask backend
        echo $response;
    } else {
        $error_message = "Sorry, there was an error uploading your file.";
        echo "Error message: ", $error_message, "<br>";
    }
} else {
    $error_message = "Sorry, there was an error uploading your file.";
    echo "Error message: ", $error_message, "<br>";
}

// Display the error message if it exists
if (isset($error_message)) {
    echo "<p>Error: ", $error_message, "</p>";
}
?>
