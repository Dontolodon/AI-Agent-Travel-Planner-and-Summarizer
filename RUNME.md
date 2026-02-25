# AI Travel Operations Agent — Podman Execution Guide (RUNME)

**Name:** Dennis Ing (應添利)  
**Environment Used:** WSL Ubuntu 20.04.6 + Podman  
**Containers:**  
- `ai-travel-agent` (Flask Web App)  
- `ollama` (Local LLM server)

Both containers must be on the same Podman network so that hostname `ollama` resolves correctly.

---

# 0) System Requirements

- WSL Ubuntu 20.04.6
- Podman installed
- Internet access (for pulling images and Google Places API)
- Google Places API key (for real attraction + photo retrieval)
- SMTP credentials (optional, for email feature)

Check environment:

```bash
uname -a
cat /etc/os-release
podman --version
```

# 1) Create Podman Network (One-Time)

```bash
podman network create ai-net || true
```

# 2) Build Application Container

```bash
podman build -t ai-travel-agent -f Containerfile .
```

# 3) Run Ollama Container

```bash
podman rm -f ollama || true

podman run -d \
  --name ollama \
  --network ai-net \
  -p 11434:11434 \
  -v ollama_models:/root/.ollama \
  docker.io/ollama/ollama:latest
```

This is for pulling the model (One-Time)

```bash
podman exec -it ollama ollama pull mistral
```

# 4) Run Travel Agent Container (Persistent Disk Mount)
Create directories needed on host:

```bash
mkdir -p data exports logs
```

Run Container:

```bash
podman rm -f travel-agent || true

podman run -d \
  --name travel-agent \
  --network ai-net \
  -p 5000:5000 \
  -v ./data:/app/data \
  -v ./exports:/app/exports \
  ai-travel-agent
```

Verify Both Container"

```bash
podman ps
```

# 5) Access Web UI
This is a very simple Web UI made by me in order to create this project.

On Browsers:

```bash
http://localhost:5000
```

# 6) CLI Usage
This means that you can use this in your WSL command prompt.

To generate itinerary:

```bash
podman exec -it travel-agent python agent.py plan \
  --city "Osaka, Japan" \
  --start 2025-12-31 \
  --days 5 \
  --user "Dontol" \
  --vibe "food, anime, chill pace" \
  --fast
```

To export it to PDF:

```bash
podman exec -it travel-agent python agent.py export-pdf \
  --city "Osaka, Japan" \
  --start 2025-12-31 \
  --days 5 \
  --user "Geoffrey" \
  --vibe "food, anime, chill pace"
```

The PDF output will be stored on host's device in (exports/itineraries/)
