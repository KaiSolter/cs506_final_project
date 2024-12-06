async function fetchData(inputID, statsID) {
  const username = document.getElementById(inputID).value.trim();
  if (!username) {
    alert("You must enter a username");
    return;
  }
  console.log("Username entered:", username);
  const URL = "https://lichess.org/api/user/" + username;
  try {
    const response = await fetch(URL);
    if (response.status != 200) {
      throw new Error("Failed to fetch user data:", response.status);
    }

    const data = await response.json();
    const blitz = data?.perfs?.blitz || {};
    const rating = blitz?.rating || null;
    const tableBody = document.getElementById(`${statsID}-table-body`);
    tableBody.innerHTML = ""; // Clear previous data

    // Add rows to the table
    addTableRow(tableBody, "Blitz Rating", rating);

    alert(`User's blitz rating: ${rating}`);
  } catch (e) {
    console.error(e);
  }
}

function addTableRow(tableBody, category, rating) {
  const row = document.createElement("tr");

  const categoryCell = document.createElement("td");
  categoryCell.textContent = category;

  const ratingCell = document.createElement("td");
  ratingCell.textContent = rating;

  row.appendChild(categoryCell);
  row.appendChild(ratingCell);

  tableBody.appendChild(row);
}
