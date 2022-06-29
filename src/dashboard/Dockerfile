FROM python:3.8-slim
WORKDIR /
COPY . .
ADD src/requirements.txt .
ADD src/utils/crypto_classes.py .
RUN pip install -r requirements.txt
CMD python -u $SCRIPT