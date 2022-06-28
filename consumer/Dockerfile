FROM python:3.8-slim
WORKDIR /
COPY . .
RUN pip install kafka-python==2.0.2
RUN pip install pandas
RUN pip install requests
RUN pip install psycopg2-binary
CMD python -u $SCRIPT