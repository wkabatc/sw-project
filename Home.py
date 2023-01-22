from textblob import TextBlob
import pandas as pd
import streamlit as st
from sentimentpl.models import SentimentPLModel
from youtube_comment_downloader import *
import numpy as np
from utils.utils import *
from utils.levenshtein import *
from langdetect import detect
import altair as alt

st.set_page_config(
    layout = 'wide',
    page_title = 'Home - analiza komentarzy na YT'
)
pd.set_option('display.width', 1200)

with open('./styles/styles.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html = True)

model = SentimentPLModel(from_pretrained = 'latest')

a1, colA1, a2 = st.columns([1, 2, 1])
colA1.header('Adres filmu na YouTube')

b1, colB1, colB2, colB3, b2 = st.columns([1, 1.2, 0.4, 0.4, 1])
ytVideoUrl = colB1.text_input('Podaj adres filmu, którego komentarze chcesz przeanalizować')
lang = colB2.selectbox('Analizowany język', ('PL', 'EN'))
levWord = colB3.text_input('Słowo porównawcze')

if ytVideoUrl:
    print('\nDownloading comments...')

    downloader = YoutubeCommentDownloader()
    comments = downloader.get_comments_from_url(ytVideoUrl, sort_by=SORT_BY_RECENT)

    commsDicts = []
    warnFlag = False

    for i, c in enumerate(comments):
        content = c['text']

        if i == 0:
            try:                                                          
                detectedLang = detect(content)

                if detectedLang.upper() != lang and (detectedLang == 'pl' or detectedLang == 'en'):
                    st.warning('Język wykryty w komentarzach to: ' + detectedLang.upper(), icon = '⚠️')
                    warnFlag = True
                    break

                if detectedLang != 'pl' and detectedLang != 'en':
                    st.info('Język wykryty w komentarz to: ' + detectedLang.upper() + '. Włączono tryb manualnego wyboru języka dla algorytmy analizującego komentarze.', icon = 'ℹ️')                                     
            except:                                                       
               st.info('Wystąpił problem z analizą języka. Włączono tryb manualnego wyboru języka dla algorytmu analizującego komentarze.', icon = 'ℹ️')                                          
               print('There was a problem parsing the language. The detected language was set automatically.')

        if lang == 'PL':
            sentiment = model(content).item()
        else:
            blob = TextBlob(content)
            sentiment = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity

        comment = {
            'content': content,
            'author': c['author'],
            'time': c['time'].split('(')[0],
            'isReply': c['reply'],
            'sentiment': sentiment,
            'timeParsed': c['time_parsed']
        }

        if lang == 'EN':
            comment['subjectivity'] = subjectivity

        if levWord:
            comment['lev'] = lev(levWord, content.split()[0])
        
        comment['tone'] = defineMood(sentiment)
        commsDicts.append(comment)
    
    if len(commsDicts) > 0:
        chartDf = pd.DataFrame.from_dict(commsDicts)
        chartDf.sort_values(by = 'timeParsed', ignore_index = True, ascending = False, inplace = True)
        chartDf.index = np.arange(1, len(chartDf) + 1)
        renameColums(chartDf)

        tableDf = chartDf
        tableDf = tableDf.drop('timeParsed', axis = 1)

        chartDf['Index'] = chartDf.index
        chartDf['Długość komentarza'] = chartDf['Treść'].str.len()

        dfHeight = 560

        if len(commsDicts) < 15:
            dfHeight = (len(commsDicts) + 1) * 35
        
        st.dataframe(tableDf, height = dfHeight, use_container_width = True)
        print('\nComments downloaded.')

        d1, colD1, colD2, d2 = st.columns([0.7, 0.6, 2, 0.7])

        with colD1:
            st.metric('Znaleziono', len(commsDicts), 'komentarzy')
            st.metric('Max', round(chartDf['Sentyment'].max(), 2), 'sentyment')

            if lang == 'EN':
                st.metric('Max', round(chartDf['Subiektywność'].max(), 2), 'subiektywność')
            
            st.metric('Przeważający', chartDf['Ton'].mode()[0], 'Ton')

        bubbleChart = alt.Chart(chartDf).mark_circle().encode(
            alt.X('Index', axis=alt.Axis(tickMinStep = 1)), 
            y = 'Sentyment', 
            color = 'Ton', 
            size = 'Długość komentarza'
        ).properties(height = 500)

        with colD2:
            st.write('Sentyment komentarzy')
            st.altair_chart(bubbleChart, use_container_width = True)

        if levWord:
            e1, colE1, e2 = st.columns([0.7, 2.6, 0.7])
            fstWord = chartDf['Treść'].str.split().str[0] 
            chartDf['Pierwsze słowo'] = fstWord

            barChart = alt.Chart(chartDf).mark_bar().encode(
                alt.Y('Levenshtein', axis=alt.Axis(tickMinStep = 1)), 
                x = "Pierwsze słowo"
            ).properties(height = 300).configure_legend(orient = 'right')
            
            with colE1:
                st.write('Odległości Levenshteina')
                st.altair_chart(barChart, use_container_width = True)

        if lang == 'EN':
            f1, colF1, f2 = st.columns([0.7, 2.6, 0.7])

            line = alt.Chart(chartDf).mark_line(
                point = True
            ).encode(
                alt.X('Index', axis = alt.Axis(tickMinStep = 1), sort = 'descending'),
                y = 'Subiektywność',
                color = alt.Color('Czas', sort = ['timeParsed']),
            )

            rule = alt.Chart(chartDf).mark_rule().encode(
                y = 'average(Subiektywność)'
            )

            subjChart = (line + rule).properties(height = 350)
            subjChart.layer[0].encoding.y.title = 'Subiektywność'

            with colF1:
                st.write('Subiektywność komentarzy')
                st.altair_chart(subjChart, use_container_width = True)

        g1, colG1, g2, colG2, G3 = st.columns([0.7, 1.3, 0.1, 1.2, 0.7])

        mostPosComm = chartDf[chartDf['Sentyment'] == chartDf['Sentyment'].max()].iloc[0]
        mostNegComm = chartDf[chartDf['Sentyment'] == chartDf['Sentyment'].min()].iloc[0]
        commDfData = {'Ton': ['Pozytywny', 'Negatywny'], 'Komentarz': [mostPosComm['Treść'], mostNegComm['Treść']], 'Sentyment': [mostPosComm['Sentyment'], mostNegComm['Sentyment']]}
        commDf = pd.DataFrame(data = commDfData, index = (1, 2))

        pieChartDf = chartDf.groupby('Ton').agg(count=('Index', 'count')).reset_index()
        pieChartDf = pieChartDf.rename(columns = {'count': 'Suma'})
    
        pieChart = alt.Chart(pieChartDf).mark_arc().encode(
            theta=alt.Theta(field = 'Suma', type = 'quantitative'),
            color=alt.Color(field = 'Ton', type = 'nominal'),
        ).properties(height = 300).configure_legend(orient = 'right')
        
        with colG1:
            st.write('Charakter komentarzy')
            st.bar_chart(data = chartDf, x = 'Index', y = 'Ton', height = 150, use_container_width = True)
            st.write('Najbardziej pozytywny i negatywny komentarz')
            st.dataframe(commDf, use_container_width = True)
        with colG2:
            st.write('Udział komentarzy o różnym tonie')
            st.altair_chart(pieChart, use_container_width = True)

    elif warnFlag == False:
        st.error('Nie znaleziono komentarzy!', icon = '🚨')
        print('\nComments not found.')