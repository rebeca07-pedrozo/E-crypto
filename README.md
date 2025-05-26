# E-cryto
Plataforma cripto con API (FastAPI), scrapers en tiempo real, análisis OLAP y predicción de precios con LSTM, visualizado en Streamlit.

<p align="center">
  <img src="https://github.com/rebeca07-pedrozo/E-crypto/blob/main/pics/E-Crypto.png?raw=true" alt="E-CRYPTO" width="300"/>
</p>

## Archivos esenciales para ejecutar la app funcionalmente

| Archivo                      | Función principal                                             | ¿Necesario para producción? |
|-----------------------------|--------------------------------------------------------------|-----------------------------|
| `api/main.py`                   | API con FastAPI que expone datos de criptomonedas            | Sí                          |
| `dashboard/app.pypy` | Dashboard visual con análisis OLAP y predicción LSTM          | Sí                          |

---
## Recomendación para el flujo de trabajo - Initializer steps

initializer steps
1. python -m venv env
2. source env/bin/activate
3. pip install -r requirements.txt
4. python -m streamlit run /workspaces/E-trading/dashboard/app.py
---

## Archivos para mantenimiento y actualización de datos

| Archivo                         | Función principal                                               | Uso recomendado               |
|--------------------------------|----------------------------------------------------------------|------------------------------|
| `scraper/crypto_scraper.py` | Scraper para obtener datos actualizados de CoinMarketCap       | Actualizar base de datos MongoDB |
| `scraper/CoinGeko.py`      | Scraper para obtener datos vía API de CoinGecko                | Alternativa para actualización |
| `mongo.py`                     | Conexión e inserción en MongoDB                                | Utilizado por scrapers         |


---

## Notas importantes

- Para que la app funcione correctamente, deben tener datos en la base MongoDB.  
- La API (`main.py`) y el dashboard (`dashboard/app.py`) dependen de que Mongo tenga datos, pero no dependen directamente de los scrapers.  
- Los scrapers solo se usan para **llenar o actualizar la base de datos**; pueden ejecutarse periódicamente si se desea.  

---


 
