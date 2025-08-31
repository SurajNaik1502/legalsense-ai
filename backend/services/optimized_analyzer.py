import os
import json
import re
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import spacy
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
import textstat

from models.schemas import (
    AnalysisResult, ParsedDocument, Party, Clause, RiskOverview, RiskCategory,
    LanguageCode, PartyRole, RiskLevel, ClauseCategory
)
from services.gemini_service import GeminiService

logger = logging.getLogger(__name__)

class OptimizedAnalyzer:
    def __init__(self):
        self.gemini_service = GeminiService()
        self.nlp = None
        self._initialize_local_models()
        
    def _initialize_local_models(self):
        """Initialize lightweight local models for basic processing"""
        try:
            # Initialize spaCy (lightweight)
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                logger.warning("spaCy model not found. Installing...")
                os.system("python -m spacy download en_core_web_sm")
                self.nlp = spacy.load("en_core_web_sm")
            
            # Download NLTK data (minimal)
            try:
                nltk.data.find('tokenizers/punkt')
            except LookupError:
                nltk.download('punkt')
            
            try:
                nltk.data.find('corpora/stopwords')
            except LookupError:
                nltk.download('stopwords')
                
        except Exception as e:
            logger.error(f"Error initializing local models: {e}")
    
    async def analyze_document(self, text_content: str, language: str = "en") -> AnalysisResult:
        """
        Optimized document analysis using local models + single Gemini API call
        """
        try:
            # Use Gemini for comprehensive analysis (single API call)
            gemini_result = await self.gemini_service.batch_analyze_document(text_content, language)
            
            # Convert Gemini result to our schema
            parsed_doc = self._convert_gemini_to_schema(gemini_result, text_content)
            
            # Create risk overview
            risks = self._create_risk_overview(gemini_result.get("risk_analysis", {}))
            
            return AnalysisResult(
                doc=parsed_doc,
                risks=risks
            )
            
        except Exception as e:
            logger.error(f"Error in optimized analysis: {e}")
            # Fallback to local-only analysis
            return await self._local_fallback_analysis(text_content, language)
    
    def _convert_gemini_to_schema(self, gemini_result: Dict[str, Any], text_content: str) -> ParsedDocument:
        """Convert Gemini analysis result to our schema"""
        try:
            doc_info = gemini_result.get("document_info", {})
            parties_data = gemini_result.get("parties", [])
            dates_data = gemini_result.get("dates", {})
            obligations_data = gemini_result.get("obligations", [])
            clauses_data = gemini_result.get("clauses", [])
            
            # Convert parties
            parties = []
            for party_data in parties_data:
                try:
                    parties.append(Party(
                        name=party_data.get("name", "Unknown"),
                        role=PartyRole(party_data.get("role", "Other"))
                    ))
                except (KeyError, ValueError):
                    continue
            
            # Convert clauses
            clauses = []
            for i, clause_data in enumerate(clauses_data):
                try:
                    clauses.append(Clause(
                        id=f"clause_{i+1}",
                        title=clause_data.get("title", f"Clause {i+1}"),
                        original_text=clause_data.get("original_text", "")[:500],
                        simplified_text=clause_data.get("simplified_text", ""),
                        category=ClauseCategory(clause_data["category"]) if clause_data.get("category") else None,
                        risk_level=RiskLevel(clause_data["risk_level"]) if clause_data.get("risk_level") else None
                    ))
                except (KeyError, ValueError):
                    continue
            
            return ParsedDocument(
                id=str(datetime.now().timestamp()),
                title=doc_info.get("title", "Legal Document"),
                language=LanguageCode("en"),
                parties=parties,
                effective_date=dates_data.get("effective_date"),
                termination_date=dates_data.get("termination_date"),
                obligations=obligations_data,
                clauses=clauses,
                summary=gemini_result.get("summary", "Analysis completed"),
                notes=doc_info.get("notes", [])
            )
            
        except Exception as e:
            logger.error(f"Error converting Gemini result: {e}")
            return self._create_fallback_document(text_content)
    
    def _create_risk_overview(self, risk_data: Dict[str, Any]) -> RiskOverview:
        """Create risk overview from Gemini analysis"""
        try:
            # Import RiskCategory and RiskOverview here to avoid circular imports
            from models.schemas import RiskCategory, RiskOverview
            
            # Ensure we have some risk data
            if not risk_data:
                logger.warning("No risk data provided")
                risk_data = {}
            
            # Create risk categories with default scores if not provided
            by_category = [
                RiskCategory(category="Financial", score=risk_data.get("financial_score", 25)),
                RiskCategory(category="Legal", score=risk_data.get("legal_score", 30)),
                RiskCategory(category="Compliance", score=risk_data.get("compliance_score", 20)),
                RiskCategory(category="Termination", score=risk_data.get("termination_score", 15))
            ]
            
            # Ensure we have some recommendations
            recommendations = risk_data.get("recommendations", ["Standard risk assessment required"])
            if not recommendations:
                recommendations = ["No specific recommendations available"]
            
            return RiskOverview(
                by_category=by_category,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Error creating risk overview: {e}")
            return RiskOverview(
                by_category=[],
                recommendations=["Risk analysis unavailable"]
            )
    
    async def _local_fallback_analysis(self, text_content: str, language: str) -> AnalysisResult:
        """Local-only analysis when Gemini is not available"""
        try:
            # Basic local extraction
            parties = self._extract_parties_local(text_content)
            dates = self._extract_dates_local(text_content)
            obligations = self._extract_obligations_local(text_content)
            clauses = self._extract_clauses_local(text_content)
            summary = self._generate_summary_local(text_content)
            
            # Create document
            parsed_doc = ParsedDocument(
                id=str(datetime.now().timestamp()),
                title="Legal Document (Local Analysis)",
                language=LanguageCode(language),
                parties=parties,
                effective_date=dates.get("effective"),
                termination_date=dates.get("termination"),
                obligations=obligations,
                clauses=clauses,
                summary=summary,
                notes=["Analysis performed using local models only"]
            )
            
            # Basic risk assessment
            risks = RiskOverview(
                by_category=[
                    RiskCategory(category="Financial", score=25),
                    RiskCategory(category="Legal", score=30),
                    RiskCategory(category="Compliance", score=20),
                    RiskCategory(category="Termination", score=15)
                ],
                recommendations=["Consider using Gemini API for detailed analysis"]
            )
            
            return AnalysisResult(doc=parsed_doc, risks=risks)
            
        except Exception as e:
            logger.error(f"Error in local fallback analysis: {e}")
            return self._create_error_result()
    
    def _extract_parties_local(self, text: str) -> List[Party]:
        """Local party extraction using regex patterns"""
        parties = []
        
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
        
        return parties[:4]
    
    def _extract_dates_local(self, text: str) -> Dict[str, Optional[str]]:
        """Local date extraction using regex"""
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
        
        return {"effective_date": effective_date, "termination_date": termination_date}
    
    def _extract_obligations_local(self, text: str) -> List[str]:
        """Local obligation extraction using keyword patterns"""
        obligations = []
        
        obligation_keywords = [
            "shall", "must", "will", "agree to", "responsible for", "obligated to",
            "required to", "duty to", "commitment to", "undertake to"
        ]
        
        sentences = sent_tokenize(text)
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            if any(keyword in sentence_lower for keyword in obligation_keywords):
                obligations.append(sentence.strip())
        
        return obligations[:10]
    
    def _extract_clauses_local(self, text: str) -> List[Clause]:
        """Local clause extraction using section headers"""
        clauses = []
        
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
                next_match = re.search(pattern, text[start_pos:])
                if next_match:
                    content = text[start_pos:start_pos + next_match.start()]
                else:
                    content = text[start_pos:]
                
                sections.append({
                    "title": title,
                    "content": content.strip()
                })
        
        for i, section in enumerate(sections[:10]):
            clauses.append(Clause(
                id=f"clause_{i+1}",
                title=section["title"],
                original_text=section["content"][:500],
                simplified_text=f"Section about {section['title'].lower()}",
                category=None,
                risk_level=None
            ))
        
        return clauses
    
    def _generate_summary_local(self, text: str) -> str:
        """Local summary generation using first few sentences"""
        sentences = sent_tokenize(text)
        return " ".join(sentences[:3])
    
    def _create_fallback_document(self, text_content: str) -> ParsedDocument:
        """Create a fallback document when conversion fails"""
        return ParsedDocument(
            id=str(datetime.now().timestamp()),
            title="Legal Document",
            language=LanguageCode("en"),
            parties=[],
            effective_date=None,
            termination_date=None,
            obligations=[],
            clauses=[],
            summary="Document analysis completed with limited information.",
            notes=["Analysis conversion failed"]
        )
    
    def _create_error_result(self) -> AnalysisResult:
        """Create error result when all analysis fails"""
        error_doc = ParsedDocument(
            id=str(datetime.now().timestamp()),
            title="Analysis Error",
            language=LanguageCode("en"),
            parties=[],
            effective_date=None,
            termination_date=None,
            obligations=[],
            clauses=[],
            summary="Document analysis failed. Please try again.",
            notes=["Analysis error occurred"]
        )
        
        error_risks = RiskOverview(
            by_category=[],
            recommendations=["Please check your configuration and try again"]
        )
        
        return AnalysisResult(doc=error_doc, risks=error_risks)
