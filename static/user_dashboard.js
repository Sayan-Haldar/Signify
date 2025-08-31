async function loadUserLogs() {
  const res = await fetch("/user/logs");
  const data = await res.json();

  const tbody = document.querySelector("#userLogsTable tbody");
  tbody.innerHTML = "";

  if (!data.logs || data.logs.length === 0) {
    tbody.innerHTML = "<tr><td colspan='4'>No logs found</td></tr>";
    return;
  }

  data.logs.forEach(log => {
    const row = `
      <tr>
        <td>${log.date || log.timestamp}</td>
        <td>${Number(log.confidence).toFixed(2)}%</td>
        <td>${Number(log.time).toFixed(2)}s</td>
        <td><button onclick="deleteLog('${log._id}')">Delete</button></td>
      </tr>
    `;
    tbody.innerHTML += row;
  });
}

async function deleteLog(id) {
  await fetch(`/user/logs/${id}`, { method: "DELETE" });
  loadUserLogs();
}

loadUserLogs();
