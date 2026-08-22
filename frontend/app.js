const form = document.getElementById('recordForm');
const thresholdInput = document.getElementById('threshold');
const thresholdVal = document.getElementById('thresholdVal');

thresholdInput.addEventListener('input', () => {
  thresholdVal.textContent = thresholdInput.value;
});


form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const payload = {
    Nombre: document.getElementById('nombre').value,
    edad: parseInt(document.getElementById('edad').value, 10),
    sexo: document.getElementById('sexo').value,
    Sintomas: document.getElementById('sintomas').value
  };

  results.textContent = 'Analizando...';

  try {
    // send to add_record so the server predicts and stores the record
    const res = await fetch('/add_record', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    // show saved record
    const savedDiv = document.getElementById('cardSaved');
    savedDiv.innerHTML = `<strong>Guardado:</strong><pre>${JSON.stringify(data.saved, null, 2)}</pre>`;

    // render predictions table (filter by threshold)
    const preds = data.predictions || [];
    const predDiv = document.getElementById('predictions');
    const thresh = Number(thresholdInput.value || 0);
    const filteredPreds = preds.filter(p => {
      const perc = (p.similarity_percent !== undefined && p.similarity_percent !== null) ? p.similarity_percent : Math.round(((p.avg_score+1)/2*100)*100)/100;
      return perc >= thresh;
    });
    if (filteredPreds.length === 0) {
      predDiv.innerHTML = '<em>No hay predicciones por encima del umbral</em>';
    } else {
      let html = '<table><tr><th>Diagnóstico</th><th>Similitud (%)</th></tr>';
      filteredPreds.forEach(p => {
        const perc = (p.similarity_percent !== undefined && p.similarity_percent !== null) ? p.similarity_percent : Math.round(((p.avg_score+1)/2*100)*100)/100;
        html += `<tr><td>${p.diagnostico}</td><td style="text-align:right">${perc}%</td></tr>`;
      });
      html += '</table>';
      predDiv.innerHTML = html;
    }

    // render matches table
    const matches = data.matches || [];
    const matchDiv = document.getElementById('matches');
    const threshMatches = Number(thresholdInput.value || 0);
    const filteredMatches = matches.filter(m => (m.similarity_percent || 0) >= threshMatches);
    if (filteredMatches.length === 0) {
      matchDiv.innerHTML = '<em>No hay registros similares por encima del umbral</em>';
    } else {
      let mhtml = '<table><tr><th>Nombre</th><th>Síntomas</th><th>Similitud (%)</th></tr>';
      filteredMatches.forEach(m => {
        const meta = m.meta || {};
        mhtml += `<tr><td>${meta.Nombre || ''}</td><td>${meta.Sintomas || ''}</td><td style="text-align:right">${m.similarity_percent}</td></tr>`;
      });
      mhtml += '</table>';
      matchDiv.innerHTML = mhtml;
    }
  } catch (err) {
    results.textContent = 'Error: ' + err;
  }
});
