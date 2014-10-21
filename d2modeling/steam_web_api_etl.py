import requests
import json
import copy
import os

from d2modeling.schema import Team, Match
from d2modeling import SessionFactory
from d2modeling import get_dbapi2_conn
from sqlalchemy.exc import IntegrityError


class SteamApiClient:
    def _get_api_url(self, path, base_url="https://api.steampowered.com/IDOTA2Match_570/", api_version="/V001"):
        return base_url + path + api_version

    def _get_key(self):
        key = os.environ.get("STEAM_KEY")
        if key is None:
            raise(ValueError("You must set the STEAM_KEY env variable."))
        return key

    def _get_params(self, params):
        new_params = copy.deepcopy(params)
        new_params.update({"key": self._get_key()})
        return new_params

    def get_match_details(self, match_id):
        url = self._get_api_url("GetMatchDetails")
        params = self._get_params({"match_id": match_id})
        r = requests.get(url, params=params)
        r.raise_for_status()
        return json.loads(r.content), r.status_code

    def get_league_listing(self):
        url = self._get_api_url("GetLeagueListing")
        params = self._get_params({})
        r = requests.get(url, params=params)
        r.raise_for_status()
        return json.loads(r.content), r.status_code


def extract_match_details():
    client = SteamApiClient()
    conn = get_dbapi2_conn()
    cursor = conn.cursor()
    match_ids = cursor.execute("select id from match")
    results = cursor.fetchall()
    conn.close()
    if  results is None:
        return []
    else:
        print("Fetching {} match details from Steam Web API...".format(len(results)))
        details = []
        for index, match_id in enumerate(results):
            print("Retrieving from Steam API result #: {} match_id: {}".format(index + 1, match_id[0]))
            detail = client.get_match_details(match_id)
            details.append(detail)
        return details


def transform_match_details(raw_match_data):
    return [match_data[0]["result"] for match_data in raw_match_data]


def load_match_details(transformed_matches):
    print("Loading {} matches into DB...".format(len(transformed_matches)))
    conn = get_dbapi2_conn()
    cursor = conn.cursor()
    for index, match_data in enumerate(transformed_matches):
        print("Updating match #: {} with match_id: {}".format(index + 1, match_data["match_id"]))
        sql = "update match set match_data = ? where id = ?"
        data = (json.dumps(match_data), match_data["match_id"])
        cursor.execute(sql, data)
    conn.commit()
    conn.close()
