# Quasimodo

This Python (FastAPI) application serves as the API for an IoT smart doorbell. Currently, it only receives video and audio streams via WebSocket.

---

## Table of Contents

1. [Description](#description)  
2. [Features](#features)  
3. [Prerequisites](#prerequisites)  
4. [Installation](#installation)  
6. [Running the Server](#running-the-server)  
7. [WebSocket Endpoints](#websocket-endpoints)  

---

## Description

This FastAPI application receives, processes, and broadcasts in real time the video and audio streams from a smart IoT doorbell. For now, it maintains two WebSocket connections (one for video, one for audio) to receive data from the device.

---

## Features

- **WebSocket Video Reception**  
- **WebSocket Audio Reception**  

---

## Prerequisites

- **Python 3.8+**  
- **pip** (or equivalent)  
- (Optional) A virtual environment tool (venv, virtualenv, conda, etc.)  

---

## Installation

1. **Clone the repository**  
   ```bash
   git clone https://github.com/ZK1569/quasimodo.git
   cd iot-doorbell-api
   ```
2. **Create and activate a virtual env**
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```
3. **Install dependencies**
  ```bash
  pip install -r requirements.txt
  ``` 

## Running the Server

Once dependencies are installed, start the API:
```bash
python3 main.py
```

## WebSocket Endpoints 

The API exposes two WebSocket endpoints to receive streams from the doorbell:
1. **Video Stream**
  - url : `ws://0.0.0.0:8080/v1/bell/ws/video`

2. **Audio Stream**
  - url : `ws://0.0.0.0:8080/v1/bell/ws/audio`
