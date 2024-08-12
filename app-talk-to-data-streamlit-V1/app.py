import os
import streamlit as st
import pandas as pd
import dotenv
from dotenv import load_dotenv
import pymongo

from pandasai import Agent
from pandasai import SmartDataframe
from pandasai.llm.openai import OpenAI
from deep_translator import GoogleTranslator
import matplotlib
from pandasai.responses.response_parser import ResponseParser


pd.set_option('display.float_format', lambda x: '%.2f' % x)
matplotlib.use('Agg')


dotenv.load_dotenv(dotenv.find_dotenv())
openai_api_key = st.secrets["OPENAI_API_KEY"]
pandas_ai_api_key = st.secrets["PANDAS_AI_API_KEY"]
db_user = st.secrets["DB_USER"]
db_password = st.secrets["DB_PASSWORD"]
db_host = st.secrets["DB_HOST"]

llm = OpenAI(api_token=openai_api_key)


def extract_transform_data():
    client_hml = pymongo.MongoClient('mongodb+srv://'+db_user+':'+db_password+db_host, unicode_decode_error_handler='ignore')
    
    db = client_hml['analytics']
    collection = db["score_devedores"]
    df = pd.json_normalize(list(collection.find()))

    df_final = df.drop(columns=['DOCUMENTO', 'PT_TOTAL', 'PT_SOMA'])

    return df_final

df = extract_transform_data()

st.set_page_config(page_title="App Talk to Data", page_icon=":bar_chart:", layout="wide")
logo_path = 'https://raw.githubusercontent.com/segal0641/app-talk-to-data-streamlit_V1/main/app-talk-to-data-streamlit-V1/imagens/logo_inovally.png'
link_inovally = "https://inovally.com.br/"

st.logo(logo_path, link=link_inovally)

st.markdown("<h1 style='text-align: center; color: #14D2AA;'>App Talk to Data</h1>", unsafe_allow_html=True)

st.subheader("Use o poder da IA Generativa para descobrir insights sobre os devedores do seu município! 📊📈")
imagem_url = 'https://raw.githubusercontent.com/segal0641/app-talk-to-data-streamlit_V1/main/app-talk-to-data-streamlit-V1/imagens/image.png'
st.image(imagem_url)



dados = Agent(df, config={"llm": llm, "enable_cache": False})


st.dataframe(df)


st.subheader("No espaço abaixo, escreva o que você gostaria de ver nos dados 👇")
texto_usuario = st.text_area("Ex: Qual é o nome do contribuinte com maior montante financeiro? e qual é o montante financeiro dele? Me mostre um gráfico de pizza com o percentual de cada categoria para TAG_SCORE. Uma cor diferente para cada categoria")
texto_usuario = texto_usuario + ', responda em português'
texto_usuario_traduzido = GoogleTranslator(source='auto', target='en').translate(texto_usuario)
texto_usuario_traduzido = texto_usuario_traduzido.replace('\u200b\u200b', '')


#if st.button("Gerar resultado"):
    #if texto_usuario_traduzido:
        #with st.spinner("Gerando resultado..."):
            #answer = dados.chat(texto_usuario_traduzido)
            #st.write(answer)




chart_path = "./app-talk-to-data-streamlit_v1/exports/charts/temp_chart.png"
chart_path2 = "/mount/src/app-talk-to-data-streamlit_v1/exports/charts/temp_chart.png"
#text = texto_usuario_traduzido.lower()
#lista_strings = ['gráfico', 'grafico']
#
#string_set = set(text.split())
#list_set = set(lista_strings)
#
#if st.button("Gerar resultado"):
    #if texto_usuario_traduzido:
        #with st.spinner("Gerando resultado..."):
            #answer = dados.chat(texto_usuario_traduzido)
            #if list_set.intersection(string_set):
                #st.success(answer)
                #st.set_option('deprecation.showPyplotGlobalUse', False)
                #st.pyplot()
                ##st.image(chart_path)
            #else:
                #st.write(answer)




class StreamlitResponse(ResponseParser):
    def __init__(self, context) -> None:
        super().__init__(context)

    def format_dataframe(self, result):
        st.dataframe(result["value"])
        return

    def format_plot(self, result):
        st.image(result["value"])
        return

    def format_other(self, result):
        st.write(result["value"])
        return

if st.button("Gerar resultado"):
    if texto_usuario_traduzido:
        llm = OpenAI(api_token=os.environ["OPENAI_API_KEY"])
        query_engine = SmartDataframe(
            df,
            config={
                "llm": llm,
                "response_parser": StreamlitResponse
            },
        )

    answer = query_engine.chat(texto_usuario_traduzido)