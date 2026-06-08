import requests
from django.core.cache import cache
from .models import Favorite
from django.db import transaction

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



@transaction.atomic
def add_favorite(user, card_data):
    # card data is going to be a dictionary
    # get_or_create returns (object, boolean), boolean is True if object was created (new) and False if it already existed (got)
    # Tuple unpack to determine if resource created or resorce exists in view status code
    # defaults is where we put fields that should only be set on creation
    # fields outside of defaults are used for the lookup
    raw_image = card_data.get('card_image', '')
    card_image_quality = "high" # options: high (600x825) or low (245x337)
    card_image_extension = "webp" # options: png, jpg, webp (recommended)
    _, created = Favorite.objects.get_or_create(
    user=user,
    card_id=card_data['card_id'],
    defaults={
        'card_name': card_data['card_name'],
        'card_image': f"{raw_image}/{card_image_quality}.{card_image_extension}" if raw_image else '',
        'card_rarity': card_data.get('card_rarity', ''),
        'card_types': card_data.get('card_types', ''),
        'card_set_id': card_data['card_set_id'],
        'card_set_name': card_data['card_set_name']
        }
    )   
    return created

@transaction.atomic
def delete_favorite(user, card_data):

    favorite = Favorite.objects.filter(user=user, card_id=card_data['card_id']).first()

    if favorite:
        favorite.delete()
        return True
    else:
        return False

    