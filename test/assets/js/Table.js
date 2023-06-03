 function searchFiles() {
	var fileName = document.getElementById("fileNameInput").value;
	var startDate = document.getElementById("startDateInput").value;
	var endDate = document.getElementById("endDateInput").value;
	var minAmount = document.getElementById("minAmountInput").value;
	var maxAmount = document.getElementById("maxAmountInput").value;
	var userEmail = document.getElementById("exampleInputEmail1").value;

    // Check the entered values
    if (Number(minAmount) < 0 || Number(maxAmount) < 0) {
        alert("Min Amount and Max Amount must be at least 0.");
        return;
    }

    if (Number(minAmount) > Number(maxAmount)) {
        alert("Min Amount cannot be greater than Max Amount.");
        return;
    }
  
	// Send an AJAX request to the PHP getData file
	var url = '/getData.php?file_name=' + fileName + '&start_date=' + startDate + '&end_date=' + endDate + '&min_amount=' + minAmount + '&max_amount=' + maxAmount + '&user_email=' + userEmail;
	var xhr = new XMLHttpRequest();
	xhr.open('GET', url, true);
	xhr.onreadystatechange = function () {
		if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
			console.log(xhr.responseText); // Log the response text to check its content
			try {
				console.log(xhr.responseText); // Log the parsed response to check if data is received correctly
				updateTable(xhr.responseText); // Call a function to update the table with the response data
			} catch (error) {
				console.error(error); // Log any error that occurs during parsing
			}
		}
	};
	xhr.send();
};

function updateTable(response) {
var data = JSON.parse(response); // Parse the response as JSON

var table = document.getElementById("myTable");
var tbody = table.getElementsByTagName("tbody")[0];
tbody.innerHTML = ""; // Clear previous table body

// Populate table with response data
for (var i = 0; i < data.length; i++) {
	var rowData = data[i];
	var row = document.createElement("tr");

	// Create table cells and populate with data
	var cellIndex = document.createElement("td");
	cellIndex.textContent = i + 1;
	row.appendChild(cellIndex);

	var cellId = document.createElement("td");
	var fileName = rowData.id.split("_")[1]; // Extract the file name by removing the first 18 characters
	cellId.textContent = fileName;

	// Create "View" button
	var viewButton = document.createElement("button");
	viewButton.textContent = "View";
	viewButton.addEventListener("click", createViewButtonClickHandler(rowData.id)); // Pass the full rowData.id

	// Create a container div for ID and button
	var container = document.createElement("div");
	container.appendChild(cellId);
	container.appendChild(viewButton);

	// Create the final table cell
	var cellView = document.createElement("td");
	cellView.appendChild(container);
	row.appendChild(cellView);

	var cellCurrency = document.createElement("td");
	cellCurrency.textContent = rowData.currency;
	row.appendChild(cellCurrency);

	var cellDate = document.createElement("td");
	cellDate.textContent = rowData.Date;
	row.appendChild(cellDate);

	var cellMerchantAddress = document.createElement("td");
	cellMerchantAddress.textContent = rowData.Merchant_Address;
	row.appendChild(cellMerchantAddress);

	var cellMerchantName = document.createElement("td");
	cellMerchantName.textContent = rowData.Merchant_Name;
	row.appendChild(cellMerchantName);

	var cellMerchantPhone = document.createElement("td");
	cellMerchantPhone.textContent = rowData.Merchant_Phone;
	row.appendChild(cellMerchantPhone);

	var cellReceiptNumber = document.createElement("td");
	cellReceiptNumber.textContent = rowData.Receipt_Number;
	row.appendChild(cellReceiptNumber);

	var cellSubtax = document.createElement("td");
	cellSubtax.textContent = rowData.Subtax;
	row.appendChild(cellSubtax);

	var cellTaxAmount = document.createElement("td");
	cellTaxAmount.textContent = rowData.Tax_Amount;
	row.appendChild(cellTaxAmount);

	var cellTotalAmount = document.createElement("td");
	cellTotalAmount.textContent = rowData.Total_Amount;
	row.appendChild(cellTotalAmount);

	var cellCreatedAt = document.createElement("td");
	cellCreatedAt.textContent = rowData.created_at;
	row.appendChild(cellCreatedAt);

	tbody.appendChild(row);
}
};
	
	
function createViewButtonClickHandler(fileId) {
    return function() {
        var url = '/get_invoice.php?file_id=' + fileId;
        var xhr = new XMLHttpRequest();
        xhr.open('GET', url, true);
        xhr.responseType = 'blob';
        xhr.onreadystatechange = function() {
            if (xhr.readyState === XMLHttpRequest.DONE) {
                if (xhr.status === 200) {
                    var blobResponse = xhr.response;
                    var contentType = xhr.getResponseHeader('Content-Type');
                    if (contentType.startsWith('image/')) {
                        var objectURL = URL.createObjectURL(blobResponse);
                        openModal(objectURL, contentType);
                    } else if (contentType === 'application/pdf') {
                        var fileURL = URL.createObjectURL(blobResponse);
                        window.open(fileURL);
                    } else {
                        console.log('Received response is not an image or PDF');
                        alert('No invoice to display');
                    }
                } else {
                    console.log('Error retrieving invoice');
                    alert('Error retrieving invoice');
                }
            }
        };
        xhr.send();
    };
};






function openModal(imageURL) {
  // Create a modal or lightbox element
  var modal = document.createElement("div");
  modal.className = "modal";
  modal.style.display = "block";

  // Create an image element
  var image = document.createElement("img");
  image.src = imageURL;

  // Add CSS styles to ensure consistent size
  modal.style.display = "flex";
  modal.style.justifyContent = "center";
  modal.style.alignItems = "center";
  modal.style.backgroundColor = "rgba(0, 0, 0, 0.5)";

  image.style.maxWidth = "100%";
  image.style.maxHeight = "100%";
  image.style.objectFit = "contain";

  // Append the image to the modal
  modal.appendChild(image);

  // Append the modal to the document body
  document.body.appendChild(modal);

  // Close the modal when clicked outside the image
  modal.addEventListener("click", function () {
	modal.style.display = "none";
	document.body.removeChild(modal);
  });
};

function searchTable() {
  var input, filter, table, tr, td, i, j, txtValue;
  input = document.getElementById("searchInput");
  filter = input.value.toUpperCase();
  table = document.getElementById("myTable");
  tr = table.getElementsByTagName("tr");

  for (i = 0; i < tr.length; i++) {
	tds = tr[i].getElementsByTagName("td");
	var found = false;
	for (j = 0; j < tds.length; j++) {
	  td = tds[j];
	  if (td) {
		txtValue = td.textContent || td.innerText;
		if (txtValue.toUpperCase().indexOf(filter) > -1) {
		  found = true;
		  break;
		}
	  }
	}
	if (found) {
	  tr[i].style.display = "";
	} else {
	  tr[i].style.display = "none";
	}
  }
};

function changeRowsPerPage() {
	let select = document.getElementById("rowSelect");
	let table = document.getElementById("myTable");
	let rowsPerPage = select.value;
	let tbody = table.getElementsByTagName("tbody")[0];
	let rows = tbody.getElementsByTagName("tr");

	for (let i = 0; i < rows.length; i++) {
		if (i < rowsPerPage) {
			rows[i].style.display = "";
		} else {
			rows[i].style.display = "none";
		}
	}
};