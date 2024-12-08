import json
import platform
import requests
import pandas as pd
import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import re


class APIHelper:

    def __init__(self):
        load_dotenv()
        self.steam_key = os.getenv("STEAM_API_KEY")

    """ Functions for general steam searching, by game and for all games:"""

    def getAllSteamApps(self):
        url = "https://api.steampowered.com/ISteamApps/GetAppList/v2/"
        response = requests.get(url)
        data = response.json()
        return data["applist"]["apps"]

    def searchSteamApps(self, game_title):
        url = f"https://store.steampowered.com/api/storesearch/?term={game_title}&l=english&cc=us"
        response = requests.get(url)
        data = response.json()
        return data["items"]

    """ Functions to Gather data from Steam API About a Given Game: """

    def getGamePlayerCount(self, game_title):
        game = self.searchSteamApps(game_title)
        if not game:
            return f"Game '{game_title}' not found"
        app_id = game[0]["id"]
        try:
            player_count_url = f"https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?appid={app_id}"
            player_count_response = requests.get(player_count_url)
            player_count_data = player_count_response.json()

            if (
                "response" in player_count_data
                and "player_count" in player_count_data["response"]
            ):
                player_count = player_count_data["response"]["player_count"]
                return {
                    "game_title": game_title,
                    "app_id": app_id,
                    "current_player_count": player_count,
                }
            else:
                return f"Player count data unavailable for '{game_title}'"

        except requests.exceptions.RequestException as e:
            return f"Error fetching player count for '{game_title}': {e}"

    def getGameAchievementData(self, game_title):
        game = self.searchSteamApps(game_title)
        if not game:
            return f"Game '{game_title}' not found"
        app_id = game[0]["id"]
        try:
            achievement_url = f"https://api.steampowered.com/ISteamUserStats/GetGlobalAchievementPercentagesForApp/v2/?gameid={app_id}"
            achievement_response = requests.get(achievement_url)
            achievement_data = achievement_response.json()

            if "achievementpercentages" in achievement_data:
                achievements = achievement_data["achievementpercentages"][
                    "achievements"
                ]
                return {
                    "game_title": game_title,
                    "app_id": app_id,
                    "achievements": achievements,
                }
            else:
                return f"Achievement data unavailable for '{game_title}'"

        except requests.exceptions.RequestException as e:
            return f"Error fetching achievement data for '{game_title}': {e}"

    def getGameNews(self, game_title, count=5):
        game = self.searchSteamApps(game_title)
        if not game:
            return f"Game '{game_title}' not found"
        app_id = game[0]["id"]
        if not app_id:
            return f"Game '{game_title}' not found"
        try:
            news_url = f"https://api.steampowered.com/ISteamNews/GetNewsForApp/v2/?appid={app_id}&count={count}"
            response = requests.get(news_url)
            response.raise_for_status()  # Raise an exception for HTTP errors

            news_data = response.json()

            # Check if news data is available
            if "appnews" in news_data and "newsitems" in news_data["appnews"]:
                news_items = news_data["appnews"]["newsitems"]

                # Format the output with game title and news items
                formatted_news = {
                    "game_title": game_title,
                    "app_id": app_id,
                    "news": [
                        {
                            "title": item["title"],
                            "contents": item["contents"],
                            "url": item["url"],
                            "date": item["date"],
                        }
                        for item in news_items
                    ],
                }
                return formatted_news
            else:
                return f"No news found for game '{game_title}' with app_id '{app_id}'"

        except requests.exceptions.RequestException as e:
            return f"Error fetching news for game '{game_title}': {e}"

    """ Functions Requiring Authentication and User Information: """

    def getUserAchievementStats(self, user_id, app_id, game_title):
        try:
            stats_url = f"https://api.steampowered.com/ISteamUserStats/GetUserStatsForGame/v2/?appid={app_id}&key={self.steam_key}&steamid={user_id}"
            stats_response = requests.get(stats_url)

            try:
                stats_data = stats_response.json()
            except ValueError:
                return (
                    f"Error: Received non-JSON response from the API for '{game_title}'"
                )

            if (
                "playerstats" in stats_data
                and "achievements" in stats_data["playerstats"]
            ):
                achievements = stats_data["playerstats"]["achievements"]
                return {
                    "game_title": game_title,
                    "app_id": app_id,
                    "achievements": achievements,
                }
            else:
                return f"Achievement data unavailable for '{game_title}'"

        except requests.exceptions.RequestException as e:
            return f"Error fetching achievement data for '{game_title}': {e}"

    def getUserGameStats(self, user_id, app_id, game_title):
        try:
            stats_url = f"https://api.steampowered.com/ISteamUserStats/GetUserStatsForGame/v2/?appid={app_id}&key={self.steam_key}&steamid={user_id}"
            stats_response = requests.get(stats_url)

            # Attempt to parse JSON response
            try:
                stats_data = stats_response.json()
            except ValueError:
                return (
                    f"Error: Received non-JSON response from the API for '{game_title}'"
                )

            player_stats = (
                stats_data["playerstats"].get("stats", [])
                if "playerstats" in stats_data
                else []
            )

            # Assemble the result with game stats and playtime
            return {
                "game_title": game_title,
                "app_id": app_id,
                "player_stats": player_stats,
            }

        except requests.exceptions.RequestException as e:
            return f"Error fetching stats for '{game_title}': {e}"

    def getUserOwnedGames(self, user_id, include_playtime=True):
        # Steam API endpoint for owned games
        owned_games_url = (
            "https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/"
        )

        # Set up parameters
        params = {
            "key": self.steam_key,
            "steamid": user_id,
            "include_appinfo": 1,
            "include_played_free_games": 1,
            "include_free_sub": 1,
            "include_playtime_forever": 1,
        }

        try:
            response = requests.get(owned_games_url, params=params)
            response.raise_for_status()  # Raise an exception for HTTP errors

            games_data = response.json()

            # Check if games data is available
            if "response" in games_data and "games" in games_data["response"]:
                games_list = games_data["response"]["games"]
                return {
                    "user_id": user_id,
                    "owned_games": [
                        {
                            "app_id": game["appid"],
                            "name": game.get("name", "Unknown Game Name"),
                            "playtime_forever": game.get(
                                "playtime_forever", 0
                            ),  # in minutes
                            "playtime_2weeks": game.get(
                                "playtime_2weeks", 0
                            ),  # last 2 weeks in minutes, if available
                        }
                        for game in games_list
                    ],
                }
            else:
                return f"No games found for user with SteamID64 '{user_id}'"

        except requests.exceptions.RequestException as e:
            return f"Error fetching owned games for user '{user_id}': {e}"

    def getSteamIDFromVanity(self, vanity_name, api_key):

        url = f"https://api.steampowered.com/ISteamUser/ResolveVanityURL/v1/"
        params = {"key": api_key, "vanityurl": vanity_name}
        response = requests.get(url, params=params)
        data = response.json()

        # Check if the response was successful
        if "response" in data and data["response"]["success"] == 1:
            steamid64 = data["response"]["steamid"]
            return steamid64
        else:
            return f"Could not resolve vanity URL '{vanity_name}'. Error: {data['response'].get('message', 'Unknown error')}"

    """ Functions Requiring Selenium/Novel Solutions:"""

    def searchSteamDisplayNames(self, display_name):
        """This function searches for Steam profiles based on display name using Selenium and a custom ChromeDriver. This is necessary because
        the Steam API does not support searching by display name and uses javascript to hamper scraping ability.
        """
        search_url = f"https://steamcommunity.com/search/users/#text={display_name}"

        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")  # Bypass the sandbox for Chrome
        options.add_argument(
            "--disable-dev-shm-usage"
        )  # Prevent crashes due to shared memory issues
        options.add_argument(
            "--disable-gpu"
        )  # Disable GPU acceleration (optional but often helps)
        options.add_argument("--remote-debugging-port=9222")  # Enable remote debugging
        options.add_argument(
            "--disable-software-rasterizer"
        )  # Software rasterizer for headless environments
        options.add_argument("--disable-extensions")  # Disable extensions for stability

        current_os = platform.system()

        # Initialize WebDriver with the ChromeDriver path in WSL

        # if current_os == "Windows":
        #     driver = webdriver.Chrome(
        #         service=Service("/usr/bin/chromedriver"), options=options
        #     )
        # elif current_os == "Darwin":
        #     driver = webdriver.Chrome(
        #         service=Service("/opt/homebrew/bin/chromedriver"), options=options
        #     )

        driver = webdriver.Chrome(
            service=Service("/usr/bin/chromedriver"), options=options
        )

        driver.get(search_url)

        time.sleep(5)

        soup = BeautifulSoup(driver.page_source, "html.parser")

        # Extract profile details
        results = []
        for user in soup.find_all("div", class_="search_row"):
            profile_name_tag = user.find("a", class_="searchPersonaName")

            if profile_name_tag and profile_name_tag.text and profile_name_tag["href"]:
                profile_name = profile_name_tag.text.strip()
                profile_url = profile_name_tag["href"].strip()

                results.append(
                    {"display_name": profile_name, "profile_url": profile_url}
                )

        driver.quit()

        return (
            results
            if results
            else f"No profiles found for display name '{display_name}'"
        )

    """ Functions Wrapping Other Functions for Ease of Use and Efficiency:"""

    def extractSteamID(self, steam_url):
        potential_id = steam_url.split("id/")[1]
        if self.isVanityURL(steam_url):
            return self.getSteamIDFromVanity(potential_id, self.steam_key)
        else:
            return potential_id

    """ General Helper Functions: """

    def isVanityURL(sef, steam_url):

        # Pattern to check for a vanity URL
        vanity_pattern = r"^https://steamcommunity\.com/id/[\w-]+/?$"

        # Pattern to check for a standard SteamID64 URL
        steamid64_pattern = r"^https://steamcommunity\.com/profiles/\d{17}/?$"

        if re.match(vanity_pattern, steam_url):
            return True
        elif re.match(steamid64_pattern, steam_url):
            return False
        else:
            return "Invalid Steam profile URL format"
