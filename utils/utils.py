def defineMood(x):
   if x >= 0.5:
       return 'Pozytywny'
   elif x <= -0.5:
       return 'Negatywny'
   else:
       return 'Neutralny'
   
def renameColums(df):
    df.rename(columns = {
        'content': 'Treść',
        'author': 'Autor',
        'time': 'Czas',
        'isReply': 'Odpowiedź?',
        'sentiment': 'Sentyment',
        'tone': 'Ton',
        'subjectivity': 'Subiektywność',
        'lev': 'Levenshtein'
    }, inplace = True)