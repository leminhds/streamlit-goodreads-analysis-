import streamlit as st
from streamlit_lottie import st_lottie
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(layout='wide')

def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

file_url = 'https://assets4.lottiefiles.com/temp/lf20_aKAfIn.json'
lottie_book = load_lottieurl(file_url)
st_lottie(lottie_book, speed=1, height=200, key="initial")

st.title('Analyze your Goodreads Books and Reading')
st.subheader('A Web App by Le Minh')

'''
Hello hello! Welcome to Goodreads Analyzer, an App dedicated to
help you understand your Goodreads reading habit.
This app currently include feature such as understanding the age of the books that you read,
the length of the book, and the time it takes you to finish those books
(only if you have filled in the starting date of course, I always forget to
do that myself...)
'''

goodreads_file = st.file_uploader('Please import your Goodreads Data')
if goodreads_file is None:
    df = pd.read_csv('goodreads_library_export.csv')
    st.write("Analyzing Le Minh's Goodreads history")
else:
    df = pd.read_csv('goodreads_file')
    st.write('Analyzing your Goodreads history')

df['Days to Finish'] = (pd.to_datetime(df['Date Read']) - pd.to_datetime(df['Date Added'])).dt.days
books_finished_filtered = df[(df['Exclusive Shelf'] == 'read') & (df['Days to Finish'] >= 0)]
u_books = len(books_finished_filtered['Book Id'].unique())
u_authors = len(books_finished_filtered['Author'].unique())
mode_author = books_finished_filtered['Author'].mode()[0]
st.write(f'It looks like you have finished {u_books} books with a total of {u_authors} unique authors. '
         f'Your most read author is {mode_author}!')
st.write(f'Your app results can be found below, we have analyzed everything from your'
         f' book length distribution your reading rate per year. Take a '
         f'look around, all the graphs are interactive!')

row1_col1, row1_col2 = st.beta_columns(2)
row2_col1, row2_col2 = st.beta_columns(2)

df['Year Finished'] = pd.to_datetime(df['Date Read']).dt.year
books_per_year = df.groupby('Year Finished')['Book Id'].count().reset_index()
books_per_year.columns = ['Year Finished', 'Count']

fig_books_per_year = px.bar(books_per_year, x='Year Finished', y='Count',
    title='Books Finished per Year')
with row1_col1:
    year_finished_mode = int(df['Year Finished'].mode()[0])
    st.plotly_chart(fig_books_per_year)
    st.write(f'You finished the most books in {year_finished_mode}')



fig_days_to_finish = px.histogram(books_finished_filtered, x='Days to Finish',
                                  title='Number of days to finish a book')
with row1_col2:
    st.plotly_chart(fig_days_to_finish)
    finish_speed_mean = int(books_finished_filtered['Days to Finish'].mean())
    st.write(f'On average, it took you {finish_speed_mean} to finish a book. Note that you might have not'
             f'added the start reading date or finishing date for a lot of boos. Therefore this metric might'
             f'not be perfect')

fig_num_pages = px.histogram(df, x='Number of Pages', title='Book Length Histogram')
with row2_col1:
    st.plotly_chart(fig_num_pages)
    pages_average = int(df['Number of Pages'].mean())
    st.write(f'On average, the length of your books are {pages_average} pages long')

books_publication_year = df.groupby('Original Publication Year')['Book Id'].count().reset_index()
books_publication_year.columns = ['Year Published', 'Count']
fig_year_published = px.bar(books_publication_year, x='Year Published', y='Count', title='Book Age Plot')
fig_year_published.update_xaxes(range=[1850, 2021])
with row2_col2:
    st.plotly_chart(fig_year_published)
    st.write('This chart is zoomed into the period of 1850-2021, but is interactive'
            ' so try zooming in/out on interesting periods!')


