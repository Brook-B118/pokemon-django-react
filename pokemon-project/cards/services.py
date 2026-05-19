import requests

def get_cards(query_params):
    tcgdex_params = {}

    if 'name' in query_params:
        tcgdex_params['name'] = query_params['name']

    if 'rarity' in query_params:
        tcgdex_params['rarity'] = query_params['rarity']

    if 'type' in query_params:
        tcgdex_params['types'] = query_params['type'].replace(',', '|')

    if 'page' in query_params:
        tcgdex_params['pagination:page'] = query_params['page']
        tcgdex_params['pagination:itemsPerPage'] = 20

    response = requests.get(
        "https://api.tcgdex.net/v2/en/cards",
        params=tcgdex_params,
        timeout=10
    )

    response.raise_for_status()
    return response.json()