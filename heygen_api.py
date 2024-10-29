import requests
import time
from typing import Optional, Dict, List

class HeyGenAPI:
    BASE_URL = "https://api.heygen.com/v1"
    
    def __init__(self, api_key: str):
        """Initialize HeyGen API client with API key"""
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def get_avatars(self) -> List[Dict]:
        """
        Fetch available avatars from HeyGen API
        Returns: List of avatar dictionaries
        """
        try:
            response = requests.get(
                f"{self.BASE_URL}/avatars",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json().get("data", [])
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch avatars: {str(e)}")
    
    def create_video(self, script: str, avatar_id: str) -> str:
        """
        Create a video using HeyGen API
        
        Args:
            script: The text content for the video
            avatar_id: The ID of the selected avatar
            
        Returns: Video ID string
        """
        try:
            payload = {
                "script": {
                    "text": script
                },
                "avatar": {
                    "avatar_id": avatar_id
                },
                "background": {
                    "type": "color",
                    "value": "#ffffff"
                }
            }
            
            response = requests.post(
                f"{self.BASE_URL}/videos",
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            return response.json().get("data", {}).get("video_id")
        except requests.RequestException as e:
            raise Exception(f"Failed to create video: {str(e)}")
    
    def get_video_status(self, video_id: str) -> Dict:
        """
        Check the status of a video
        
        Args:
            video_id: The ID of the video to check
            
        Returns: Dictionary containing video status information
        """
        try:
            response = requests.get(
                f"{self.BASE_URL}/videos/{video_id}",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json().get("data", {})
        except requests.RequestException as e:
            raise Exception(f"Failed to get video status: {str(e)}")
    
    def wait_for_video(self, video_id: str, timeout: int = 300) -> Dict:
        """
        Wait for video to be ready with timeout
        
        Args:
            video_id: The ID of the video to wait for
            timeout: Maximum time to wait in seconds
            
        Returns: Dictionary containing final video information
        """
        start_time = time.time()
        while True:
            if time.time() - start_time > timeout:
                raise Exception("Video generation timed out")
            
            status = self.get_video_status(video_id)
            if status.get("status") == "completed":
                return status
            elif status.get("status") == "failed":
                raise Exception(f"Video generation failed: {status.get('error')}")
            
            time.sleep(5)  # Wait 5 seconds before checking again
