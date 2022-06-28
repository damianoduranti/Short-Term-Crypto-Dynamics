FROM python:3.8-slim
WORKDIR /
COPY . .
ADD src/requirements.txt .
RUN pip install -r requirements.txt
CMD python -u $SCRIPT