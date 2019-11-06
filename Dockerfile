FROM python:3.8

WORKDIR /app/src

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/data
RUN useradd -m -u 7000 springerwatch
RUN chown springerwatch /app/data
USER springerwatch

CMD [ "python", "./springerwatch.py" ]
