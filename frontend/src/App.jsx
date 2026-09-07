import React, { useState, useEffect, useRef } from 'react'
import './App.css'

// Environment configurations from .env (prefixed with VITE_)
const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '')
const PDKI_URL = import.meta.env.VITE_PDKI_URL || 'https://pdki-indonesia.dgip.go.id'
const MAX_UPLOAD_MB = Number(import.meta.env.VITE_MAX_UPLOAD_SIZE_MB) || 5

export default function App() {
  const [selectedFile, setSelectedFile] = useState(null)
  const [previewUrl, setPreviewUrl] = useState(null)
  const [fileMeta, setFileMeta] = useState(null)
  const [selectedCategory, setSelectedCategory] = useState('semua')
  const [isDragging, setIsDragging] = useState(false)
  
  const [isLoading, setIsLoading] = useState(false)
  const [loadingStep, setLoadingStep] = useState(1)
  const [errorMessage, setErrorMessage] = useState(null)
  
  const [checkResult, setCheckResult] = useState(null)
  const [displayScore, setDisplayScore] = useState(0)
  const [systemHealth, setSystemHealth] = useState({ online: true, totalIndexed: 12 })
  
  const fileInputRef = useRef(null)

  // Polling status backend secara berkala agar otomatis terhubung saat model selesai dimuat
  useEffect(() => {
    let isMounted = true

    const checkHealth = async () => {
      try {
        const res = await fetch(`${API_BASE_URL}/api/health`)
        if (!res.ok) throw new Error('Backend offline')
        const data = await res.json()
        if (isMounted) {
          setSystemHealth({
            online: data.status === 'healthy',
            totalIndexed: data.total_indexed_images || 200,
          })
        }
      } catch {
        if (isMounted) {
          setSystemHealth({ online: false, totalIndexed: 0 })
        }
      }
    }

    checkHealth()
    const timer = setInterval(checkHealth, 4000)

    return () => {
      isMounted = false
      clearInterval(timer)
    }
  }, [])

  // Score Count-Up Animation (PRD Section 8.1 Motion: 0 -> final score)
  useEffect(() => {
    if (!checkResult) return

    const targetScore = checkResult.max_similarity_score
    const durationMs = 700
    const frameRateMs = 25
    const totalSteps = durationMs / frameRateMs
    const increment = targetScore / totalSteps
    let current = 0

    const timer = setInterval(() => {
      current += increment
      if (current >= targetScore) {
        setDisplayScore(targetScore)
        clearInterval(timer)
      } else {
        setDisplayScore(parseFloat(current.toFixed(1)))
      }
    }, frameRateMs)

    return () => clearInterval(timer)
  }, [checkResult])

  // Handle file selection and local preview
  const handleFile = (file) => {
    setErrorMessage(null)

    if (!file) return

    // Validasi tipe format file (JPEG, PNG, WEBP)
    const validTypes = ['image/jpeg', 'image/png', 'image/webp']
    if (!validTypes.includes(file.type)) {
      setErrorMessage('Format file tidak didukung. Harap gunakan format JPEG, PNG, atau WEBP.')
      return
    }

    // Validasi ukuran maksimal (PRD Section 6 & .env VITE_MAX_UPLOAD_SIZE_MB)
    const maxSizeBytes = MAX_UPLOAD_MB * 1024 * 1024
    if (file.size > maxSizeBytes) {
      setErrorMessage(`Ukuran file (${(file.size / (1024 * 1024)).toFixed(2)} MB) melebihi batas maksimal ${MAX_UPLOAD_MB} MB.`)
      return
    }

    setSelectedFile(file)
    setFileMeta({
      name: file.name,
      sizeKb: Math.round(file.size / 1024),
    })

    const objectUrl = URL.createObjectURL(file)
    setPreviewUrl(objectUrl)
  }

  const onInputChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0])
    }
  }

  const handleDragOver = (e) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = () => {
    setIsDragging(false)
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setIsDragging(false)
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0])
    }
  }

  const clearSelection = (e) => {
    e.stopPropagation()
    setSelectedFile(null)
    setPreviewUrl(null)
    setFileMeta(null)
    setErrorMessage(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  // Submit to POST /api/check
  const handleCheck = async () => {
    if (!selectedFile) return

    setIsLoading(true)
    setErrorMessage(null)
    setLoadingStep(1)

    // Simulate honest progress updates
    const step2Timer = setTimeout(() => setLoadingStep(2), 250)
    const step3Timer = setTimeout(() => setLoadingStep(3), 600)

    try {
      const formData = new FormData()
      formData.append('file', selectedFile)
      if (selectedCategory && selectedCategory !== 'semua') {
        formData.append('category', selectedCategory)
      }

      const response = await fetch(`${API_BASE_URL}/api/check`, {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        if (response.status === 502) {
          throw new Error('Server backend (port 8000) sedang memuat model AI atau belum siap menerima request (HTTP 502 Bad Gateway). Harap tunggu beberapa detik lalu tekan Cek Sekarang kembali.')
        }
        const errData = await response.json().catch(() => ({}))
        throw new Error(errData.detail || `Terjadi kesalahan pada server (HTTP ${response.status})`)
      }

      const data = await response.json()
      setCheckResult(data)
    } catch (err) {
      setErrorMessage(err.message || 'Gagal menghubungi server.')
    } finally {
      clearTimeout(step2Timer)
      clearTimeout(step3Timer)
      setIsLoading(false)
    }
  }

  // Helper untuk styling skor risiko (PRD 8.1: Indigo -> Amber -> Ink)
  const getRiskClass = (score) => {
    if (score >= 75.0) return 'high-risk'
    if (score >= 50.0) return 'medium-risk'
    return 'low-risk'
  }

  // Helper untuk resolve URL gambar statis dari backend saat deploy di Vercel
  const resolveImageUrl = (url) => {
    if (!url) return ''
    if (url.startsWith('http://') || url.startsWith('https://')) return url
    return `${API_BASE_URL}${url}`
  }

  return (
    <div className="app-wrapper">
      {/* Masthead Header */}
      <header className="masthead">
        <div className="brand-block">
          <span className="brand-title">Tarum</span>
          <span className="brand-tagline">Instrumen verifikasi kemiripan visual kriya & fashion</span>
        </div>
        <div className="system-status">
          <span className={`status-dot ${systemHealth.online ? '' : 'offline'}`}></span>
          <span>
            {systemHealth.online
              ? `FAISS: ${systemHealth.totalIndexed} motif diindeks`
              : 'Backend sedang memuat model / terputus'}
          </span>
        </div>
      </header>

      {/* Main Asymmetric Split: 40% Upload | 60% Results */}
      <main className="split-layout">
        {/* PANEL KIRI (40%): Upload & Kontrol Input */}
        <section className="panel-upload" aria-label="Upload Desain">
          <div className="panel-header">
            <h1 className="panel-heading">Upload Desain</h1>
            <p className="panel-subheading">
              Pilih foto motif atau produk fisik dalam format JPEG/PNG (maksimal 5 MB).
            </p>
          </div>

          {/* Drag and Drop Zone */}
          <div
            className={`drop-zone ${isDragging ? 'dragging' : ''}`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => !previewUrl && fileInputRef.current?.click()}
            tabIndex={0}
            role="button"
            aria-label="Area unggah file gambar"
          >
            <input
              type="file"
              ref={fileInputRef}
              className="file-input-hidden"
              accept=".jpg,.jpeg,.png,.webp"
              onChange={onInputChange}
            />

            {previewUrl ? (
              <div className="preview-container">
                <img src={previewUrl} alt="Preview desain yang diunggah" className="preview-image" />
                <div className="preview-metadata">
                  <span>{fileMeta?.name}</span>
                  <span>{fileMeta?.sizeKb} KB</span>
                </div>
                <button
                  type="button"
                  className="change-photo-btn"
                  onClick={clearSelection}
                >
                  Ganti foto
                </button>
              </div>
            ) : (
              <div className="drop-prompt">
                <svg
                  className="drop-icon"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  aria-hidden="true"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5"
                  />
                </svg>
                <span className="drop-title">Tarik & lepas foto desain di sini, atau klik untuk memilih file</span>
                <span className="drop-hint">Mendukung JPEG, PNG, WEBP hingga 5 MB</span>
              </div>
            )}
          </div>

          {/* Kategori Dropdown */}
          <div className="form-group">
            <label htmlFor="kategori-select" className="form-label">
              Kategori Produk (Opsional)
            </label>
            <select
              id="kategori-select"
              className="select-category"
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
            >
              <option value="semua">Semua Motif Batik (2.599 Gambar — MVP)</option>
              <option value="parang">Batik Parang (Yogyakarta & Solo)</option>
              <option value="kawung">Batik Kawung</option>
              <option value="megamendung">Batik Megamendung (Cirebon)</option>
              <option value="bali">Batik Bali (Barong & Merak)</option>
              <option value="papua">Batik Papua (Asmat & Cendrawasih)</option>
              <option value="tenun" disabled>Tenun Ikat & Songket (Roadmap V1)</option>
              <option value="anyaman" disabled>Anyaman Bambu & Rotan (Roadmap V1)</option>
              <option value="kerajinan" disabled>Kerajinan Kayu & Logam (Roadmap V1)</option>
              <option value="fashion" disabled>Fashion & Kulit (Roadmap V1)</option>
            </select>
          </div>

          {/* Error Message */}
          {errorMessage && (
            <div className="error-banner" role="alert">
              {errorMessage}
            </div>
          )}

          {/* Action Button - PRD: Solid Indigo Tarum, no arrow icon */}
          <button
            type="button"
            className="btn-submit"
            onClick={handleCheck}
            disabled={!selectedFile || isLoading}
          >
            {isLoading ? 'Sedang Memeriksa...' : 'Cek Sekarang'}
          </button>

          {/* Disclaimer Wajib (PRD Section 8.1 & 8.2) - Selalu Terlihat, Non-Dismissible */}
          <footer className="disclaimer-box">
            <div className="disclaimer-title">Pernyataan Hukum</div>
            <p className="disclaimer-text">
              Ini bukan opini hukum. Hasil ini membantu kamu memutuskan langkah berikutnya, bukan menggantikan konsultasi HKI resmi.
            </p>
            <a
              href={PDKI_URL}
              target="_blank"
              rel="noopener noreferrer"
              className="disclaimer-link"
            >
              Kunjungi Pangkalan Data Kekayaan Intelektual (PDKI Resmi)
            </a>
          </footer>
        </section>

        {/* PANEL KANAN (60%): Hasil Pengecekan & Pembanding */}
        <section className="panel-results" aria-label="Hasil Pengecekan">
          <div className="results-header-row">
            <div>
              <h2 className="results-header-title">Hasil Pengecekan</h2>
              <p className="results-header-sub">
                {checkResult
                  ? `Pemeriksaan selesai dalam ${checkResult.execution_time_ms} ms`
                  : 'Perbandingan visual terhadap dataset referensi budaya'}
              </p>
            </div>

            {/* Skor Besar di Kanan Atas (Font Mono) - Wireframe Section 8.1 */}
            {checkResult && (
              <div className="score-hero-container">
                <span className={`score-hero-number ${getRiskClass(checkResult.max_similarity_score)}`}>
                  {displayScore.toFixed(1)}%
                </span>
                <span className={`risk-badge ${getRiskClass(checkResult.max_similarity_score)}`}>
                  {checkResult.risk_level}
                </span>
              </div>
            )}
          </div>

          {/* Loading State: Honest Progressive Feedback */}
          {isLoading && (
            <div className="loading-container">
              <div className="loading-title">Memproses gambar desain...</div>
              <div className="loading-steps">
                <div className={`loading-step-item ${loadingStep >= 1 ? 'active' : ''}`}>
                  <span className="step-indicator"></span>
                  <span>1. Membaca dan validasi resolusi gambar</span>
                </div>
                <div className={`loading-step-item ${loadingStep >= 2 ? 'active' : ''}`}>
                  <span className="step-indicator"></span>
                  <span>2. Ekstraksi visual embedding CLIP ViT-B/32 (512 dimensi)</span>
                </div>
                <div className={`loading-step-item ${loadingStep >= 3 ? 'active' : ''}`}>
                  <span className="step-indicator"></span>
                  <span>3. Pencarian tetangga terdekat pada indeks FAISS</span>
                </div>
              </div>
            </div>
          )}

          {/* Empty State: Belum Ada Upload */}
          {!isLoading && !checkResult && (
            <div className="empty-state">
              <div className="empty-state-canvas">
                <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <path d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              </div>
              <div className="empty-state-title">Belum ada desain yang diperiksa</div>
              <p className="empty-state-desc">
                Unggah foto rancangan motif batik atau produk kriya di panel sebelah kiri lalu tekan tombol <strong>Cek Sekarang</strong> untuk melihat skor kemiripan visual dan perbandingan terhadap dataset 2.599 motif Batik Indonesia.
              </p>
            </div>
          )}

          {/* Active Result State */}
          {!isLoading && checkResult && (
            <div>
              {/* User-Perspective Summary Statement */}
              <div className="result-summary-box">
                <p className="user-perspective-statement">
                  Desainmu {checkResult.max_similarity_score}% mirip dengan karya dalam database referensi.
                </p>
                <p className="recommendation-text">
                  <strong>Rekomendasi: </strong>
                  {checkResult.recommendation}
                </p>
                <div className="latency-meta">
                  File: {checkResult.query.filename} • Ukuran: {Math.round(checkResult.query.size_bytes / 1024)} KB • Waktu Komputasi: {checkResult.execution_time_ms} ms
                </div>
              </div>

              {/* Comparison Section (Top-5 Hasil Pembanding) */}
              <div className="comparison-section-title">
                5 Karya Pembanding Paling Mirip
              </div>

              <div className="comparison-list">
                {checkResult.results.map((item) => (
                  <div key={item.id} className="comparison-card" tabIndex={0}>
                    <div className="thumb-wrapper">
                      <img
                        src={resolveImageUrl(item.image_url)}
                        alt={item.title || item.filename}
                        className="thumb-image"
                        onError={(e) => {
                          // Fallback jika thumbnail statis tidak termuat
                          e.target.style.display = 'none'
                        }}
                      />
                    </div>
                    <div className="item-details">
                      <div className="item-header">
                        <span className="item-title">
                          #{item.rank} {item.title || item.filename}
                        </span>
                        <span className={`item-score ${getRiskClass(item.similarity_score)}`}>
                          {item.similarity_score}%
                        </span>
                      </div>
                      <div className="item-meta">
                        <span className="item-category">[{item.category.toUpperCase()}]</span>
                        {item.metadata?.motif && (
                          <>
                            <span>•</span>
                            <span>Motif: {item.metadata.motif}</span>
                          </>
                        )}
                        <span>•</span>
                        <span>Status: {item.risk_level}</span>
                      </div>
                      {item.metadata?.source && (
                        <div className="item-source-tag">
                          Sumber: {item.metadata.source} ({item.metadata.license_notice || 'Riset non-komersial'})
                        </div>
                      )}
                      {item.metadata?.description && (
                        <p className="item-description">{item.metadata.description}</p>
                      )}
                    </div>
                  </div>
                ))}
              </div>

              {/* Actionable Next Steps Card */}
              <div className="next-steps-card">
                <div className="next-steps-text">
                  <strong>Langkah selanjutnya: </strong>
                  {checkResult.max_similarity_score >= 75.0
                    ? 'Lakukan revisi elemen visual motif yang memiliki kemiripan sebelum diproduksi massal.'
                    : checkResult.max_similarity_score >= 50.0
                    ? 'Tinjau kembali bagian pola tertentu untuk memperbesar diferensiasi karya Anda.'
                    : 'Karya memiliki orisinalitas visual tinggi. Anda siap mendaftarkan Desain Industri ke DJKI.'}
                </div>
                <a
                  href={PDKI_URL}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="pdki-link-btn"
                >
                  Buka Portal PDKI
                </a>
              </div>
            </div>
          )}
        </section>
      </main>
    </div>
  )
}
