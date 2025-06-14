function editRow(index) {
    
    var row = document.getElementById('row_' + index);
    var cells = row.getElementsByTagName('td');

    // Skip the first cell (Category Name)
    for (var i = 1; i < cells.length - 1; i++) {
        var input = document.createElement('input');
        input.value = cells[i].innerText;
        input.className = 'Category';
        cells[i].innerText = '';
        cells[i].appendChild(input);
    }

    var button = row.getElementsByTagName('button')[0];
    button.innerText = 'Save';
    button.onclick = function() { saveRow(index); };

    // Toggle form visibility
    toggleForm(index);
}

function saveRow(index) {
    var row = document.getElementById('row_' + index);
    var cells = row.getElementsByTagName('td');
    var updatedValues = {};

    // Skip the first cell (Category Name)
    for (var i = 1; i < cells.length - 1; i++) {
        var input = cells[i].getElementsByTagName('input')[0];
        updatedValues['column' + (i - 1)] = input.value; // Adjust column index by subtracting 1
    }

    var queryParams = Object.keys(updatedValues).map(key => key + '=' + encodeURIComponent(updatedValues[key])).join('&');
    var url = '/Categorylist?index=' + index + '&' + queryParams;

    fetch(url)
        .then(response => {
            if (response.ok) {
                return response.text();
            }
            throw new Error('Network response was not ok.');
        })
        .then(data => {
            console.log(data); // Handle the response from Flask if needed
        })
        .catch(error => {
            console.error('There was a problem with the fetch operation:', error);
        });

    // Update table cells with new values
    for (var i = 1; i < cells.length - 1; i++) { // Skip the first cell (Category Name)
        var input = cells[i].getElementsByTagName('input')[0];
        cells[i].innerText = input.value;
    }

    var button = row.getElementsByTagName('button')[0];
    button.innerText = 'Edit';
    button.onclick = function() { editRow(index); };

    // Toggle form visibility
    toggleForm(index);
}

document.addEventListener("DOMContentLoaded", function(event) { 
    window.scrollTo(0, 0);
    
    var scrollpos = localStorage.getItem('scrollpos');
    if (scrollpos) window.scrollTo(0, scrollpos);
    });
