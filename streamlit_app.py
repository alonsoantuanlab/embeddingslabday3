import streamlit as st
import requests

API_URL = st.secrets.get('API_URL', 'http://localhost:8000')

st.title('Streamlit — Analizador de Registros Médicos')

st.markdown('Este dashboard llama al backend FastAPI para analizar registros y mostrar similitudes.')

if st.button('Cargar registros ejemplo'):
    r = requests.get(f'{API_URL}/records')
    st.json(r.json())

with st.form('predict'):
    nombre = st.text_input('Nombre')
    edad = st.number_input('Edad', min_value=0, max_value=120, value=30)
    sexo = st.selectbox('Sexo', ['F','M'])
    sintomas = st.text_area('Síntomas')
    submitted = st.form_submit_button('Analizar')
    if submitted:
        payload = {"Nombre": nombre, "edad": int(edad), "sexo": sexo, "Sintomas": sintomas}
        res = requests.post(f'{API_URL}/predict', json=payload)
        st.json(res.json())
