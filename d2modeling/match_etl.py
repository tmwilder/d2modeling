import datetime
import requests
import bs4
from d2modeling.schema import Team, Match
from d2modeling import SessionFactory
from sqlalchemy.exc import IntegrityError

def extract_matches(num_matches_to_read):
    results = []
    while len(results) < num_matches_to_read:
        data_page = _read_match_html(len(results))
        data = _extract_match_data(data_page.text)
        results.extend(data)
    return results

def _read_match_html(records_back):
    params = {"l0": records_back}
    url = "http://www.datdota.com/matches.php"
    res = requests.get(url, params=params)
    return res

def _extract_match_data(match_page_html):
    doc = bs4.BeautifulSoup(match_page_html)
    table = doc.find_all("table")[0]
    rows = table.find_all("tr")
    parsed_headers = [header.text.lower() for header in rows[0]]

    results = []
    for row in rows[1:]:
        data = row.find_all("td")
        parsed_data = [datum.text for datum in data]
        formatted_data = dict(zip(parsed_headers, parsed_data))
        results.append(formatted_data)
    return results

def transform_matches(raw_match_data):
    for datum in raw_match_data:
        score = datum.pop("score")
        radiant_score, dire_score = [int(team_score.strip()) for team_score in score.split("-")]
        datum["radiant_score"] = radiant_score
        datum["dire_score"] = dire_score
        datum["match"] = int(datum["match"])
        datum["time"] = float(datum["time"])
        datum["date"] = datetime.datetime.strptime(datum["date"], "%m/%d/%y")
    return raw_match_data

def load_matches(transformed_matches):
    session = SessionFactory()
    for match in transformed_matches:
        load_match(session, match)
    session.close()

def load_match(session, match):
    try:
        session.add(Team(name=match['radiant']))
        session.commit()
    except IntegrityError:
        session.rollback()

    try:
        session.add(Team(name=match['dire']))
        session.commit()
    except IntegrityError:
        session.rollback()

    try:
        match_obj = Match(
            id=match['match'],
            dire_score=match['dire_score'],
            radiant_score=match['radiant_score'],
            time=match['time'],
            date=match['date'],
            winner=match['winner'],
            dire_name=match['dire'],
            radiant_name=match['radiant']
        )
        session.add(match_obj)
        session.commit()
    except IntegrityError:
        session.rollback()
