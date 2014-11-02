from d2modeling.match_etl import extract_matches, transform_matches, load_matches
from d2modeling.steam_web_api_etl import extract_match_details, transform_match_details, load_match_details
import d2modeling.elo

load_matches(transform_matches(extract_matches(2500)))
print("Getting match detail data...")

print("Updating match elos...")
d2modeling.elo.update_all()
print("Match elos updated.")
load_match_details(transform_match_details(extract_match_details()))
