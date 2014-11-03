from d2modeling.dota2_lounge_etl import load_bets_page, transform_bets_page, extract_bets_page


load_bets_page(transform_bets_page(extract_bets_page()))
