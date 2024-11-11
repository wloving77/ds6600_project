import json
import requests
import pandas as pd
import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time


class APIHelper:

    def __init__(self):
        load_dotenv()
        self.steam_key = os.getenv("STEAM_API_KEY")

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

    def getGamePlayerCount(self, game_title):
        try:
            game_data = self.search_steam_game(game_title)

            if not game_data or "id" not in game_data[0]:
                return f"Game '{game_title}' not found or could not retrieve app ID."

            app_id = game_data[0]["id"]

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
        try:
            game_data = self.search_steam_game(game_title)

            if not game_data or "id" not in game_data[0]:
                return f"Game '{game_title}' not found or could not retrieve app ID."

            app_id = game_data[0]["id"]

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

    def getUserAchievementStats(self, user_id, game_title):
        try:
            game_data = self.search_steam_game(game_title)

            if not game_data or "id" not in game_data[0]:
                return f"Game '{game_title}' not found or could not retrieve app ID."

            app_id = game_data[0]["id"]

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

            playtime_url = f"https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/?key={self.steam_key}&steamid={user_id}&include_appinfo=1"
            playtime_response = requests.get(playtime_url)

            # Attempt to parse playtime data
            try:
                playtime_data = playtime_response.json()
            except ValueError:
                return f"Error: Received non-JSON response from the playtime API for '{game_title}'"

            # Locate the game in owned games data
            playtime = None
            if "response" in playtime_data and "games" in playtime_data["response"]:
                for game in playtime_data["response"]["games"]:
                    if game["appid"] == app_id:
                        playtime = game.get(
                            "playtime_forever", 0
                        )  # Playtime in minutes
                        break

            # Assemble the result with game stats and playtime
            return {
                "game_title": game_title,
                "app_id": app_id,
                "player_stats": player_stats,
                "playtime_minutes": (
                    playtime if playtime is not None else "Playtime data unavailable"
                ),
            }

        except requests.exceptions.RequestException as e:
            return f"Error fetching stats for '{game_title}': {e}"

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

    def searchSteamDisplayNames(self, display_name):
        search_url = f"https://steamcommunity.com/search/users/#text={display_name}"

        options = webdriver.ChromeOptions()
        options.add_argument("--headless")

        # Initialize WebDriver with the ChromeDriver path in WSL
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

            # Ensure both profile name and link exist
            if profile_name_tag and profile_name_tag.text and profile_name_tag["href"]:
                profile_name = profile_name_tag.text.strip()
                profile_url = profile_name_tag["href"].strip()

                # Add profile details to results list
                results.append(
                    {"display_name": profile_name, "profile_url": profile_url}
                )

        driver.quit()

        # Return the list of results
        return (
            results
            if results
            else f"No profiles found for display name '{display_name}'"
        )

    def getUserAgent(self):
        url = "https://httpbin.org/user-agent"
        r = requests.get(url)
        useragent = json.loads(r.text)["user-agent"]
        return useragent

    def makeHeaders(self, email="wloving77@virginia.edu"):
        useragent = self.get_useragent()
        headers = {"User-Agent": useragent, "From": email}
        return headers
