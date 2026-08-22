const form = document.getElementById('recordForm');
const results = document.getElementById('results');

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

    // render predictions table
    const preds = data.predictions || [];
    const predDiv = document.getElementById('predictions');
    if (preds.length === 0) {
      predDiv.innerHTML = '<em>No hay predicciones</em>';
    } else {
      let html = '<table border="1" cellpadding="6"><tr><th>Diagnóstico</th><th>Similitud (%)</th></tr>';
      preds.forEach(p => {
        html += `<tr><td>${p.diagnostico}</td><td style="text-align:right">${p.similarity_percent ?? p.similarity_percent === 0 ? p.similarity_percent : (p.similarity_percent || (Math.round(((p.avg_score+1)/2*100)*100)/100))}%</td></tr>`;
      });
      html += '</table>';
      predDiv.innerHTML = html;
    }

    // render matches table
    const matches = data.matches || [];
    const matchDiv = document.getElementById('matches');
    if (matches.length === 0) {
      matchDiv.innerHTML = '<em>No hay registros similares</em>';
    } else {
      let mhtml = '<table border="1" cellpadding="6"><tr><th>Nombre</th><th>Síntomas</th><th>Similitud (%)</th></tr>';
      matches.forEach(m => {
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
