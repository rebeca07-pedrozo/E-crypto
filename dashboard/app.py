import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import streamlit as st
from analysis.queries import listar_criptos, buscar_por_nombre, resumen_precios

st.title("Dashboard de Criptomonedas")

st.header("Resumen de precios")
resumen = resumen_precios()
if resumen:
    st.write(f"Precio máximo: {resumen['max_price']:.2f}")
    st.write(f"Precio mínimo: {resumen['min_price']:.2f}")
    st.write(f"Precio promedio: {resumen['avg_price']:.2f}")
else:
    st.write("No hay datos estadísticos disponibles.")

st.header("Listado de criptomonedas")
criptos = listar_criptos()
for cripto in criptos:
    st.write(f"**{cripto['name']}**: {cripto['price']}")

st.header("Buscar cripto por nombre")
busqueda = st.text_input("Nombre de la criptomoneda:")
if busqueda:
    resultado = buscar_por_nombre(busqueda)
    if resultado:
        st.write(f"**{resultado['name']}**: {resultado['price']}")
    else:
        st.write("No se encontró la criptomoneda.")