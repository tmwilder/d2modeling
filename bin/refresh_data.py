from d2modeling.match_etl import extract_matches, transform_matches, load_matches
from d2modeling.steam_web_api_etl import extract_match_details, transform_match_details, load_match_details
from d2modeling.dota2_lounge_etl import extract_bets_page, transform_bets_page, load_bets_page
import d2modeling.elo

print("Loading pro match data from datdota.com...")
load_matches(transform_matches(extract_matches(2500)))
print("Loaded pro match data!")

print("Updating match elos...")
d2modeling.elo.update_all()
print("Match elos updated!")

print("Getting match detail data...")
load_match_details(transform_match_details(extract_match_details()))
print("Got match detail data!")

print("Getting bets information...")
load_bets_page(transform_bets_page(extract_bets_page()))
print("Got bets information!")
