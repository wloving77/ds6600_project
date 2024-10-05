import json
import requests
import pandas as pd
import os


class APIHelper:

    def __init__(self):
        self.steam_key = os.getenv("STEAM_API_KEY")

    def get_useragent(self):
        url = "https://httpbin.org/user-agent"
        r = requests.get(url)
        useragent = json.loads(r.text)['user-agent']
        return useragent
        
    def make_headers(self, email='wloving77@virginia.edu'):
        useragent = self.get_useragent()
        headers = {
            'User-Agent': useragent, 
            'From': email
        }
        return headers


    def getGameUserStatistics(self, gameid, steamid, apikey):
        return -1
    
    def getGlobalGameStatistics(self, gameid)
        return -1
    
    def getGlobalGameAchievements(self, gameid):
        endpoint = "https://api.steampowered.com/ISteamUserStats/GetGlobalAchievementPercentagesForApp/v2/"
        headers = self.make_headers()
        params = {"gameid": gameid}
        r = requests.get(endpoint, headers=headers, params=params)

        if r.status_code == 200:
            return r.json()
        else: 
            return f"Error Getting Game Statistics"

