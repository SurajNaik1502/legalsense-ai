import os
import json
import logging
from typing import Dict, Any, List, Optional
import google.generativeai as genai
from datetime import datetime

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self):
        self.model = None
        self._initialize_model()
        
    def _initialize_model(self):
        """Initialize Gemini model"""
        try:
            api_key = os.getenv("GOOGLE_API_KEY")
            if api_key:
                genai.configure(api_key=api_key)
                # Use Gemini 2.0 Flash for better performance and cost
                self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
                logger.info("Gemini 2.0 Flash model initialized successfully")
            else:
                logger.warning("GOOGLE_API_KEY not set. Gemini features will be disabled.")
                
        except Exception as e:
            logger.error(f"Error initializing Gemini model: {e}")
    
    async def batch_analyze_document(self, text_content: str, language: str = "en") -> Dict[str, Any]:
        """
        Single API call to analyze entire document - extracts all information at once
        This reduces API calls from 7+ to just 1 per document
        """
        if not self.model:
            return self._fallback_analysis()
        
        try:
            prompt = f"""
            Analyze this legal document and extract key information. Return ONLY a valid JSON object with this exact structure:

            {{
                "document_info": {{
                    "title": "Document title or type",
                    "type": "Contract/Agreement/Other",
                    "notes": []
                }},
                "parties": [
                    {{"name": "Party name", "role": "Lessor/Lessee/Employer/Employee/Vendor/Customer/Other"}}
                ],
                "dates": {{
                    "effective_date": "Date if found or null",
                    "termination_date": "Date if found or null"
                }},
                "obligations": [
                    "Key obligation 1",
                    "Key obligation 2"
                ],
                "clauses": [
                    {{
                        "title": "Clause title",
                        "original_text": "Brief clause text",
                        "simplified_text": "Simple explanation",
                        "category": "Financial/Legal/Compliance/Termination/General",
                        "risk_level": "Low/Medium/High"
                    }}
                ],
                "summary": "2-3 sentence summary",
                "risk_analysis": {{
                    "financial_score": 25,
                    "legal_score": 30,
                    "compliance_score": 20,
                    "termination_score": 15,
                    "recommendations": ["Recommendation 1", "Recommendation 2"]
                }}
            }}

            Document text to analyze:
            {text_content[:4000]}

            IMPORTANT: Return ONLY the JSON object, no other text.
            """
            
            response = self.model.generate_content(prompt)
            
            # Try to extract JSON from the response
            response_text = response.text.strip()
            
            # Remove any markdown formatting if present
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            response_text = response_text.strip()
            
            try:
                result = json.loads(response_text)
            except json.JSONDecodeError as e:
                logger.error(f"JSON parsing error: {e}. Response: {response_text[:200]}")
                return self._fallback_analysis()
            
            # Add metadata
            result["analysis_timestamp"] = datetime.utcnow().isoformat()
            result["model_used"] = "gemini-2.0-flash"
            
            return result
            
        except Exception as e:
            logger.error(f"Error in batch document analysis: {e}")
            return self._fallback_analysis()
    
    async def answer_question(self, question: str, document_content: str, language: str = "en") -> str:
        """Answer questions about legal documents using Gemini"""
        if not self.model:
            return "I'm sorry, I couldn't process your question at the moment."
        
        try:
            prompt = f"""
            You are a legal document assistant. Answer the following question about the legal document provided.
            
            Document content:
            {document_content[:4000]}
            
            Question: {question}
            
            Instructions:
            1. Answer based only on the information in the document
            2. If the information is not in the document, say so
            3. Provide specific references to relevant sections when possible
            4. Keep answers concise but informative (max 200 words)
            5. Use professional legal language
            
            Answer:
            """
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Error answering question: {e}")
            return "I'm sorry, I couldn't process your question at the moment."
    
    async def generate_suggested_questions(self, document_content: str, language: str = "en") -> List[str]:
        """Generate suggested questions based on document content"""
        if not self.model:
            return self._default_suggestions()
        
        try:
            prompt = f"""
            Based on this legal document, generate 5 relevant questions. Return ONLY a JSON array like this:
            ["Question 1", "Question 2", "Question 3", "Question 4", "Question 5"]
            
            Document content:
            {document_content[:3000]}
            """
            
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Clean up the response
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            response_text = response_text.strip()
            
            try:
                questions = json.loads(response_text)
                if isinstance(questions, list):
                    return questions[:5]
                else:
                    return self._default_suggestions()
            except json.JSONDecodeError:
                return self._default_suggestions()
            
        except Exception as e:
            logger.error(f"Error generating suggested questions: {e}")
            return self._default_suggestions()
    
    def _fallback_analysis(self) -> Dict[str, Any]:
        """Fallback analysis when Gemini is not available"""
        return {
            "document_info": {
                "title": "Legal Document",
                "type": "Contract",
                "notes": ["Analysis performed using fallback method"]
            },
            "parties": [],
            "dates": {
                "effective_date": None,
                "termination_date": None
            },
            "obligations": [],
            "clauses": [],
            "summary": "Document analysis completed using fallback method. Consider checking API configuration for enhanced analysis.",
            "risk_analysis": {
                "financial_score": 25,
                "legal_score": 30,
                "compliance_score": 20,
                "termination_score": 15,
                "recommendations": ["Use Gemini API for detailed analysis"]
            },
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "model_used": "fallback"
        }
    
    def _default_suggestions(self) -> List[str]:
        """Default suggested questions when Gemini is not available"""
        return [
            "Who are the parties involved in this agreement?",
            "What are the main obligations of each party?",
            "What are the payment terms and amounts?",
            "How can this agreement be terminated?",
            "What happens in case of breach or default?"
        ]
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model"""
        return {
            "model_name": "gemini-2.0-flash-exp" if self.model else "none",
            "api_available": self.model is not None,
            "optimization": "batch_analysis",
            "estimated_cost_savings": "85% vs individual API calls"
        }
