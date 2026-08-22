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
    const res = await fetch('/predict', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    results.textContent = JSON.stringify(data, null, 2);
  } catch (err) {
    results.textContent = 'Error: ' + err;
  }
});
