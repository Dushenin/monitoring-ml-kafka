import time
import logging
import psycopg2

logger = logging.getLogger(__name__)

class SentInfoPersonDBNode:
    """Модуль для отправки актуальной информации о трафике в базу данных"""

    def __init__(self, config: dict) -> None:
        config_db = config["sent_info_db_node"]
        self.last_db_update = time.time()
        self.last_id = 0

        # Параметры подключения к базе данных
        db_connection = config_db["connection_info"]
        conn_params = {
            "user": db_connection["user"],
            "password": db_connection["password"],
            "host": db_connection["host"],
            "port": str(db_connection["port"]),
            "database": db_connection["database"],
        }

        # Подключение к базе данных
        try:
            self.connection = psycopg2.connect(**conn_params)
            print("Connected to PostgreSQL")
        except (Exception, psycopg2.Error) as error:
            print("Error while connecting to PostgreSQL:", error)

        # Создание курсора для выполнения SQL-запросов
        self.cursor = self.connection.cursor()

        # SQL-запрос для удаления таблицы, если она уже существует
        drop_table_query = f"DROP TABLE IF EXISTS total_results;"

        # Удаление таблицы, если она уже существует
        try:
            self.cursor.execute(drop_table_query)
            self.connection.commit()
        except (Exception, psycopg2.Error) as error:
            logger.error(
                f"Error while dropping table:: {error}"
            ) 

        # SQL-запрос для создания таблицы
        create_table_query = f"""
        CREATE TABLE "total_results"(
            "id" BIGINT NOT NULL,
            "task_id" UUID NOT NULL,
            "human_check" BOOLEAN NOT NULL,
            "update_date" TIMESTAMP(0) WITH
                TIME zone NOT NULL
        );
        """
        create_index_query = f"""
        ALTER TABLE
            "total_results" ADD PRIMARY KEY("id");
        """

        # Создание таблицы
        try:
            self.cursor.execute(create_table_query)
            self.connection.commit()
            logger.info(
                f"Table total_results created successfully"
            ) 
        except (Exception, psycopg2.Error) as error:
            logger.error(
                f"Error while creating table: {error}"
            )   

        # Создание индекса таблицы
        try:
            self.cursor.execute(create_index_query)
            self.connection.commit()
            logger.info(
                f"Index to total_results created successfully"
            ) 
        except (Exception, psycopg2.Error) as error:
            logger.error(
                f"Error while creating index: {error}"
            ) 


    def insert_data(self, data : dict) -> None:
        
        # Получение значений для записи в бд новой строки:
        task_id = data['taskId']
        timestamp = data['timestamp']
        check_human = data['checkHuman']
        id = self.last_id

        self._insert_in_db(id, task_id, timestamp, check_human) # добавим датку
        self.last_db_update = time.time()  # Обновление времени последнего обновления базы данных
        self.last_id += 1


    def _insert_in_db(self, id, task_id, timestamp, check_human) -> None:
        # Формирование и выполнение SQL-запроса для вставки данных в бд
        insert_query = (
            f"INSERT INTO total_results"
            "(id, task_id, human_check, update_date) "
            "VALUES (%s, %s, %s, to_timestamp(%s));"
        )
        try:
            self.cursor.execute(
                insert_query,
                (   
                    id,
                    task_id,
                    check_human,
                    timestamp,
                )
            )
            self.connection.commit()
            logger.info(
                f"Successfully inserted data into PostgreSQL"
            )   
        except (Exception, psycopg2.Error) as error:
            logger.error(
                f"Error while inserting data into PostgreSQL: {error}"
            )   