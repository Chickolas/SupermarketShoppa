function toggleMenu() {
  var menu = document.querySelector('.menu');
  menu.classList.toggle('active');
}

function closeMenu() {
  var menu = document.querySelector('.menu');
  menu.classList.remove('active');
}

// function sendToServer(url, data) {
//   fetch(url, {
//     method: "POST",
//     headers: {
//       'Content-Type': 'application/json'
//     },
//     body: JSON.stringify(data)
//   })
// }