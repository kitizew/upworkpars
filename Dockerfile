FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
      wget ca-certificates fonts-liberation xvfb xauth x11vnc novnc websockify fluxbox \
    && wget -q -O /tmp/chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt-get install -y /tmp/chrome.deb \
    && rm /tmp/chrome.deb && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
