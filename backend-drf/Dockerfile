FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN  pip install --no-cache-dir -r requirements.txt

COPY . .

#wsgi.py
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clickmart_main.settings')
# --> clickmart_main

CMD ["gunicorn", "clickmart_main.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "180"]
#gunicorn is our production or application server where... 
# clickmart_main.wsgi:application is our Django entry point 
# --bind 0.0.0.0:8000 to allow the external traffic 
# --workers 3 => 3 djnago instances in parallel
# --timeout 180 => try for 180 seconds ? 

# gunicorn clickmart_main.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 180