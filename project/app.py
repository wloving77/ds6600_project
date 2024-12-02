from dash import Dash, html, dcc, Input, Output
import json
from helpers import steam_api_helper

steam_api_helper = steam_api_helper.APIHelper()


def fetch_game_data(game_name):
    return steam_api_helper.searchSteamApps(game_name)


def fetch_user_data(user_name):
    return steam_api_helper.searchSteamDisplayNames(user_name)


# Initialize the Dash app
external_stylesheets = [
    "https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css"
]
app = Dash(__name__, external_stylesheets=external_stylesheets)

# App layout
app.layout = html.Div(
    [
        html.H1("Steam Dashboard", style={"textAlign": "center"}),
        html.Div(
            [
                html.Label(
                    "Search for Games:",
                    style={
                        "margin-right": "10px",
                        "margin-left": "10px",
                        "margin-top": "20px",
                    },
                ),
                dcc.Input(
                    id="game-search-bar",
                    type="text",
                    placeholder="Enter game name...",
                    style={"width": "50%", "margin-bottom": "20px"},
                ),
                html.Button("Search", id="game-search-button", n_clicks=0),
                html.Div(
                    id="game-result",
                    style={
                        "margin-top": "20px",
                        "display": "flex",
                        "flex-wrap": "wrap",
                    },
                ),
            ],
            style={"margin-bottom": "40px"},
        ),
        html.Div(
            [
                html.Label(
                    "Search for Users:",
                    style={
                        "margin-right": "10px",
                        "margin-left": "10px",
                        "margin-top": "20px",
                    },
                ),
                dcc.Input(
                    id="user-search-bar",
                    type="text",
                    placeholder="Enter username...",
                    style={"width": "50%", "margin-bottom": "20px"},
                ),
                html.Button("Search", id="user-search-button", n_clicks=0),
                html.Div(id="user-result", style={"margin-top": "20px"}),
            ]
        ),
    ]
)


# Callback for game search
@app.callback(
    Output("game-result", "children"),
    Input("game-search-button", "n_clicks"),
    Input("game-search-bar", "value"),
)
def search_game(n_clicks, game_name):
    if n_clicks > 0 and game_name:
        games_data = fetch_game_data(game_name)
        if isinstance(games_data, list) and games_data:  # Ensure it's a non-empty list
            return [
                html.Div(
                    [
                        # Game Image
                        html.Img(
                            src=game.get("tiny_image", ""),
                            style={"width": "150px", "margin-right": "10px"},
                        ),
                        html.Div(
                            [
                                # Game Name
                                html.H4(game.get("name", "Unknown Name")),
                                # Game ID
                                html.P(f"ID: {game.get('id', 'N/A')}"),
                                # Price
                                html.P(
                                    f"Price: {game.get('price', {}).get('final', 0) / 100:.2f} "
                                    f"{game.get('price', {}).get('currency', 'N/A')}"
                                    if "price" in game
                                    else "Price: Not available"
                                ),
                                # Metascore
                                html.P(f"Metascore: {game.get('metascore', 'N/A')}"),
                                # Platforms
                                html.P(
                                    f"Platforms: {', '.join([k for k, v in game.get('platforms', {}).items() if v]) or 'None'}"
                                ),
                                # Controller Support
                                html.P(
                                    f"Controller Support: {game.get('controller_support', 'None')}"
                                ),
                            ],
                            style={"max-width": "300px"},
                        ),
                    ],
                    style={
                        "display": "flex",
                        "flex-direction": "row",
                        "align-items": "center",
                        "border": "1px solid #ddd",
                        "padding": "10px",
                        "margin": "10px",
                        "border-radius": "5px",
                        "box-shadow": "2px 2px 5px rgba(0, 0, 0, 0.1)",
                    },
                )
                for game in games_data
            ]
        else:
            return html.Div(
                "No results found or invalid response.", style={"margin-left": "20px"}
            )
    return html.Div(
        "Enter a game name and click search.", style={"margin-left": "20px"}
    )


# Callback for user search
@app.callback(
    Output("user-result", "children"),
    Input("user-search-button", "n_clicks"),
    Input("user-search-bar", "value"),
)
def search_user(n_clicks, user_name):
    if n_clicks > 0 and user_name:
        user_data = fetch_user_data(user_name)
        if isinstance(user_data, list) and user_data:  # Ensure it's a non-empty list
            return html.Div(
                [
                    html.Div(
                        [
                            # User Display Name
                            html.H4(user.get("display_name", "Unknown User")),
                            # Profile URL
                            html.A(
                                "Profile Link",
                                href=user.get("profile_url", "#"),
                                target="_blank",
                                style={"color": "blue", "text-decoration": "underline"},
                            ),
                        ],
                        style={
                            "border": "1px solid #ddd",
                            "padding": "10px",
                            "margin": "10px",
                            "border-radius": "5px",
                            "box-shadow": "2px 2px 5px rgba(0, 0, 0, 0.1)",
                            "max-width": "300px",
                        },
                    )
                    for user in user_data
                ],
                style={
                    "display": "flex",
                    "flex-wrap": "wrap",
                    "margin-top": "20px",
                },
            )
        else:
            return html.Div(
                "No results found or invalid response.", style={"margin-left": "20px"}
            )
    return html.Div("Enter a username and click search.", style={"margin-left": "20px"})


# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
