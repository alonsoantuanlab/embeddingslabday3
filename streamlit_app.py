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
        # call add_record so it is saved and prediction returned
        res = requests.post(f'{API_URL}/add_record', json=payload)
        try:
            data = res.json()
            saved = data.get('saved')
            preds = data.get('predictions', [])
            matches = data.get('matches', [])

            st.subheader('Registro Guardado')
            st.json(saved)

            if preds:
                st.subheader('Predicciones')
                import pandas as pd
                df = pd.DataFrame([{'Diagnostico': p['diagnostico'], 'Similitud (%)': p.get('similarity_percent') } for p in preds])
                st.table(df)

            if matches:
                st.subheader('Registros Similares')
                dfm = pd.DataFrame([{'Nombre': m['meta'].get('Nombre'), 'Sintomas': m['meta'].get('Sintomas'), 'Similitud (%)': m.get('similarity_percent')} for m in matches])
                st.table(dfm)
        except Exception:
            st.error('Error al comunicarse con la API')
