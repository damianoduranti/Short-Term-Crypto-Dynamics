# SHORT TERM CRYPTO DYNAMICS
## *Project for Big Data Technologies 2022*
___

This project has been developed for the Big Data Technologies course of the University of Trento. 
The project objective refers to developing a Big Data system for supporting crypto investors by predicting the short-term dynamics of Bitcoin and other crypto assets. 

## Data sources

Data about Crypto market is obtained through [Binance API](https://binance.com).

## Prerequisites 

In order to be run, the project requires [Docker Desktop](https://www.docker.com/) or [Docker Compose](https://docs.docker.com/compose/install/).

This project uses the following Docker images: 

-   [wurstmeister/Zookeeper](https://hub.docker.com/r/wurstmeister/zookeeper)

-	[wurstmeister/Kafka](https://hub.docker.com/r/wurstmeister/kafka)

-   [Kafka-UI](https://hub.docker.com/r/provectuslabs/kafka-ui)

## Usage

### Clone the repository 

Clone the repository locally with the command: 

```
git clone https://github.com/damianoduranti/BDT-Project.git
```

### Activate Docker images 

Move to the folder and run:
```
docker-compose up
```
    

### Access services 

Some points of the pipeline can be accessed at the following addresses:

-	**Kafka-UI**: [http://localhost:8080](http://localhost:8080/) shows the topics and the messages shared through them.

-	**Dashboard**: [http://localhost:8501](http://localhost:8501/) shows the short term predictions for the different coins.

## Overall code structure
```
├── src
│   ├── consumer.py
│   ├── producer.py
│   ├── model_fit.py
│   ├── requirements.txt
│   └── dashboard
│   	  ├── dashboard.py
│   	  └── Dockerfile
│ 
├── docker-compose.yml
└── Dockerfile
```

## Notes
- When the data producer has been inactive for some time, the app has the capabilities to recover the missing data and fill the dataset to have a complete history. This may need some time at the first run to correctly display the plots and the predictions.
- During execution, you may encounter some issues related to the connection to Postgres services. These problems may be due to your connection limitations.
- The coins analyzed are chosen in the docker-compose.yml as an envirorment variable for each of the different containers. The string is editable. However, the system is not meant to change the displayed coins very often, as this will need additional time to recover past data for these.
- If you encounter errors while executing the Dockerfile, you should consider cleaning all the unused/dangling images.
