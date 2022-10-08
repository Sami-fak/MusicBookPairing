import requests
from dash import Dash, html, dcc, dependencies
import dash_bootstrap_components as dbc
import spotipy as spotipy
from spotipy.oauth2 import SpotifyOAuth
from pprint import pprint
from time import sleep
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "backend_api/key.json"

APIKEY="AIzaSyDVOS-1dHYqBAmAIimDFtXpxR-E6k7_ccM"

#####################
# SPOTIFY CONNECTION
#####################

CLIENT_ID = "a08742993525464baccf9c36dd7d5b94"
with open("key.txt", "r") as f:
    CLIENT_SECRET = f.readline().strip()


AUTH_URL = "https://accounts.spotify.com/api/token"
auth_response = requests.post(AUTH_URL, {
    'grant_type': 'client_credentials',
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET,
})

#Convert response to JSON
auth_response_data = auth_response.json()

#Save the access token
access_token = auth_response_data['access_token']

#Need to pass access token into header to send properly formed GET request to API server
headers = {
    'Authorization': 'Bearer {token}'.format(token=access_token)
}

theme = dbc.themes.QUARTZ
css = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css'

app = Dash(__name__, external_stylesheets=[theme, css])
server = app.server

app.layout = html.Div([
    html.Header([
        dbc.Row([
            dbc.Col([
                html.H1("Music & books pairing tool."),
                html.H4("Listen to the right music while reading"),
            ], className="col-lg-10 col-md-10 col-sm-10 col-xs-12" ),
        ]), 
    ]),

    html.Section([
        dbc.Row([
            dbc.Input(id="input", placeholder="What book are you reading today?", type="text"),
        ], className='row mb-3'),
        dbc.Row([
            dbc.Col([
                html.P(id="output"),
            ]),
            dbc.Col([
                html.P(id="spotify-output"),
            ])
        ], className="col-lg-12 col-md-12 col-sm-12 col-xs-12"),
    ], className='justify-content-center'),
], className='container')

@app.callback(
    dependencies.Output('output', 'children'), 
    dependencies.Input('input', 'value')
)
def get_google_book_data(value):
    # use requests library to send HTTP requests
    # in this example, GET sentiment analysis data
    print("value = ",value)
    if value:
        url = f"https://www.googleapis.com/books/v1/volumes?q={value}&key={APIKEY}"
        res = requests.get(url)
        data = res.json()
        print(data)
        items = data['items']
        cards = []
        for i,item in enumerate(items[:1]):
            info = item['volumeInfo']
            authors = ', '.join(info['authors'])
            title = info['title']
            if "categories" in info.keys():
                categories = ' '.join(info['categories'])
            else:
                categories = title
            if "imageLinks" in info.keys():
                thumbnail = info['imageLinks']['thumbnail']
            else:
                thumbnail = "https://upload.wikimedia.org/wikipedia/commons/5/5a/No_image_available_500_x_500.svg"

            card = dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.A([  
                                html.H2(title),
                                html.H4(authors),
                                html.Img(src=thumbnail, width=128, height=206),
                            ], id=f"card-{i}", href="#", n_clicks=0, rel=categories),
                            html.P(f"Categories : {categories}"),
                        ])
                    ])
                ])
            ])
            cards.append(card)
    return cards[0]

@app.callback(
    dependencies.Output('spotify-output', 'children'), 
    [dependencies.Input('card-0', 'n_clicks'), dependencies.Input('card-0', 'rel')]
)
def get_spotify_data(n_clicks, rel):
    # use requests library to send HTTP requests
    # in this example, GET sentiment analysis data
    if n_clicks>0:
        BASE_URL = 'https://api.spotify.com/v1/'
        res = requests.get(BASE_URL + f'search?q={rel}&type=playlist', headers=headers)
        data = res.json()
        items = data['playlists']['items']
        cards = []
        for i, item in enumerate(items):
            description = item['description']
            name = item['name']
            image = item['images'][0]['url']
            url = item['external_urls']['spotify']
            card = dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.H2(name),
                            html.A([
                                html.Img(src=image, width=128, height=128, className="mx-auto d-block"),
                            ], href=url, target="_blank"),
                            html.P(f"Description : {description}"),
                        ])
                    ])
                ])
            ])
            cards.append(card)

        print(cards)
        return cards[0]

if __name__=='__main__':
    server.run(debug=True,port=8050)