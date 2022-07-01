FROM python:3.8-slim
WORKDIR /
COPY . .
ADD src/requirements.txt .
ADD data/symbols.json .
RUN apt-get update -y && apt-get install -y gcc
RUN pip install -r requirements.txt

CMD python -u $SCRIPT