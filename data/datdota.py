import requests
import bs4
import pdb

def _get_past_matches_page(records_back=0):
    params = {"l0": records_back}
    url = "http://www.datdota.com/matches.php"
    res = requests.get(url, params=params)
    return res


def _parse_results_from_past_matches(text):
    doc = bs4.BeautifulSoup(text)
    table = doc.find_all("table")[0]

    rows = table.find_all("tr")

    parsed_headers = [header.text.lower() for header in rows[0]]

    results = []

    for row in rows[1:]:
        data = row.find_all("td")
        parsed_data = [datum.text for datum in data]

        formatted_data = dict(zip(parsed_headers, parsed_data))

        results.append(formatted_data)

    _set_team_scores(results)

    return results


def _set_team_scores(results):
    for datum in results:
        score = datum.pop("score")
        radiant_score, dire_score = [int(team_score.strip()) for team_score in score.split("-")]
        datum[u"radiant_score"] = radiant_score
        datum[u"dire_score"] = dire_score


def save_data(data):
    pass


def _get_upcoming_matches_page():
    url = "http://www.datdota.com/upcoming_matches.php"
    res = requests.get(url=url)
    return res


def _parse_results_from_upcoming_matches(text):
    # TODO factor parsing methods into common class if we do one more of these.
    doc = bs4.BeautifulSoup(text)
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


def get_past_matches(how_many_500_matches):
    results = []
    for n in range(how_many_500_matches):
        data_page = _get_past_matches_page(500*n)
        data = _parse_results_from_past_matches(data_page.text)
        results.extend(data)
    pdb.set_trace()
    return results

def get_upcoming_matches():
    upcoming_page = _get_upcoming_matches_page()
    results = _parse_results_from_upcoming_matches(upcoming_page.text)
    return results


if __name__ == "__main__":
    past_matches = get_past_matches(1)
    save_data(past_matches)

    upcoming_matches = get_upcoming_matches()
    save_data(upcoming_matches)
