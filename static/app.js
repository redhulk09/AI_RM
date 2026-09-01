const form = document.querySelector('#risk-form');
const table = document.querySelector('#risks');
const message = document.querySelector('#message');

const esc = (value) => String(value ?? '').replace(/[&<>\"']/g, (c) => ({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',"'":'&#039;'}[c]));

async function loadRisks() {
  const response = await fetch('/api/risks');
  const risks = await response.json();
  table.innerHTML = risks.map((risk) => `
    <tr>
      <td><strong>${esc(risk.title)}</strong><small>${esc(risk.category)}</small></td>
      <td>${esc(risk.owner)}</td>
      <td>${risk.adjusted_score}/${risk.base_score}</td>
      <td><span class="badge ${risk.severity.toLowerCase()}">${esc(risk.severity)}</span></td>
      <td>${esc(risk.recommendation || 'Not analyzed')}</td>
      <td class="actions"><button onclick="analyzeRisk(${risk.id})">Analyze</button><button class="danger" onclick="deleteRisk(${risk.id})">Delete</button></td>
    </tr>`).join('') || '<tr><td colspan="6">No risks yet.</td></tr>';
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  const data = Object.fromEntries(new FormData(form));
  ['likelihood', 'impact', 'control_effectiveness'].forEach((key) => { data[key] = Number(data[key]); });
  const response = await fetch('/api/risks', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data)});
  if (!response.ok) { message.textContent = 'Could not create risk.'; return; }
  form.reset();
  message.textContent = 'Risk created.';
  await loadRisks();
});

document.querySelector('#refresh').addEventListener('click', loadRisks);

async function analyzeRisk(id) {
  await fetch(`/api/risks/${id}/analyze`, {method: 'POST'});
  await loadRisks();
}

async function deleteRisk(id) {
  if (!confirm('Delete this risk?')) return;
  await fetch(`/api/risks/${id}`, {method: 'DELETE'});
  await loadRisks();
}

loadRisks();
