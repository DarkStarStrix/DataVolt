import pandas as pd
import dash
from dash import dcc, html
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import base64
from io import BytesIO


COLORS = {
    'background': '#f8f9fa',
    'card': '#ffffff',
    'text': '#2c3e50',
    'positive': '#27ae60',
    'negative': '#e74c3c',
    'neutral': '#3498db'
}

df = pd.read_csv ('C:/Users/kunya/PycharmProjects/DataVolt/Market_Mind/Data/preprocessed_data.csv')
positive_posts = df [df ['label'] == 1]
negative_posts = df [df ['label'] == 0]


def generate_wordcloud(text):
    wordcloud = WordCloud (
        width=800,
        height=400,
        background_color='white',
        prefer_horizontal=0.7,
        max_words=100,
        color_func=lambda *args, **kwargs: (0, 0, 0),
    ).generate (' '.join (text))

    buffer = BytesIO ()
    plt.figure (figsize=(10, 5))
    plt.imshow (wordcloud, interpolation='bilinear')
    plt.axis ('off')
    plt.savefig (buffer, format='png', bbox_inches='tight', pad_inches=0)
    plt.close ()
    buffer.seek (0)
    img = base64.b64encode (buffer.getvalue ()).decode ()
    return f'data:image/png;base64,{img}'



positive_wordcloud = generate_wordcloud (positive_posts ['text'])
negative_wordcloud = generate_wordcloud (negative_posts ['text'])


sentiment_fig = px.pie (
    names=['Positive', 'Negative'],
    values=[len (positive_posts), len (negative_posts)],
    title='Sentiment Distribution',
    color_discrete_sequence=[COLORS ['positive'], COLORS ['negative']]
)
sentiment_fig.update_layout (
    height=400,
    showlegend=True,
    legend=dict (orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)


topics_df = pd.DataFrame (df ['text'].value_counts ().head (10)).reset_index ()
topics_df.columns = ['Topic', 'Count']

topics_fig = px.bar (
    topics_df,
    x='Topic',
    y='Count',
    title='Top 10 Most Discussed Topics',
    color_discrete_sequence=[COLORS ['neutral']]
)
topics_fig.update_layout (
    height=400,
    xaxis_tickangle=-45,
    xaxis_title="Topics",
    yaxis_title="Frequency"
)


app = dash.Dash (__name__, meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}])


def create_stat_card(title, value, color):
    return html.Div ([
        html.H3 (title, style={'color': COLORS ['text'], 'fontSize': '1.1rem', 'margin': '0'}),
        html.H2 (f"{value:,}", style={'color': color, 'fontSize': '2rem', 'margin': '10px 0'})
    ], className='stat-card')


app.layout = html.Div ([
    html.H1 ('Data Engineering Social Media Analysis',
             style={'textAlign': 'center', 'color': COLORS ['text'], 'padding': '20px 0'}),

    html.Div ([
        html.Div ([
            create_stat_card ('Total Posts', len (df), COLORS ['neutral']),
            create_stat_card ('Positive Posts', len (positive_posts), COLORS ['positive']),
            create_stat_card ('Negative Posts', len (negative_posts), COLORS ['negative'])
        ], style={'display': 'flex', 'justifyContent': 'space-between', 'marginBottom': '20px'}),

        html.Div ([
            html.H2 ('Sentiment Word Clouds', style={'color': COLORS ['text'], 'marginBottom': '20px'}),
            html.Div ([
                html.Div ([
                    html.H3 ('Positive Sentiment', style={'color': COLORS ['positive']}),
                    html.Img (src=positive_wordcloud, style={'width': '100%'})
                ], style={'width': '48%'}),
                html.Div ([
                    html.H3 ('Negative Sentiment', style={'color': COLORS ['negative']}),
                    html.Img (src=negative_wordcloud, style={'width': '100%'})
                ], style={'width': '48%'})
            ], style={'display': 'flex', 'justifyContent': 'space-between'})
        ], className='dashboard-card'),


        html.Div ([
            html.Div ([
                dcc.Graph (figure=sentiment_fig)
            ], className='dashboard-card', style={'width': '48%'}),

            html.Div ([
                dcc.Graph (figure=topics_fig)
            ], className='dashboard-card', style={'width': '48%'})
        ], style={'display': 'flex', 'justifyContent': 'space-between', 'marginTop': '20px'})

    ], style={'maxWidth': '1200px', 'margin': '0 auto', 'padding': '0 20px'})

], style={'backgroundColor': COLORS ['background'], 'minHeight': '100vh', 'padding': '20px'})

app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>Data Engineering Dashboard</title>
        {%favicon%}
        {%css%}
        <style>
            body {
                margin: 0;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
            }
            .stat-card {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
                width: 30%;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .dashboard-card {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                margin-bottom: 20px;
            }
            @media (max-width: 768px) {
                .stat-card {
                    width: 100%;
                    margin-bottom: 10px;
                }
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

if __name__ == '__main__':
    app.run_server (debug=True)
