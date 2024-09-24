from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
import requests
from .serializers import SearchQuerySerializer
from .utils import safe_search_model  # Ensure your safe_search_model function is imported

class SearchVideos(APIView):
    """
    API View to handle video search requests based on user queries.
    """

    def post(self, request):
        serializer = SearchQuerySerializer(data=request.data)
        if serializer.is_valid():
            query = serializer.validated_data['query'].lower()
            age = serializer.validated_data['age']
            # child_id = serializer.validated_data['child_id'] 
            language = serializer.validated_data['language'].lower()
            mode = serializer.validated_data['mode'].lower()

            # Evaluate the query for appropriateness using the AI model
            safe_search_result = safe_search_model(query, age)
            if safe_search_result == "Not Allowed":
                return Response(
                    {
                        "message": "You do not have permission to search for this query."
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            # Adjust query based on language
            if language == "english":
                query += " videos in english"
            elif language == "hindi":
                query += " videos in hindi"
            elif language == "punjabi":
                query += " videos in punjabi"

            # Adjust the query based on age
            if age < 4:
                query += " for toddlers"
            elif age < 10:
                query += " for children"
            elif age < 12:
                # query += " cartoons and educational videos"
                query += " for children"

            # Perform YouTube search
            search_results = self.search_youtube(query, language, mode)
            return Response(search_results, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def search_youtube(self, query: str, language: str, mode: str) -> dict:
        """Search for YouTube videos based on the provided query and parameters."""
        API_KEY = settings.YOUTUBE_API_KEY

        print("------------ API KEY:", API_KEY)
        print("------------ Query:", query)
        print("------------ Language:", language)
        print("------------ Safe Search Mode:", mode)

        # Normalize language input
        if language.lower() == "english":
            language = 'en'

        SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
        
        params = {
            "part": "snippet",
            "q": query,
            "key": API_KEY,
            "type": "video",
            "videoCaption": "any",
            "relevanceLanguage": language,
            "regionCode": "IN",
            "safeSearch": mode,
            "maxResults": 8,
        }

        # Print the full URL for debugging
        full_url = requests.Request('GET', SEARCH_URL, params=params).prepare().url
        print("Full URL:", full_url)
        
        try:
            response = requests.get(SEARCH_URL, params=params)
            response.raise_for_status()
            data = response.json()

            # Prepare the detailed response
            video_details = []
            for item in data.get("items", []):
                video_details.append({
                    "video_id": item["id"]["videoId"],
                    "title": item["snippet"]["title"],
                    "description": item["snippet"]["description"],
                    "thumbnail_url": item["snippet"]["thumbnails"]["default"]["url"],
                    "published_at": item["snippet"]["publishedAt"],
                    "channel_id": item["snippet"]["channelId"],
                    "channel_title": item["snippet"]["channelTitle"],
                    # Optional fields can be added later, like view count, etc.
                })

            return {"videos": video_details}

        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}, Response: {response.text}")
            return {"error": str(http_err), "details": response.json()}
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}