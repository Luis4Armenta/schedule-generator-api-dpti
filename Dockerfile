FROM python:3.9-slim

ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Instalamos dependencias necesarias para Firefox (navegación headless)
RUN apt-get update \
	&& apt-get install -y --no-install-recommends firefox-esr ca-certificates wget tar \
	&& wget -q https://github.com/mozilla/geckodriver/releases/download/v0.36.0/geckodriver-v0.36.0-linux64.tar.gz \
	&& tar -xzf geckodriver-v0.36.0-linux64.tar.gz \
	&& mv geckodriver /usr/local/bin/ \
	&& chmod +x /usr/local/bin/geckodriver \
	&& rm geckodriver-v0.36.0-linux64.tar.gz \
	&& rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . .

EXPOSE 3000

# Variables para ejecución headless opcional (Selenium ya activa headless vía Options)
ENV MOZ_HEADLESS=1

CMD ["gunicorn", "-c", "gunicorn.conf.py", "main:app"]
