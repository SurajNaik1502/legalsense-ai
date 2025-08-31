import os
import json
import re
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import openai
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import spacy
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
import textstat

from models.schemas import (
    AnalysisResult, ParsedDocument, Party, Clause, RiskOverview,
    LanguageCode, PartyRole, RiskLevel, ClauseCategory
)

logger = logging.getLogger(__name__)

class NLPAnalyzer:
    def __init__(self):
        self.openai_client = None
        self.sentiment_analyzer = None
        self.nlp = None
        self._initialize_models()
        
    def _initialize_models(self):
        """Initialize NLP models and tools"""
        try:
            # Initialize OpenAI client
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                self.openai_client = openai.OpenAI(api_key=api_key)
            
            # Initialize sentiment analysis
            try:
                self.sentiment_analyzer = pipeline(
                    "sentiment-analysis",
                    model="cardiffnlp/twitter-roberta-base-sentiment-latest"
                )
            except Exception as e:
                logger.warning(f"Could not load sentiment analyzer: {e}")
            
            # Initialize spaCy
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                logger.warning("spaCy model not found. Installing...")
                os.system("python -m spacy download en_core_web_sm")
                self.nlp = spacy.load("en_core_web_sm")
            
            # Download NLTK data
            try:
                nltk.data.find('tokenizers/punkt')
            except LookupError:
                nltk.download('punkt')
            
            try:
                nltk.data.find('corpora/stopwords')
            except LookupError:
                nltk.download('stopwords')
                
        except Exception as e:
            logger.error(f"Error initializing NLP models: {e}")
    
    async def analyze_document(self, text_content: str, language: str = "en") -> AnalysisResult:
        """Analyze legal document and extract structured information"""
        try:
            # Extract basic document information
            doc_info = await self._extract_document_info(text_content, language)
            
            # Extract parties
            parties = await self._extract_parties(text_content, language)
            
            # Extract dates
            effective_date, termination_date = await self._extract_dates(text_content)
            
            # Extract obligations
            obligations = await self._extract_obligations(text_content, language)
            
            # Extract and analyze clauses
            clauses = await self._extract_clauses(text_content, language)
            
            # Generate summary
            summary = await self._generate_summary(text_content, language)
            
            # Analyze risks
            risks = await self._analyze_risks(text_content, clauses, language)
            
            # Create parsed document
            parsed_doc = ParsedDocument(
                id=doc_info["id"],
                title=doc_info["title"],
                language=LanguageCode(language),
                parties=parties,
                effective_date=effective_date,
                termination_date=termination_date,
                obligations=obligations,
                clauses=clauses,
                summary=summary,
                notes=doc_info.get("notes", [])
            )
            
            return AnalysisResult(
                doc=parsed_doc,
                risks=risks
            )
            
        except Exception as e:
            logger.error(f"Error analyzing document: {e}")
            raise
    
    async def _extract_document_info(self, text: str, language: str) -> Dict[str, Any]:
        """Extract basic document information"""
        try:
            if self.openai_client:
                # Use OpenAI for better extraction
                prompt = f"""
                Extract the following information from this legal document:
                1. Document title/name
                2. Document type (contract, agreement, etc.)
                3. Any important notes or warnings
                
                Document text:
                {text[:2000]}...
                
                Return as JSON with keys: title, type, notes
                """
                
                response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=500
                )
                
                result = json.loads(response.choices[0].message.content)
                return {
                    "id": str(datetime.now().timestamp()),
                    "title": result.get("title", "Legal Document"),
                    "type": result.get("type", "Contract"),
                    "notes": result.get("notes", [])
                }
            else:
                # Fallback to basic extraction
                lines = text.split('\n')
                title = lines[0] if lines else "Legal Document"
                return {
                    "id": str(datetime.now().timestamp()),
                    "title": title[:100],
                    "type": "Contract",
                    "notes": []
                }
                
        except Exception as e:
            logger.error(f"Error extracting document info: {e}")
            return {
                "id": str(datetime.now().timestamp()),
                "title": "Legal Document",
                "type": "Contract",
                "notes": []
            }
    
    async def _extract_parties(self, text: str, language: str) -> List[Party]:
        """Extract parties from legal document"""
        try:
            if self.openai_client:
                prompt = f"""
                Extract all parties mentioned in this legal document. For each party, identify:
                1. Name
                2. Role (Lessor, Lessee, Employer, Employee, PartyA, PartyB, Vendor, Customer, Other)
                
                Document text:
                {text[:2000]}...
                
                Return as JSON array with objects containing: name, role
                """
                
                response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=500
                )
                
                parties_data = json.loads(response.choices[0].message.content)
                parties = []
                
                for party_data in parties_data:
                    try:
                        parties.append(Party(
                            name=party_data["name"],
                            role=PartyRole(party_data["role"])
                        ))
                    except (KeyError, ValueError):
                        continue
                
                return parties
            else:
                # Fallback to basic extraction
                return self._basic_party_extraction(text)
                
        except Exception as e:
            logger.error(f"Error extracting parties: {e}")
            return self._basic_party_extraction(text)
    
    def _basic_party_extraction(self, text: str) -> List[Party]:
        """Basic party extraction using regex patterns"""
        parties = []
        
        # Common patterns for party identification
        patterns = [
            r"between\s+([^,]+?)\s+and\s+([^,]+?)(?:\s|$)",
            r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:as\s+)?(?:the\s+)?(Lessor|Lessee|Employer|Employee|Vendor|Customer)",
            r"(?:Party\s+A|First\s+Party)\s*[:=]\s*([^,\n]+)",
            r"(?:Party\s+B|Second\s+Party)\s*[:=]\s*([^,\n]+)"
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                if len(match.groups()) == 2:
                    name = match.group(1).strip()
                    role = match.group(2).strip()
                    try:
                        parties.append(Party(name=name, role=PartyRole(role)))
                    except ValueError:
                        parties.append(Party(name=name, role=PartyRole.OTHER))
                elif len(match.groups()) == 1:
                    name = match.group(1).strip()
                    parties.append(Party(name=name, role=PartyRole.OTHER))
        
        return parties[:4]  # Limit to 4 parties
    
    async def _extract_dates(self, text: str) -> tuple[Optional[str], Optional[str]]:
        """Extract effective and termination dates"""
        try:
            # Date patterns
            date_patterns = [
                r"effective\s+date[:\s]*([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{2,4})",
                r"commencement\s+date[:\s]*([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{2,4})",
                r"start\s+date[:\s]*([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{2,4})",
                r"termination\s+date[:\s]*([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{2,4})",
                r"end\s+date[:\s]*([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{2,4})",
                r"expiry\s+date[:\s]*([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{2,4})"
            ]
            
            effective_date = None
            termination_date = None
            
            for pattern in date_patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    date_str = match.group(1)
                    if "effective" in match.group(0).lower() or "commencement" in match.group(0).lower() or "start" in match.group(0).lower():
                        effective_date = date_str
                    elif "termination" in match.group(0).lower() or "end" in match.group(0).lower() or "expiry" in match.group(0).lower():
                        termination_date = date_str
            
            return effective_date, termination_date
            
        except Exception as e:
            logger.error(f"Error extracting dates: {e}")
            return None, None
    
    async def _extract_obligations(self, text: str, language: str) -> List[str]:
        """Extract obligations from legal document"""
        try:
            if self.openai_client:
                prompt = f"""
                Extract the main obligations and responsibilities from this legal document.
                Return as a JSON array of strings, each describing one obligation.
                
                Document text:
                {text[:2000]}...
                """
                
                response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=500
                )
                
                obligations = json.loads(response.choices[0].message.content)
                return obligations[:10]  # Limit to 10 obligations
            else:
                # Fallback to basic extraction
                return self._basic_obligation_extraction(text)
                
        except Exception as e:
            logger.error(f"Error extracting obligations: {e}")
            return self._basic_obligation_extraction(text)
    
    def _basic_obligation_extraction(self, text: str) -> List[str]:
        """Basic obligation extraction using keyword patterns"""
        obligations = []
        
        # Keywords that indicate obligations
        obligation_keywords = [
            "shall", "must", "will", "agree to", "responsible for", "obligated to",
            "required to", "duty to", "commitment to", "undertake to"
        ]
        
        sentences = sent_tokenize(text)
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            if any(keyword in sentence_lower for keyword in obligation_keywords):
                obligations.append(sentence.strip())
        
        return obligations[:10]  # Limit to 10 obligations
    
    async def _extract_clauses(self, text: str, language: str) -> List[Clause]:
        """Extract and analyze clauses from legal document"""
        try:
            if self.openai_client:
                prompt = f"""
                Extract and analyze the main clauses from this legal document.
                For each clause, provide:
                1. A descriptive title
                2. The original text
                3. A simplified explanation
                4. Category (Financial, Legal, Compliance, Termination, General)
                5. Risk level (Low, Medium, High)
                
                Document text:
                {text[:3000]}...
                
                Return as JSON array with objects containing: title, original_text, simplified_text, category, risk_level
                """
                
                response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=1000
                )
                
                clauses_data = json.loads(response.choices[0].message.content)
                clauses = []
                
                for i, clause_data in enumerate(clauses_data):
                    try:
                        clauses.append(Clause(
                            id=f"clause_{i+1}",
                            title=clause_data["title"],
                            original_text=clause_data["original_text"],
                            simplified_text=clause_data["simplified_text"],
                            category=ClauseCategory(clause_data["category"]) if clause_data.get("category") else None,
                            risk_level=RiskLevel(clause_data["risk_level"]) if clause_data.get("risk_level") else None
                        ))
                    except (KeyError, ValueError) as e:
                        logger.warning(f"Error parsing clause {i}: {e}")
                        continue
                
                return clauses
            else:
                # Fallback to basic extraction
                return self._basic_clause_extraction(text)
                
        except Exception as e:
            logger.error(f"Error extracting clauses: {e}")
            return self._basic_clause_extraction(text)
    
    def _basic_clause_extraction(self, text: str) -> List[Clause]:
        """Basic clause extraction using section headers"""
        clauses = []
        
        # Split by common section headers
        section_patterns = [
            r"\d+\.\s*([^:\n]+):",
            r"([A-Z][A-Z\s]+):",
            r"Section\s+\d+[:\s]*([^:\n]+)",
            r"Article\s+\d+[:\s]*([^:\n]+)"
        ]
        
        sections = []
        for pattern in section_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                title = match.group(1).strip()
                start_pos = match.end()
                # Find next section or end of text
                next_match = re.search(pattern, text[start_pos:])
                if next_match:
                    content = text[start_pos:start_pos + next_match.start()]
                else:
                    content = text[start_pos:]
                
                sections.append({
                    "title": title,
                    "content": content.strip()
                })
        
        # Create clauses from sections
        for i, section in enumerate(sections[:10]):  # Limit to 10 clauses
            clauses.append(Clause(
                id=f"clause_{i+1}",
                title=section["title"],
                original_text=section["content"][:500],  # Limit text length
                simplified_text=f"Section about {section['title'].lower()}",
                category=None,
                risk_level=None
            ))
        
        return clauses
    
    async def _generate_summary(self, text: str, language: str) -> str:
        """Generate document summary"""
        try:
            if self.openai_client:
                prompt = f"""
                Generate a concise summary of this legal document in 2-3 sentences.
                Focus on the main purpose, parties involved, and key terms.
                
                Document text:
                {text[:2000]}...
                """
                
                response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=200
                )
                
                return response.choices[0].message.content.strip()
            else:
                # Fallback to basic summary
                sentences = sent_tokenize(text)
                return " ".join(sentences[:3])  # First 3 sentences
                
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return "Legal document requiring analysis."
    
    async def _analyze_risks(self, text: str, clauses: List[Clause], language: str) -> RiskOverview:
        """Analyze risks in the document"""
        try:
            # Calculate risk scores by category
            risk_scores = {
                "Financial": 0,
                "Legal": 0,
                "Compliance": 0,
                "Termination": 0
            }
            
            # Count high-risk clauses by category
            for clause in clauses:
                if clause.category and clause.risk_level:
                    if clause.risk_level == RiskLevel.HIGH:
                        risk_scores[clause.category.value] += 30
                    elif clause.risk_level == RiskLevel.MEDIUM:
                        risk_scores[clause.category.value] += 15
                    else:
                        risk_scores[clause.category.value] += 5
            
            # Normalize scores to 0-100
            max_clauses = max(len([c for c in clauses if c.category == cat]) for cat in risk_scores.keys())
            if max_clauses > 0:
                for category in risk_scores:
                    risk_scores[category] = min(100, risk_scores[category] / max_clauses * 100)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(risk_scores, clauses)
            
            return RiskOverview(
                by_category=[
                    {"category": cat, "score": score}
                    for cat, score in risk_scores.items()
                ],
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Error analyzing risks: {e}")
            return RiskOverview(
                by_category=[],
                recommendations=["Risk analysis unavailable"]
            )
    
    def _generate_recommendations(self, risk_scores: Dict[str, float], clauses: List[Clause]) -> List[str]:
        """Generate risk-based recommendations"""
        recommendations = []
        
        for category, score in risk_scores.items():
            if score > 70:
                recommendations.append(f"High {category.lower()} risk detected. Consider legal review.")
            elif score > 40:
                recommendations.append(f"Moderate {category.lower()} risk. Review terms carefully.")
            elif score > 20:
                recommendations.append(f"Low {category.lower()} risk. Standard terms.")
        
        if not recommendations:
            recommendations.append("Document appears to have standard risk levels.")
        
        return recommendations[:5]  # Limit to 5 recommendations
