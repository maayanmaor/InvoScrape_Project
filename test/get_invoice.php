<?php
$fileId = urlencode($_GET['file_id']); // URL encode the file name
$url = 'http://localhost:5000/getInvoice?file_id=' . $fileId;

$ch = curl_init($url);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
$response = curl_exec($ch);
$httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
$contentType = curl_getinfo($ch, CURLINFO_CONTENT_TYPE);
curl_close($ch);

if ($httpCode >= 200 && $httpCode < 300) {
    header('Content-Type: ' . $contentType);
    echo $response;
} else {
    // Print the error response and logs
    echo 'Error: Request failed with status code ' . $httpCode . '<br>';
    echo 'Response from Flask: <br>';
    echo nl2br($response);
}
?>
