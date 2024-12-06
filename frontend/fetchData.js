async function fetchData(inputID, statsID) {
  const username = document.getElementById(inputID).value.trim();
  if (!username) {
    alert("You must enter a username");
    return;
  }
  const URL = "https://lichess.org/api/user/" + username + "/perf/blitz";
  try {
    const response = await fetch(URL);
    if (response.status != 200) {
      throw new Error("Failed to fetch user data:", response.status);
    }

    const data = await response.json();
    const rating = data?.perf?.glicko?.rating || "N/A";

    const deviation = data?.perf?.glicko?.deviation || "N/A";

    const totalGames = data?.stat?.count?.all || "N/A";

    const bestWins = data?.stat?.bestWins?.results || [];
    let bw1 = null;
    let bw2 = null;
    let bw3 = null;
    if (bestWins.length >= 3) {
      bw1 = bestWins[0]?.opRating || 0;
      bw2 = bestWins[1]?.opRating || 0;
      bw3 = bestWins[2]?.opRating || 0;
    } else {
      bw1 = 0;
      bw2 = 0;
      bw3 = 0;
    }

    const tableBody = document.getElementById(`${statsID}-table-body`);
    tableBody.innerHTML = ""; // Clear previous data

    // Add rows to the table
    addTableRow(tableBody, "Blitz Rating", rating);
    addTableRow(tableBody, "Rating Deviation", deviation);
    addTableRow(tableBody, "Total Games Played", totalGames);
    addTableRow(tableBody, "Highest Rated Win", bw1);
    addTableRow(tableBody, "Second Highest Rated Win", bw2);
    addTableRow(tableBody, "Third Highest Rated Win", bw3);

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
