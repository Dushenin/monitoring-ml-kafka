## Запуск всех сервисов разом:

Открой терминал и запусти:
```
docker-compose -p ml_services_diploma up -d
```
Далее на локалхост 3111 переходи и работай с графаной. Сайт для загрузки фоток будет на порту 8501

---

### Если хочешь тесты руками делать то подними все сервисы кроме трех бекендов и тестируй через отдельное 3.10 окружение со всеми нужными библиотеками:
Создай окружение в питона и далее в него установи библиотеки:
```
pip install -r requirements.txt
```

---

PS для графаны подключение:
pg_ml:5432 - подключение к Grafana для постграсу
http://host.docker.internal:9090 - подключение к Grafana для прометеуса