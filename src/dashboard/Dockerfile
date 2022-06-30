FROM python:3.8-slim
WORKDIR /
COPY . .
ADD src/requirements.txt .
RUN apt-get update -y && apt-get install -y gcc
RUN pip install -r requirements.txt

EXPOSE 8501

ENTRYPOINT ["streamlit", "run"]
CMD ["src/dashboard/dashboard.py"]