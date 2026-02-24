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