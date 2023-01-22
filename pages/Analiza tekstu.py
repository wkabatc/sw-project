from textblob import TextBlob
import streamlit as st
from sentimentpl.models import SentimentPLModel
from youtube_comment_downloader import *
from utils.utils import *
from utils.levenshtein import *
from langdetect import detect

st.set_page_config(
    layout = 'wide',
    page_title = 'Analiza tekstu'
)

model = SentimentPLModel(from_pretrained='latest')

st.header('Analiza tekstu')

with st.expander('Sprawdź sentyment', expanded = True):

    colA1, colA2, a1, a2 = st.columns([4, 0.6, 1, 1])
    text = colA1.text_input('Podaj tekst, który chcesz przeanalizować')
    lang = colA2.selectbox('Analizowany język', ('PL', 'EN'))
        
    if text:
        detectedLang = detect(text)
        if detectedLang.upper() != lang and (detectedLang == 'pl' or detectedLang == 'en'):
            st.warning('Język wykryty w komentarzach to: ' + detectedLang.upper(), icon = '⚠️')
        else:
            colB1, colB2, colB3, b1 = st.columns([1, 1.5, 1.3, 8])

            if detectedLang != 'pl' and detectedLang != 'en':
                lang = 'PL'

            if lang == 'PL':
                sentiment = model(text).item()
                with colB3:
                    st.write('Sentyment: ', round(sentiment, 2))
            else:
                blob = TextBlob(text)
                sentiment = blob.sentiment.polarity
                subjectivity = blob.sentiment.subjectivity

                with colB3:
                    st.write('Sentyment: ', round(sentiment, 2))
                    st.write('Subiektywność: ', round(subjectivity, 2))

            colB1.metric('Wykryty język: ',  detectedLang.upper())
            colB2.metric('Ton tekstu:',  defineMood(sentiment))
        
with st.expander('Odległość levenshteina', expanded = True):

    colB1, colB2, b1, b2 = st.columns([1, 1, 1, 1])
    w1 = colB1.text_input('Pierwsze słowo')
    w2 = colB2.text_input('Drugie słowo')
    
    if w1 and w2:
        st.write('Odległość Levenshteina: ', lev(w1, w2))