const form = document.getElementById('recordForm');
const thresholdInput = document.getElementById('threshold');
const thresholdVal = document.getElementById('thresholdVal');
const results = document.getElementById('results');

if (thresholdInput && thresholdVal) {
  thresholdInput.addEventListener('input', () => {
    thresholdVal.textContent = thresholdInput.value;
  });
}

if (form) {
  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const payload = {
      Nombre: document.getElementById('nombre').value,
      edad: parseInt(document.getElementById('edad').value, 10),
      sexo: document.getElementById('sexo').value,
      Sintomas: document.getElementById('sintomas').value
    };

    if (results) {
      results.textContent = 'Analizando...';
    }

    try {
      const res = await fetch('/add_record', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload)
      });

      if (!res.ok) {
        throw new Error(`Error HTTP ${res.status}`);
      }

      const data = await res.json();
      const savedDiv = document.getElementById('cardSaved');
      if (savedDiv) {
        savedDiv.innerHTML = `<strong>Guardado:</strong><pre>${JSON.stringify(data.saved, null, 2)}</pre>`;
      }

      const preds = data.predictions || [];
      const predDiv = document.getElementById('predictions');
      const thresh = Number(thresholdInput ? thresholdInput.value : 0);
      const filteredPreds = preds.filter(p => {
        const perc = (p.similarity_percent !== undefined && p.similarity_percent !== null)
          ? p.similarity_percent
          : Math.round(((p.avg_score + 1) / 2 * 100) * 100) / 100;
        return perc >= thresh;
      });

      if (predDiv) {
        if (filteredPreds.length === 0) {
          predDiv.innerHTML = '<em>No hay predicciones por encima del umbral</em>';
        } else {
          let html = '<table><tr><th>Diagnóstico</th><th>Similitud (%)</th></tr>';
          filteredPreds.forEach(p => {
            const perc = (p.similarity_percent !== undefined && p.similarity_percent !== null)
              ? p.similarity_percent
              : Math.round(((p.avg_score + 1) / 2 * 100) * 100) / 100;
            html += `<tr><td>${p.diagnostico}</td><td style="text-align:right">${perc}%</td></tr>`;
          });
          html += '</table>';
          predDiv.innerHTML = html;
        }
      }

      const matches = data.matches || [];
      const matchDiv = document.getElementById('matches');
      const threshMatches = Number(thresholdInput ? thresholdInput.value : 0);
      const filteredMatches = matches.filter(m => (m.similarity_percent || 0) >= threshMatches);

      if (matchDiv) {
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
      }

      if (results) {
        results.textContent = 'Análisis completado.';
      }
    } catch (err) {
      if (results) {
        results.textContent = 'Error: ' + err.message;
      }
      if (document.getElementById('predictions')) {
        document.getElementById('predictions').innerHTML = '<em>Ocurrió un error al procesar la solicitud.</em>';
      }
      if (document.getElementById('matches')) {
        document.getElementById('matches').innerHTML = '<em>Intenta nuevamente.</em>';
      }
    }
  });
}
