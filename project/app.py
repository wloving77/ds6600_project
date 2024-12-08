from dash import Dash, html, dcc, Input, Output
from helpers import steam_api_helper
import pandas as pd

steam_api_helper = steam_api_helper.APIHelper()


def fetch_game_data(game_name):
    return steam_api_helper.searchSteamApps(game_name)


def fetch_user_data(user_name):
    return steam_api_helper.searchSteamDisplayNames(user_name)


def fetch_game_news(game_name):
    return steam_api_helper.getGameNews(game_name)


def fetch_achievement_data(game_name):
    return steam_api_helper.getGameAchievementData(game_name)


# Initialize the Dash app
external_stylesheets = [
    "https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css"
]
app = Dash(__name__, external_stylesheets=external_stylesheets)

# App layout
app.layout = html.Div(
    [
        html.H1("Steam Dashboard", style={"textAlign": "center"}),
        # Parent Div for All Search Sections
        html.Div(
            [
                # Game Search Section
                html.Div(
                    [
                        html.Label(
                            "Search for Games:", style={"margin-bottom": "10px"}
                        ),
                        dcc.Input(
                            id="game-search-bar",
                            type="text",
                            placeholder="Enter game name...",
                            style={"width": "60%", "margin-right": "10px"},
                        ),
                        html.Button("Search", id="game-search-button", n_clicks=0),
                        html.Div(id="game-result", style={"margin-top": "10px"}),
                    ],
                    style={"margin-bottom": "20px"},
                ),
                # Game News Section
                html.Div(
                    [
                        html.Label(
                            "Search for Game News:", style={"margin-bottom": "10px"}
                        ),
                        dcc.Input(
                            id="game-news-search-bar",
                            type="text",
                            placeholder="Enter game name...",
                            style={"width": "60%", "margin-right": "10px"},
                        ),
                        html.Button("Search News", id="game-news-button", n_clicks=0),
                        html.Div(id="game-news-result", style={"margin-top": "10px"}),
                    ],
                    style={"margin-bottom": "20px"},
                ),
                # Achievement Data Section
                html.Div(
                    [
                        html.Label(
                            "Search for Game Achievements:",
                            style={"margin-bottom": "10px"},
                        ),
                        dcc.Input(
                            id="achievement-search-bar",
                            type="text",
                            placeholder="Enter game name...",
                            style={"width": "60%", "margin-right": "10px"},
                        ),
                        html.Button(
                            "Search Achievements", id="achievement-button", n_clicks=0
                        ),
                        html.Div(id="achievement-result", style={"margin-top": "10px"}),
                    ],
                    style={"margin-bottom": "20px"},
                ),
                # User Search Section
                html.Div(
                    [
                        html.Label(
                            "Search for Users:", style={"margin-bottom": "10px"}
                        ),
                        dcc.Input(
                            id="user-search-bar",
                            type="text",
                            placeholder="Enter username...",
                            style={"width": "60%", "margin-right": "10px"},
                        ),
                        html.Button(
                            "Search Users", id="user-search-button", n_clicks=0
                        ),
                        html.Div(id="user-result", style={"margin-top": "10px"}),
                    ],
                    style={"margin-bottom": "20px"},
                ),
            ],
            style={
                "max-width": "2000px",
                "margin": "0 auto",
                "padding": "20px",
                "border": "1px solid #ddd",
                "border-radius": "8px",
                "box-shadow": "0px 4px 6px rgba(0, 0, 0, 0.1)",
                "background-color": "#f9f9f9",
            },
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
                            style={
                                "width": "150px",
                                "height": "auto",
                                "margin-right": "10px",
                                "border-radius": "5px",
                            },
                        ),
                        html.Div(
                            [
                                # Game Name
                                html.H4(game.get("name", "Unknown Name")),
                                # Game ID
                                html.P(f"ID: {game.get('id', 'N/A')}"),
                                # Price
                                html.P(
                                    f"Price: ${game['price']['final'] / 100:.2f} "
                                    f"{game['price'].get('currency', 'N/A')}"
                                    if "price" in game and game["price"]
                                    else "Price: Not available"
                                ),
                                # Metascore
                                html.P(f"Metascore: {game.get('metascore', 'N/A')}"),
                                # Platforms
                                html.P(
                                    f"Platforms: {', '.join([k.capitalize() for k, v in game.get('platforms', {}).items() if v]) or 'None'}"
                                ),
                                # Controller Support
                                html.P(
                                    f"Controller Support: {game.get('controller_support', 'None')}"
                                ),
                            ],
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
            return "No results found or invalid response."
    return "Enter a game name and click search."


# Callback for user search
@app.callback(
    Output("user-result", "children"),
    Input("user-search-button", "n_clicks"),
    Input("user-search-bar", "value"),
)
def search_user(n_clicks, user_name):
    if n_clicks > 0 and user_name:
        user_data = fetch_user_data(user_name)
        if isinstance(user_data, list) and user_data:
            return [
                html.Div(
                    [
                        html.H4(user.get("display_name", "Unknown User")),
                        html.A(
                            "Profile Link",
                            href=user.get("profile_url", "#"),
                            target="_blank",
                            style={"color": "blue"},
                        ),
                    ],
                    style={
                        "border": "1px solid #ddd",
                        "padding": "10px",
                        "margin": "10px",
                    },
                )
                for user in user_data
            ]
        else:
            return "No results found or invalid response."
    return "Enter a username and click search."


# Callback for game news search
# Callback for game news search
@app.callback(
    Output("game-news-result", "children"),
    Input("game-news-button", "n_clicks"),
    Input("game-news-search-bar", "value"),
)
def search_game_news(n_clicks, game_name):
    if n_clicks > 0 and game_name:
        news_data = fetch_game_news(game_name)
        if isinstance(news_data, dict) and "news" in news_data:
            return [
                html.Div(
                    [
                        # News Title
                        html.H4(item["title"], style={"margin-bottom": "5px"}),
                        # Link to Full Article
                        html.A(
                            "Read More",
                            href=item["url"],
                            target="_blank",
                            style={"color": "blue", "text-decoration": "underline"},
                        ),
                        # Date
                        html.P(
                            f"Published on: {pd.to_datetime(item['date'], unit='s').strftime('%Y-%m-%d')}",
                            style={"font-style": "italic", "margin-top": "5px"},
                        ),
                    ],
                    style={
                        "border": "1px solid #ddd",
                        "padding": "10px",
                        "margin": "10px",
                        "border-radius": "5px",
                        "box-shadow": "2px 2px 5px rgba(0, 0, 0, 0.1)",
                    },
                )
                for item in news_data["news"]
            ]
        else:
            return f"No news found for '{game_name}'."
    return "Enter game details and click search."


# Callback for achievement data search
@app.callback(
    Output("achievement-result", "children"),
    Input("achievement-button", "n_clicks"),
    Input("achievement-search-bar", "value"),
)
def search_achievements(n_clicks, game_name):
    if n_clicks > 0 and game_name:
        achievement_data = fetch_achievement_data(game_name)
        if isinstance(achievement_data, dict) and "achievements" in achievement_data:
            return [
                html.Div(
                    [
                        html.H4(achievement["name"]),
                        html.P(f"Percent Unlocked: {achievement['percent']}%"),
                    ],
                    style={
                        "border": "1px solid #ddd",
                        "padding": "10px",
                        "margin": "10px",
                    },
                )
                for achievement in achievement_data["achievements"]
            ]
        else:
            return f"No achievements found for '{game_name}'."
    return "Enter game details and click search."


# Run the app
if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8050)
