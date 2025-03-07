# Prometheus Exporter

## Dev

pip install -r ./requirements

## Using Docker

```bash

docker build -t prometheus-exporter .
docker run -p 5000:5000 -p 8022:8022 prometheus-exporter

```

8022 是 prometheus pull 的端口
5000 是 data_buried_point API 使用的端口

## API Test

```bash

curl --location 'http://localhost:5000/data_buried_point' \
--header 'Content-Type: application/json' \
--data '{
    "name" : "test_buried_point_2",
    "doc" : "test_buried_point_2_doc"
}'

```

## About the prometheus counter

The name of the counter must be unique and valid java identifier.
