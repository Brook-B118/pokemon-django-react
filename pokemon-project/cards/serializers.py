from rest_framework import serializers

class CardSearchSerializer(serializers.Serializer):
    name = serializers.CharField(required=False)
    type = serializers.CharField(required=False)
    rarity = serializers.CharField(required=False)
    set = serializers.CharField(required=False)
    page = serializers.IntegerField(required=True, min_value=1)
    page_size = serializers.IntegerField(required=False, default=20, min_value=1, max_value=100)


class FavoriteCardSerializer(serializers.Serializer):
    card_id = serializers.CharField(required=True, max_length=64)
    card_name = serializers.CharField(required=True, max_length=128)
    card_image = serializers.CharField(required=False, max_length=256)
    card_rarity = serializers.CharField(required=False, max_length=64)
    card_types = serializers.CharField(required=False, max_length=128)
    card_set_id = serializers.CharField(required=True, max_length=64)
    card_set_name = serializers.CharField(required=True, max_length=128)


class FavoriteCardDeleteSerializer(serializers.Serializer):
    card_id = serializers.CharField(required=True, max_length=64)