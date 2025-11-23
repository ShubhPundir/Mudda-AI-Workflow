"""
Gemini AI client for low-level API interaction
"""
import os
import google.generativeai as genai


class GeminiClient:
    """
    Low-level Gemini AI client for API interaction
    Handles only initialization and model access
    """
    
    def __init__(self):
        self.model = None
        self._initialize_gemini()
    
    def _initialize_gemini(self):
        """Initialize Gemini AI client"""
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
    
    def generate(self, content: str):
        """
        Generate content using the Gemini model
        
        Args:
            content: The prompt/content to send to the model
            
        Returns:
            Response object from Gemini API
        """
        return self.model.generate_content(content)


# Global Gemini client instance
gemini_client = GeminiClient()
