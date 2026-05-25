import requests
from django.core.cache import cache

def get_cards(query_params):
    tcgdex_params = {}

    if 'name' in query_params:
        tcgdex_params['name'] = query_params['name']

    if 'rarity' in query_params:
        tcgdex_params['rarity'] = query_params['rarity']

    if 'type' in query_params:
        tcgdex_params['types'] = query_params['type'].replace(',', '|')

    if 'set' in query_params:
        tcgdex_params['set'] = query_params['set']

    if 'page' in query_params:
        tcgdex_params['pagination:page'] = query_params['page']
        tcgdex_params['pagination:itemsPerPage'] = 20

    query_list = []
    for k, v in tcgdex_params.items():
        query_list.append(f"{k}={v}")
    query_string = "&".join(query_list)

    cache_key = f"cards:{query_string}"

    try:
        cached_results = cache.get(cache_key)
        if cached_results is not None:
            return cached_results
    except Exception:
        pass  # potential redis server issue? Fall through to TCGdex

    response = requests.get(
        "https://api.tcgdex.net/v2/en/cards",
        params=tcgdex_params,
        timeout=10
    )
    
    response.raise_for_status()

    try:
        cache.set(cache_key, response.json(), timeout=86400) # Redis SET is extremeley fast, don't need to make this async.
    except Exception:
        pass  # Redis is down, response still returns fine

    return response.json()