from rest_framework.throttling import UserRateThrottle, AnonRateThrottle

class AnonCardSearchRateThrottle(AnonRateThrottle):
    scope = 'anon_search_cards'


class UserCardSearchRateThrottle(UserRateThrottle):
    scope = 'user_search_cards'