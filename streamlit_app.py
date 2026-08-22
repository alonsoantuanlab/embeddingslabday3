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
    thresh = st.slider('Umbral de similitud (%) para mostrar resultados', 0, 100, 50)

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
                # filter preds by threshold
                filtered = []
                for p in preds:
                    perc = p.get('similarity_percent')
                    if perc is None:
                        perc = round(((p.get('avg_score', 0)+1)/2*100), 2)
                    if perc >= thresh:
                        filtered.append({'Diagnostico': p['diagnostico'], 'Similitud (%)': perc})
                if filtered:
                    st.subheader('Predicciones')
                    import pandas as pd
                    df = pd.DataFrame(filtered)
                    st.table(df)
                else:
                    st.info('No hay predicciones por encima del umbral')

            if matches:
                dfm_list = []
                for m in matches:
                    perc = m.get('similarity_percent', 0)
                    if perc >= thresh:
                        dfm_list.append({'Nombre': m['meta'].get('Nombre'), 'Sintomas': m['meta'].get('Sintomas'), 'Similitud (%)': perc})
                if dfm_list:
                    st.subheader('Registros Similares')
                    import pandas as pd
                    dfm = pd.DataFrame(dfm_list)
                    st.table(dfm)
                else:
                    st.info('No hay registros similares por encima del umbral')
        except Exception:
            st.error('Error al comunicarse con la API')
