const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface DocumentUploadResponse {
  success: boolean;
  document_id: string;
  document_info: any;
  message: string;
}

export interface AnalysisRequest {
  document_id: string;
  language: string;
}

export interface AnalysisResponse {
  success: boolean;
  analysis: any;
  message: string;
}

export interface QARequest {
  document_id: string;
  question: string;
  language: string;
}

export interface QAResponse {
  success: boolean;
  answer: string;
  message: string;
}

export interface DocumentInfo {
  id: string;
  filename: string;
  content_type: string;
  size: number;
  uploaded_at: string;
  language: string;
  processing_status: string;
  word_count?: number;
  page_count?: number;
}

class ApiService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = API_BASE_URL;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    
    const defaultOptions: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    };

    const response = await fetch(url, { ...defaultOptions, ...options });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  async uploadDocument(file: File, language: string = 'en'): Promise<DocumentUploadResponse> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('language', language);

    const response = await fetch(`${this.baseUrl}/api/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Upload failed! status: ${response.status}`);
    }

    return response.json();
  }

  async analyzeDocument(documentId: string, language: string = 'en'): Promise<AnalysisResponse> {
    return this.request<AnalysisResponse>('/api/analyze', {
      method: 'POST',
      body: JSON.stringify({
        document_id: documentId,
        language: language,
      }),
    });
  }

  async askQuestion(documentId: string, question: string, language: string = 'en'): Promise<QAResponse> {
    return this.request<QAResponse>('/api/qa', {
      method: 'POST',
      body: JSON.stringify({
        document_id: documentId,
        question: question,
        language: language,
      }),
    });
  }

  async getDocumentInfo(documentId: string): Promise<{ success: boolean; document_info: DocumentInfo }> {
    return this.request<{ success: boolean; document_info: DocumentInfo }>(`/api/documents/${documentId}`);
  }

  async deleteDocument(documentId: string): Promise<{ success: boolean; message: string }> {
    return this.request<{ success: boolean; message: string }>(`/api/documents/${documentId}`, {
      method: 'DELETE',
    });
  }

  async healthCheck(): Promise<{ status: string; services: any }> {
    return this.request<{ status: string; services: any }>('/health');
  }
}

export const apiService = new ApiService();
