FROM python:3.9-slim
WORKDIR /
COPY . .
ADD src/requirements.txt .
RUN apt-get update -y && apt-get install -y gcc
RUN pip install -r requirements.txt
CMD python -u $SCRIPT