FROM python:3.12.3-slim
WORKDIR /usr/src/app
COPY requirements.txt .
RUN python -m pip install -r requirements.txt
RUN python -m pip install psycopg[binary]
COPY . .
RUN chmod +x start.sh
EXPOSE 5000
CMD ["./start.sh"]