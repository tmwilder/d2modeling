import datetime
import requests
import bs4

import insert_data


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

    _format_fields(results)

    return results


def _format_fields(results):
    for datum in results:
        score = datum.pop("score")
        radiant_score, dire_score = [int(team_score.strip()) for team_score in score.split("-")]
        datum[u"radiant_score"] = radiant_score
        datum[u"dire_score"] = dire_score

        datum["date"] = datetime.datetime.strptime(datum["date"], "%m/%d/%y")


def save_results(results):
    session = insert_data.get_session()
    for result in results:
        insert_data.insert_match(session, result)


def get_past_matches(how_many_500_matches):
    results = []
    for n in range(how_many_500_matches):
        data_page = _get_past_matches_page(500*n)
        data = _parse_results_from_past_matches(data_page.text)
        results.extend(data)
    return results


if __name__ == "__main__":
    past_matches = get_past_matches(1)
    save_results(past_matches)
