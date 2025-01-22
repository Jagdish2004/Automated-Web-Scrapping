from google.generativeai import GenerativeModel
import google.generativeai as genai
from typing import List, Dict
from src.config import Config
import json

class GeminiHelper:
    def __init__(self):
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = GenerativeModel('gemini-pro')
        
    def get_industries_and_companies(self) -> Dict[str, List[str]]:
        """Get industries and their top companies using Gemini"""
        prompt = """
        Generate a comprehensive list of major industries and their top companies worldwide.
        Format the response as a JSON object where keys are industry names and values are 
        lists of company names. Include at least 50 companies per industry.
        Focus on industries like: Technology, Healthcare, Finance, Manufacturing, Retail, 
        Energy, Telecommunications, Automotive, etc.
        Include company full names only, no descriptions.
        """
        
        response = self.model.generate_content(prompt)
        try:
            # Parse the response to get JSON data
            json_str = response.text.strip('```json\n').strip('```')
            return json.loads(json_str)
        except Exception as e:
            print(f"Error parsing Gemini response: {e}")
            return {}
            
    def expand_company_list(self, industry: str, existing_companies: List[str]) -> List[str]:
        """Get more companies for a specific industry"""
        prompt = f"""
        Generate a list of 100 additional companies in the {industry} industry.
        Do not include these existing companies: {', '.join(existing_companies)}
        Format the response as a JSON array of company names only.
        Include both well-known and emerging companies.
        """
        
        response = self.model.generate_content(prompt)
        try:
            json_str = response.text.strip('```json\n').strip('```')
            return json.loads(json_str)
        except:
            return [] 