async function loadAllLogs() {
  const res = await fetch("/admin/logs");
  const data = await res.json();

  const tbody = document.querySelector("#adminLogsTable tbody");
  tbody.innerHTML = "";

  if (!data.logs || data.logs.length === 0) {
    tbody.innerHTML = "<tr><td colspan='5'>No logs found</td></tr>";
    return;
  }

  data.logs.forEach(log => {
    const row = `
      <tr>
        <td>${log.username}</td>
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
  await fetch(`/admin/logs/${id}`, { method: "DELETE" });
  loadAllLogs();
}

loadAllLogs();
