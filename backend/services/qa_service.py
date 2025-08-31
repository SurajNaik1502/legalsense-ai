import os
import json
import logging
from typing import Optional, List, Dict, Any
import openai
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import re

logger = logging.getLogger(__name__)

class QAService:
    def __init__(self):
        self.openai_client = None
        self.embedding_model = None
        self._initialize_models()
        
    def _initialize_models(self):
        """Initialize QA models"""
        try:
            # Initialize OpenAI client
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                self.openai_client = openai.OpenAI(api_key=api_key)
            
            # Initialize sentence transformer for embeddings
            try:
                self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            except Exception as e:
                logger.warning(f"Could not load embedding model: {e}")
                
        except Exception as e:
            logger.error(f"Error initializing QA models: {e}")
    
    async def get_answer(self, question: str, document_content: str, language: str = "en") -> str:
        """Get answer to question about legal document"""
        try:
            if self.openai_client:
                return await self._get_openai_answer(question, document_content, language)
            else:
                return await self._get_basic_answer(question, document_content, language)
                
        except Exception as e:
            logger.error(f"Error getting answer: {e}")
            return "I'm sorry, I couldn't process your question at the moment. Please try again."
    
    async def _get_openai_answer(self, question: str, document_content: str, language: str) -> str:
        """Get answer using OpenAI"""
        try:
            # Create context-aware prompt
            prompt = f"""
            You are a legal document assistant. Answer the following question about the legal document provided.
            
            Document content:
            {document_content[:4000]}...
            
            Question: {question}
            
            Instructions:
            1. Answer based only on the information in the document
            2. If the information is not in the document, say so
            3. Provide specific references to relevant sections when possible
            4. Keep answers concise but informative
            5. Use professional legal language
            
            Answer:
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful legal document assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error with OpenAI answer: {e}")
            return await self._get_basic_answer(question, document_content, language)
    
    async def _get_basic_answer(self, question: str, document_content: str, language: str) -> str:
        """Get basic answer using keyword matching and context"""
        try:
            # Simple keyword-based answer generation
            question_lower = question.lower()
            document_lower = document_content.lower()
            
            # Common question patterns and their handling
            if any(word in question_lower for word in ["party", "parties", "who"]):
                return self._extract_party_info(document_content)
            elif any(word in question_lower for word in ["date", "when", "effective", "termination"]):
                return self._extract_date_info(document_content)
            elif any(word in question_lower for word in ["obligation", "responsibility", "duty", "must", "shall"]):
                return self._extract_obligation_info(document_content)
            elif any(word in question_lower for word in ["payment", "money", "cost", "fee", "price"]):
                return self._extract_payment_info(document_content)
            elif any(word in question_lower for word in ["terminate", "end", "cancel", "breach"]):
                return self._extract_termination_info(document_content)
            else:
                return self._extract_general_info(question, document_content)
                
        except Exception as e:
            logger.error(f"Error with basic answer: {e}")
            return "I'm sorry, I couldn't find relevant information to answer your question."
    
    def _extract_party_info(self, document_content: str) -> str:
        """Extract information about parties"""
        try:
            # Look for party information
            party_patterns = [
                r"between\s+([^,]+?)\s+and\s+([^,]+?)(?:\s|$)",
                r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:as\s+)?(?:the\s+)?(Lessor|Lessee|Employer|Employee|Vendor|Customer)",
                r"(?:Party\s+A|First\s+Party)\s*[:=]\s*([^,\n]+)",
                r"(?:Party\s+B|Second\s+Party)\s*[:=]\s*([^,\n]+)"
            ]
            
            parties = []
            for pattern in party_patterns:
                matches = re.finditer(pattern, document_content, re.IGNORECASE)
                for match in matches:
                    if len(match.groups()) == 2:
                        name = match.group(1).strip()
                        role = match.group(2).strip()
                        parties.append(f"{name} ({role})")
                    elif len(match.groups()) == 1:
                        name = match.group(1).strip()
                        parties.append(name)
            
            if parties:
                return f"The parties involved are: {', '.join(set(parties))}"
            else:
                return "Party information could not be clearly identified in the document."
                
        except Exception as e:
            return "Party information could not be extracted."
    
    def _extract_date_info(self, document_content: str) -> str:
        """Extract date information"""
        try:
            date_patterns = [
                r"effective\s+date[:\s]*([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{2,4})",
                r"commencement\s+date[:\s]*([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{2,4})",
                r"start\s+date[:\s]*([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{2,4})",
                r"termination\s+date[:\s]*([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{2,4})",
                r"end\s+date[:\s]*([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{2,4})",
                r"expiry\s+date[:\s]*([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{2,4})"
            ]
            
            dates = []
            for pattern in date_patterns:
                matches = re.finditer(pattern, document_content, re.IGNORECASE)
                for match in matches:
                    date_str = match.group(1)
                    context = match.group(0)
                    if "effective" in context.lower() or "commencement" in context.lower() or "start" in context.lower():
                        dates.append(f"Effective date: {date_str}")
                    elif "termination" in context.lower() or "end" in context.lower() or "expiry" in context.lower():
                        dates.append(f"Termination date: {date_str}")
            
            if dates:
                return " ".join(dates)
            else:
                return "Date information could not be clearly identified in the document."
                
        except Exception as e:
            return "Date information could not be extracted."
    
    def _extract_obligation_info(self, document_content: str) -> str:
        """Extract obligation information"""
        try:
            obligation_keywords = [
                "shall", "must", "will", "agree to", "responsible for", "obligated to",
                "required to", "duty to", "commitment to", "undertake to"
            ]
            
            sentences = document_content.split('.')
            obligations = []
            
            for sentence in sentences:
                sentence_lower = sentence.lower()
                if any(keyword in sentence_lower for keyword in obligation_keywords):
                    obligations.append(sentence.strip())
            
            if obligations:
                return f"Key obligations include: {' '.join(obligations[:3])}"
            else:
                return "Specific obligations could not be clearly identified in the document."
                
        except Exception as e:
            return "Obligation information could not be extracted."
    
    def _extract_payment_info(self, document_content: str) -> str:
        """Extract payment information"""
        try:
            payment_patterns = [
                r"\$[\d,]+(?:\.\d{2})?",
                r"[\d,]+(?:\.\d{2})?\s*(?:dollars?|USD)",
                r"payment\s+of\s+[\d,]+(?:\.\d{2})?",
                r"fee\s+of\s+[\d,]+(?:\.\d{2})?"
            ]
            
            payments = []
            for pattern in payment_patterns:
                matches = re.finditer(pattern, document_content, re.IGNORECASE)
                for match in matches:
                    payments.append(match.group(0))
            
            if payments:
                return f"Payment information found: {'; '.join(payments[:3])}"
            else:
                return "Payment information could not be clearly identified in the document."
                
        except Exception as e:
            return "Payment information could not be extracted."
    
    def _extract_termination_info(self, document_content: str) -> str:
        """Extract termination information"""
        try:
            termination_keywords = [
                "terminate", "termination", "end", "cancel", "breach", "default",
                "violation", "failure to", "non-compliance"
            ]
            
            sentences = document_content.split('.')
            termination_info = []
            
            for sentence in sentences:
                sentence_lower = sentence.lower()
                if any(keyword in sentence_lower for keyword in termination_keywords):
                    termination_info.append(sentence.strip())
            
            if termination_info:
                return f"Termination conditions: {' '.join(termination_info[:2])}"
            else:
                return "Termination information could not be clearly identified in the document."
                
        except Exception as e:
            return "Termination information could not be extracted."
    
    def _extract_general_info(self, question: str, document_content: str) -> str:
        """Extract general information based on question keywords"""
        try:
            # Simple keyword matching
            question_words = question.lower().split()
            sentences = document_content.split('.')
            
            relevant_sentences = []
            for sentence in sentences:
                sentence_lower = sentence.lower()
                if any(word in sentence_lower for word in question_words if len(word) > 3):
                    relevant_sentences.append(sentence.strip())
            
            if relevant_sentences:
                return f"Based on the document: {' '.join(relevant_sentences[:2])}"
            else:
                return "I couldn't find specific information related to your question in the document."
                
        except Exception as e:
            return "I couldn't process your question at the moment."
    
    async def get_suggested_questions(self, document_content: str, language: str = "en") -> List[str]:
        """Get suggested questions based on document content"""
        try:
            if self.openai_client:
                return await self._get_openai_suggestions(document_content, language)
            else:
                return self._get_basic_suggestions(document_content)
                
        except Exception as e:
            logger.error(f"Error getting suggested questions: {e}")
            return [
                "Who are the parties involved?",
                "What are the key obligations?",
                "What are the payment terms?",
                "How can this agreement be terminated?"
            ]
    
    async def _get_openai_suggestions(self, document_content: str, language: str) -> List[str]:
        """Get suggested questions using OpenAI"""
        try:
            prompt = f"""
            Based on this legal document, generate 5 relevant questions that someone might ask.
            Focus on key legal aspects like parties, obligations, payments, termination, etc.
            
            Document content:
            {document_content[:2000]}...
            
            Return as JSON array of strings.
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.7
            )
            
            suggestions = json.loads(response.choices[0].message.content)
            return suggestions[:5]
            
        except Exception as e:
            logger.error(f"Error with OpenAI suggestions: {e}")
            return self._get_basic_suggestions(document_content)
    
    def _get_basic_suggestions(self, document_content: str) -> List[str]:
        """Get basic suggested questions"""
        suggestions = [
            "Who are the parties involved in this agreement?",
            "What are the main obligations of each party?",
            "What are the payment terms and amounts?",
            "How can this agreement be terminated?",
            "What happens in case of breach or default?"
        ]
        
        # Customize based on document content
        content_lower = document_content.lower()
        
        if any(word in content_lower for word in ["lease", "rental", "property"]):
            suggestions.extend([
                "What is the rental amount and payment schedule?",
                "What are the maintenance responsibilities?"
            ])
        elif any(word in content_lower for word in ["employment", "employee", "employer"]):
            suggestions.extend([
                "What are the employment terms and conditions?",
                "What are the termination procedures?"
            ])
        elif any(word in content_lower for word in ["service", "vendor", "consulting"]):
            suggestions.extend([
                "What services are being provided?",
                "What are the service level requirements?"
            ])
        
        return suggestions[:5]
