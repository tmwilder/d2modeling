import requests
import bs4
import re
import datetime

from d2modeling.schema import BetMatch
from d2modeling import SessionFactory


class Dota2LoungeClient:
    def get_main_page(self):
        url = "http://dota2lounge.com/"
        response = requests.get(url)
        response.raise_for_status()
        return response.content


def extract_bets_page():
    page = Dota2LoungeClient().get_main_page()
    return page


def transform_bets_page(page_html):
    soup = bs4.BeautifulSoup(page_html)

    matches = soup.findAll("div", {"class": "matchmain"})
    
    team_regex = re.compile(r"^(.*?)(\d{1,2})%$")
    time_delta_regex = re.compile(r"(?:\r\n){0,1}\s*(\d+ [^\s]+ [^\s]+).*")

    parsed_matches = []

    for match in matches:

        teams = []

        team_data = match.findAll("div", {"class": "teamtext"})
        for team_html in team_data:
            team_name, odds = re.match(team_regex, team_html.text).groups()
            teams.append({"team_name": team_name, "odds": odds})

        match_data = match.findAll("div", {"class": "whenm"})
        time_delta_phrase = re.match(time_delta_regex, match_data[0].text).groups(0)[0]
        true_date_time = _get_true_date_time(time_delta_phrase)

        tournament_name = match.find("div", {"class": "eventm"}).text.strip("\r\n ")

        match_data = {
            "tournament": tournament_name,
            "team_1_name": teams[0]["team_name"],
            "team_1_odds": teams[0]["odds"],
            "team_2_name": teams[1]["team_name"],
            "team_2_odds": teams[1]["odds"],
            "date_time": true_date_time,
            "current_date_time": datetime.datetime.now()
        }

        parsed_matches.append(match_data)

    return parsed_matches


def _get_true_date_time(time_delta_phrase):
    time_number, time_unit, from_or_ago = re.match(
        r"^(\d+)\s+(seconds{0,1}|minutes{0,1}|hours{0,1}|days{0,1})\s+(from|ago).*",
        time_delta_phrase
    ).groups()
    time_number = int(time_number)

    now = datetime.datetime.now()

    if time_unit in ("second", "seconds"):
        delta = datetime.timedelta(seconds=time_number)
    elif time_unit in ("minute", "minutes"):
        delta = datetime.timedelta(minutes=time_number)
    elif time_unit in ("hour", "hours"):
        delta = datetime.timedelta(hours=time_number)
    elif time_unit in ("day", "days"):
        delta = datetime.timedelta(days=time_number)
    
    if from_or_ago == "from":
        # From case, match is yet to happen, i.e. match is x minutes from now.
        match_time = now + delta
    else:
        # Ago case, match already happened.
        match_time = now - delta

    return match_time


def load_bets_page(transformed_matches):
    session = SessionFactory()
    for count, match in enumerate(transformed_matches):
        load_match(session, match, count+1)
    session.close()


def load_match(session, match, count=None):
    if count is not None:
        message = "Adding bet_match #{} with data: {}".format(count, match)
    else:
        message = "Adding match with match id {}".format(match)
    print(message)

    match_obj = BetMatch(
        team_1_name=match["team_1_name"],
        team_2_name=match["team_2_name"],
        team_1_odds=match["team_1_odds"],
        team_2_odds=match["team_2_odds"],
        tournament=match["tournament"],
        date_time=match["date_time"],
        current_date_time=match["current_date_time"]
    )
    session.add(match_obj)
    session.commit()
