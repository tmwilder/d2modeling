from d2modeling.match_etl import extract_matches, transform_matches, load_matches
import d2modeling.elo

load_matches(transform_matches(extract_matches(2500)))
print("Updating match elos...")
d2modeling.elo.update_all()
