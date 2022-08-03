# centiment-data-pipeline

Centiment is a cryptocurrency monitoring platform offering market sentiment information formed based on tweets from Twitter.

The pipeline utilizes Twitter streaming API processing tweets by scoring its sentiment using VADER. The sentiment scores from the tweets will then be stored to influxdb and served to the dashboard.

The main goal of the project is to build a data pipeline that process data continously providing most recent and historical market sentiment.

![Laptop Preview](/docs/laptop-preview.png)

The dashboard offers widgets such as:

![Dashboard Preview](/docs/widgets.png)

### High Level Architecture

![High level architecture](/docs/high-level-architecture.png)