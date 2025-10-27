# ☁️ MiniCloud – Dockerized Cloud Management Platform  

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg?logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Framework-green.svg?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg?logo=docker)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Build Status](https://img.shields.io/badge/Build-Passing-brightgreen.svg)](#)
[![Made with ❤️ by Aryan](https://img.shields.io/badge/Made%20with-%E2%9D%A4-red.svg)]([https://www.linkedin.com/in/aryan-srivastava-605b3a220/)])

> A lightweight cloud platform that simulates **AWS EC2 + S3** functionality using **FastAPI**, **Docker**, and **MinIO**.  
> Users can spin up containerized instances, upload/download files, and manage resources through REST APIs — all locally.

---

## 🚀 Features  

- 🖥️ **Compute Orchestration** – Launch and manage containerized services (like `nginx`, `redis`) via API.  
- 🗂️ **Object Storage (S3-like)** – Upload, list, and download files securely with presigned URLs.  
- ⚙️ **Control-Plane + Agent Architecture** – Simulates AWS’s separation between orchestration and execution layers.  
- 💾 **Persistent Storage** – Uses Docker volumes for state retention (SQLite DB + MinIO data).  
- 🩺 **Health Monitoring** – Built-in `/health/` and `/files/ping` endpoints for system checks.  
- 🐳 **Fully Containerized** – All services managed with Docker Compose for simplicity and modularity.  

---

## 🧩 Tech Stack  

| Layer | Tools |
|-------|--------|
| **Backend Framework** | FastAPI (Python 3.11) |
| **Storage** | SQLite |
| **Object Storage** | MinIO (S3-compatible) |
| **Containerization** | Docker · Docker Compose |
| **APIs** | REST (Swagger UI at `/docs`) |
| **SDK** | Boto3 (AWS SDK for Python) |

---

## 🏗️ Architecture  
+—————————+
|Control Plane|  ← FastAPI
|—————————|
| /instances | /files API  |
| SQLite DB  | MinIO client|
+—————————+
|
↓
+—————————+
| Agent Node|  ← Executes container commands
| (docker run / stop tasks) |
+—————————+
|
↓
+—————————+
| MinIO Server|  ← S3-compatible object storage
| (uploads, downloads)|
+—————————+


---

## ⚙️ Setup  

### 1️⃣ Prerequisites  
- Docker Desktop (running)  
- Python (optional, for API tests)  
- cURL or Postman  

---

### 2️⃣ Clone & Build  

```bash
git clone https://github.com/aryan-mini/MiniCloud.git
cd MiniCloud
docker compose build


### Run the Stack
docker compose up -d

### Test File Upload
echo "hello cloud" > hello.txt
curl -F "file=@hello.txt" http://localhost:8000/files/upload/

###List File
curl http://localhost:8000/files/list/

MiniCloud/
├── control_plane/
│   ├── Dockerfile
│   ├── main.py
│   ├── db.py
│   └── routes/
│       ├── instances.py
│       ├── files.py
│       ├── health.py
│       └── agents.py
├── agent/
│   ├── Dockerfile
│   └── main.py
├── docker-compose.yml
├── requirements.txt
└── README.md



###Useful Commands
docker compose logs -f control-plane   # View live logs
docker compose restart control-plane   # Restart only control-plane
docker compose down                    # Stop everything
