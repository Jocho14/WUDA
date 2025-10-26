FROM python:3.11-slim AS runtime

WORKDIR /app

COPY requirements.txt ./

RUN pip install --upgrade --no-cache-dir pip \
	&& pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python3", "app.py"]