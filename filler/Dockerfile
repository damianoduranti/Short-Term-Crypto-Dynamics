FROM python:3.10-slim
WORKDIR /
COPY . .
RUN pip install pandas
RUN pip install requests
RUN pip install psycopg2-binary
CMD python -u $SCRIPT