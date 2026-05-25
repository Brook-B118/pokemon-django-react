from rest_framework import serializers

class CardSearchSerializer(serializers.Serializer):
    name = serializers.CharField(required=False)
    type = serializers.CharField(required=False)
    rarity = serializers.CharField(required=False)
    set = serializers.CharField(required=False)
    page = serializers.IntegerField(required=True, min_value=1)
    page_size = serializers.IntegerField(required=False, default=20, min_value=1, max_value=100)