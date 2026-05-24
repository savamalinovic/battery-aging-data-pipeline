# NASA Battery Cloud Pipeline

Projekat za obradu NASA Li-ion Battery Aging podataka.

Cilj projekta je napraviti data pipeline koji preuzima raw `.mat` fajlove, čisti i transformiše podatke, računa battery health metrike, snima izlaze kao Parquet fajlove i omogućava Streamlit dashboard.

## Scope prve verzije

Radimo:

- lokalni pipeline
- cleaned Parquet fajlove
- analytics Parquet fajlove
- data quality output
- Streamlit dashboard
- Docker pipeline
- AWS one-time pipeline run
- Lightsail dashboard hosting

Ne radimo:

- ML model
- RUL predikciju modelom
- posebne alerte
- sensor quality summary kao poseban output
- ambijentalnu temperaturu kao zaseban trend dashboard

## Status

Trenutno: inicijalni skeleton projekta.
