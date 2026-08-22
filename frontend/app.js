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
    // show saved record and top prediction
    let out = 'Guardado:\n' + JSON.stringify(data.saved || data.saved, null, 2) + '\n\nPredicciones:\n' + JSON.stringify(data.predictions || data.predictions, null, 2);
    results.textContent = out;
  } catch (err) {
    results.textContent = 'Error: ' + err;
  }
});
