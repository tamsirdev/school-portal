FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf-xlib-2.0-0 \
    libffi-dev shared-mime-info && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN groupadd -r app && useradd -r -g app -d /app app && chown -R app:app /app
USER app

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "--access-logfile", "-", "manage:app"]
