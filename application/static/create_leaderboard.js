function create_leaderboard(div, label, data) {
    clear_leaderboard(div);
    add_leaderboard_heading(div, label);
    leaderboard_table = document.createElement("table"); leaderboard_table.classList.add("leaderboard");
    if (data.length > 0 && data[0][1] > 0) {
        row = document.createElement("tr");
        row.appendChild(document.createElement("th"));
        name_header = document.createElement("th"); name_header.classList.add("name"); name_header.innerText = "Name";
        row.appendChild(name_header);
        distance_header = document.createElement("th"); distance_header.classList.add("distance"); distance_header.innerText = "km";
        row.appendChild(distance_header);
        leaderboard_table.appendChild(row);

        for (i = 0; i < Math.min(data.length, 30); i++) {
            if (data[i][1] > 0) {
                row = document.createElement("tr");
                rank = document.createElement("td"); rank.classList.add("rank");
                link = document.createElement("a"); link.href = "/users/viewprofile/" + data[i][2];
                link.innerText = (i + 1) + ".";
                rank.appendChild(link);
                row.appendChild(rank);

                full_name = document.createElement("td"); full_name.classList.add("name");
                link = document.createElement("a"); link.href = "/users/viewprofile/" + data[i][2];
                link.innerText = data[i][0];
                full_name.appendChild(link);
                row.appendChild(full_name);

                distance = document.createElement("td"); distance.classList.add("distance");
                link = document.createElement("a"); link.href = "/users/viewprofile/" + data[i][2];
                link.innerText = data[i][1];
                distance.appendChild(link);
                row.appendChild(distance);
                leaderboard_table.appendChild(row);
            }
        }
    } else {
        row = document.createElement("tr");
        cell = document.createElement("td"); cell.innerText = "No one's walked yet!";
        row.appendChild(cell);
        leaderboard_table.appendChild(row);
    }
    div.appendChild(leaderboard_table);
}

function clear_leaderboard(div) {
    while (div.firstChild) {
        div.removeChild(div.firstChild);
    }
}

function add_leaderboard_heading(div, label) {
    let leaderboardHeading = document.createElement("h2");
    leaderboardHeading.textContent = label;
    div.appendChild(leaderboardHeading);
}

function add_leaderboard_loading(div) {
    let leaderboardLoading = document.createElement("p");
    leaderboardLoading.textContent = "Loading...";
    div.appendChild(leaderboardLoading);
}