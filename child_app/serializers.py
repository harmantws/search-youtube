from rest_framework import serializers

class SearchQuerySerializer(serializers.Serializer):
    query = serializers.CharField(required=True)
    age = serializers.IntegerField(required=True)
    language = serializers.ChoiceField(choices=['English', 'Hindi', 'Punjabi'], required=True)
    mode = serializers.ChoiceField(choices=['strict', 'moderate'], required=True)
