from .models import Favorite

def get_user_favorites(user):
    # Don't return user, not needed for frontend.
    return Favorite.objects.filter(user=user).values('card_id', 'card_name', 'card_image', 'card_rarity', 'card_types', 'card_set_id', 'card_set_name')


def get_favorited_card_ids(user, searched_card_ids):
    return Favorite.objects.filter(
        user=user, 
        card_id__in=searched_card_ids
    ).values_list('card_id', flat=True)