#!/bin/bash

# Создаем необходимые папки
mkdir -p ./ml_monitoring_services/pg_ml
mkdir -p ./ml_monitoring_services/pg_grafana 
mkdir -p ./ml_monitoring_services/grafana
mkdir -p ./ml_monitoring_services/s3_storage
mkdir -p ./ml_monitoring_services/prometheus

# Запускаем docker-compose
docker-compose -p ml_services_diploma up -d
