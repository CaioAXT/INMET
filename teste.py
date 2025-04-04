import pandas as pd

caminho = r"C:\Users\caio.alves\OneDrive - ARAXA\Python\AXT\Projetos\INMET\.streamlit\BaseDeDados\INMET.csv"

df = pd.read_csv(caminho)

print(len(df))
