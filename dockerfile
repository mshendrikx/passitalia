# Use a Debian ARM64 base image with Python 3.12 (Bookworm)
FROM python:3.12-slim-bookworm

# Set environment variable for non-interactive apt-get installs
ENV DEBIAN_FRONTEND=noninteractive

# Update apt-get and install Chromium and its dependencies
# The list of dependencies is generally stable, but can be adjusted if needed.
RUN apt-get update && apt-get install -y  \
    apt-transport-https \
    nano \
    curl \
    cron \
    wget \
    unzip \
    ca-certificates \
    fonts-liberation \
    libappindicator3-1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libc6 \
    libcairo2 \
    libcups2 \
    libdbus-1-3 \
    libexpat1 \
    libfontconfig1 \
    libgbm1 \
    libgcc1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    libxrender1 \
    lsb-release \
    xdg-utils \
    xvfb \
    chromium \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Set environment variables for Chromium inside the virtual display
# DISPLAY=:99 is for the virtual display server.
# CHROME_BIN points to the Chromium executable.
ENV DISPLAY=:99
ENV CHROME_BIN=/usr/bin/chromium
ENV BROWSER_HEADLESS=false
ENV TZ=America/Sao_Paulo

WORKDIR /app

RUN mkdir logs

COPY requirements.txt .

RUN pip3 install --upgrade pip

RUN pip3 install -r requirements.txt

COPY . .

# Expose port 5000 for web traffic
EXPOSE 5000

# Start the virtual display and Python app in the foreground
CMD ["sh", "-c", "Xvfb :99 -screen 0 1920x1080x24 -nolisten tcp & exec python3 /app/scrypt_nodrive.py"]
