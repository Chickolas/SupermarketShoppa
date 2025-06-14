document.getElementById("Login").addEventListener("submit", function(event) {
    event.preventDefault();
    let formData = new FormData(event.target);
    for (let [key, value] of formData.entries()) {
        console.log(key + ": " + value);
    }
});