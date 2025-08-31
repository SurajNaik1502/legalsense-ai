from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from enum import Enum
from datetime import datetime

class LanguageCode(str, Enum):
    EN = "en"
    HI = "hi"
    MR = "mr"

class PartyRole(str, Enum):
    LESSOR = "Lessor"
    LESSEE = "Lessee"
    EMPLOYER = "Employer"
    EMPLOYEE = "Employee"
    PARTY_A = "PartyA"
    PARTY_B = "PartyB"
    VENDOR = "Vendor"
    CUSTOMER = "Customer"
    OTHER = "Other"

class RiskLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

class ClauseCategory(str, Enum):
    FINANCIAL = "Financial"
    LEGAL = "Legal"
    COMPLIANCE = "Compliance"
    TERMINATION = "Termination"
    GENERAL = "General"

# Base models
class Party(BaseModel):
    name: str
    role: PartyRole

class Clause(BaseModel):
    id: str
    title: str
    original_text: str
    simplified_text: str
    category: Optional[ClauseCategory] = None
    risk_level: Optional[RiskLevel] = None

class RiskCategory(BaseModel):
    category: str
    score: int

class RiskOverview(BaseModel):
    by_category: List[RiskCategory]
    recommendations: List[str]

class ParsedDocument(BaseModel):
    id: str
    title: str
    language: LanguageCode
    parties: List[Party]
    effective_date: Optional[str] = None
    termination_date: Optional[str] = None
    obligations: List[str]
    clauses: List[Clause]
    summary: str
    notes: Optional[List[str]] = None

class AnalysisResult(BaseModel):
    doc: ParsedDocument
    risks: RiskOverview

# API Request/Response models
class DocumentUploadResponse(BaseModel):
    success: bool
    document_id: str
    document_info: Dict[str, Any]
    message: str

class AnalysisRequest(BaseModel):
    document_id: str
    language: LanguageCode = LanguageCode.EN

class AnalysisResponse(BaseModel):
    success: bool
    analysis: AnalysisResult
    message: str

class QARequest(BaseModel):
    document_id: str
    question: str
    language: LanguageCode = LanguageCode.EN

class QAResponse(BaseModel):
    success: bool
    answer: str
    message: str

class DocumentInfo(BaseModel):
    id: str
    filename: str
    content_type: str
    size: int
    uploaded_at: datetime
    language: LanguageCode
    processing_status: str
    word_count: Optional[int] = None
    page_count: Optional[int] = None

# Error models
class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
