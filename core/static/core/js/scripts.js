/**
 * Makes a GET request to the server to get a list of teachers matching the given query and page number.
 * @param {string} query - The search query string. Optional.
 * @param {number} page - The page number to display. Optional.
 */
function getTeachers(query, page) {
  // Create a new XMLHttpRequest object
  const xhr = new XMLHttpRequest();

  // Set the URL for the GET request
  let url = `list/?page=${page}`
  if (query) {
      url += `&query=${query}`;
  }

  // Open the XMLHttpRequest with the URL
  xhr.open('GET', url);

  // Define the function to execute when the XMLHttpRequest loads
  xhr.onload = function() {
      // If the XMLHttpRequest status is 200 (OK), display the response
      if (xhr.status === 200) {
          const teachersList = document.getElementById('teachers-container');
          console.log(xhr.responseText)
          teachersList.innerHTML = xhr.responseText;
      } else {
          console.log('Search error!');
      }
  }

  // Send the XMLHttpRequest
  xhr.send();
}
