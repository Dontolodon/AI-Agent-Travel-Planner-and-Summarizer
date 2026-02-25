# AI Travel Operations Agent (Local LLM + Tools + PDF Export)

**Name:** Dennis Ing (應添利)  
**Project:** AI Travel Operations Agent (CLI + Localhost Web UI)  
**Runtime:** Podman containers (App + Ollama), persistent disk output via volume mounts

This project is a terminal + localhost-based AI agent for travel planning and travel document summarization.  
It runs inside a Podman container and uses **Ollama (local LLM)** + **tool calls** (OCR / PDF parsing / city geocoding / Google Places).

---

## Features

1) **Summarize Mode**
- Upload a **PDF booking** or **ticket screenshot**
- Extract text via:
  - PDF parsing (`pdfminer`)
  - OCR (`tesseract`) including **Traditional Chinese (chi_tra)** and English
- Produce a clean summary (no guessing)

2) **Plan Trip Mode**
- Input: destination city, start date, number of days, user name, preferences (“vibe”)
- Tools used:
  - City geocoding API (Open-Meteo geocoding)
  - Season/climate profile reasoning (based on latitude + country)
  - Google Places Text Search (real attractions)
- Output: Day-by-day itinerary (Day 1..Day N) with Morning/Afternoon/Evening
- Saves per-user trip history to disk: `data/history_trip.json`

3) **Export PDF (Bonus)**
- Export itinerary to PDF using ReportLab
- Includes up to 6 place photos from Google Places Photos (when available)
- Output stored on disk: `exports/itineraries/*.pdf`

4) **Email (Optional)**
- Send itinerary/summary via SMTP (requires `.env` configuration)
- If PDF export is enabled, can email the PDF as attachment

---

This project **does NOT implement embedding-based RAG** and **does NOT use a vector database**.  
It is tool-augmented using:
- Google Places results (cached to disk)
- City info + season profile
- User trip history JSON retrieval (`data/history_trip.json`)

---

## Quick Start (Podman + Ollama)

> Full step-by-step instructions and screenshots checklist are in `RUNME.md`.

### 1) Build image
```bash
podman build -t ai-travel-agent -f Containerfile .
