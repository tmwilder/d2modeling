import requests
import bs4


def get_data_page(records_back=0):
    params = {"l0": records_back}
    url = 'http://www.datdota.com/matches.php'
    res = requests.get(url, params=params)
    return res


def parse_results_from_page(text):
    doc = bs4.BeautifulSoup(text)
    table = doc.find_all("table")[0]

    rows = table.find_all('tr')

    parsed_headers = [header.text.lower() for header in rows[0]]

    results = []

    for row in rows[1:]:
        data = row.find_all('td')
        parsed_data = [datum.text for datum in data]
        
        formatted_data = dict(zip(parsed_headers, parsed_data))


        results.append(formatted_data)

    set_team_scores(results)

    return results


def set_team_scores(results):
    for datum in results:
        score = datum.pop(u'score')
        radiant_score, dire_score = [int(team_score.strip()) for team_score in score.split('-')]
        datum[u'radiant_score'] = radiant_score
        datum[u'dire_score'] = dire_score


def save_data(data):
    pass


def main():
    result = []
    for n in range(5):
        data_page = get_data_page(500*n)
        data = parse_results_from_page(data_page.text)
        result.extend(data)
    save_data(result)


if __name__ == "__main__":
    main()
