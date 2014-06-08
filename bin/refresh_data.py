from d2modeling.match_etl import extract_matches, transform_matches, load_matches

load_matches(transform_matches(extract_matches(2500)))