from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class QueryInfo(BaseModel):
    filename: str
    content_type: str
    size_bytes: int


class CheckResultItem(BaseModel):
    rank: int = Field(..., description="Peringkat kemiripan (1-5)")
    id: int = Field(..., description="ID internal indeks vektor")
    filename: str = Field(..., description="Nama file gambar referensi pembanding")
    image_url: str = Field(..., description="URL statis untuk melihat/memuat gambar referensi")
    title: Optional[str] = Field(None, description="Nama atau judul karya referensi")
    category: Optional[str] = Field(None, description="Kategori produk (misal: batik, tenun, fashion)")
    similarity_score: float = Field(..., description="Skor kemiripan visual (0.00% - 100.00%)")
    risk_level: str = Field(..., description="Kategori risiko: Cukup Orisinal | Perlu Ditinjau | Sangat Mirip")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata pendukung karya referensi")


class CheckResponse(BaseModel):
    status: str = Field(default="success")
    query: QueryInfo
    max_similarity_score: float = Field(..., description="Skor kemiripan tertinggi yang ditemukan (0-100%)")
    risk_level: str = Field(..., description="Kategori risiko keseluruhan: Cukup Orisinal | Perlu Ditinjau | Sangat Mirip")
    recommendation: str = Field(..., description="Rekomendasi tindak lanjut kontekstual")
    results: List[CheckResultItem] = Field(default_factory=list, description="Top-5 gambar pembanding paling mirip")
    disclaimer: str = Field(..., description="Disclaimer hukum wajib sesuai PRD Section 6 & 8")
    execution_time_ms: float = Field(..., description="Waktu komputasi end-to-end dalam milidetik")


class HealthResponse(BaseModel):
    status: str
    model_name: str
    model_loaded: bool
    index_loaded: bool
    total_indexed_images: int
