#!/bin/bash

# Создаем необходимые папки
mkdir -p ./ml_monitoring_services/pg_ml
mkdir -p ./ml_monitoring_services/pg_grafana 
mkdir -p./ml_monitoring_services/grafana

# Запускаем docker-compose
docker-compose -p ml_services_diploma up -d
