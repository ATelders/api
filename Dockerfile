FROM python:3.8
EXPOSE 8000
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["uvicorn", "app.main:app", "--reload"]