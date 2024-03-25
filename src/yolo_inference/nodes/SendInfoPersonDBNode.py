import time
import logging
import psycopg2

logger = logging.getLogger(__name__)

class SendInfoPersonDBNode:
    """Модуль для отправки актуальной информации о трафике в базу данных"""

    def __init__(self, config: dict) -> None:
        config_db = config["send_info_db_node"]
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
        drop_table_query = f"DROP TABLE IF EXISTS ml_model;"

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
        CREATE TABLE "ml_model"(
            "id" BIGINT NOT NULL,
            "task_id" UUID NOT NULL,
            "url" VARCHAR(2000) NOT NULL,
            "start_date" TIMESTAMP(0) WITH
                TIME zone NULL,
            "end_date" TIMESTAMP(0) WITH
                TIME zone NULL,
            "result_id" BIGINT NULL,
            "errors" VARCHAR(500) NULL
        );
        """
        create_index_query = f"""
        ALTER TABLE
            "ml_model" ADD PRIMARY KEY("id");
        """

        # Создание таблицы
        try:
            self.cursor.execute(create_table_query)
            self.connection.commit()
            logger.info(
                f"Table ml_model created successfully"
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
                f"Index to ml_model created successfully"
            ) 
        except (Exception, psycopg2.Error) as error:
            logger.error(
                f"Error while creating index: {error}"
            ) 

        ############################### next table: #####################################

        # SQL-запрос для удаления таблицы, если она уже существует
        drop_table_query = f"DROP TABLE IF EXISTS results;"

        # Удаление таблицы, если она уже существует
        try:
            self.cursor.execute(drop_table_query)
            self.connection.commit()
        except (Exception, psycopg2.Error) as error:
            logger.error(
                f"Error while dropping table results:: {error}"
            ) 

        # SQL-запрос для создания таблицы
        create_table_query = f"""
        CREATE TABLE "results"(
            "id" BIGINT NOT NULL,
            "human_check" BOOLEAN NOT NULL
        );
        """

        create_index_query = f"""
        ALTER TABLE
            "results" ADD PRIMARY KEY("id");
        """

        # Создание таблицы
        try:
            self.cursor.execute(create_table_query)
            self.connection.commit()
            logger.info(
                f"Table results created successfully"
            ) 
        except (Exception, psycopg2.Error) as error:
            logger.error(
                f"Error while creating table results: {error}"
            )   

        # Создание индекса таблицы
        try:
            self.cursor.execute(create_index_query)
            self.connection.commit()
            logger.info(
                f"Index to results created successfully"
            ) 
        except (Exception, psycopg2.Error) as error:
            logger.error(
                f"Error while creating index results: {error}"
            ) 


    def insert_data(self, predict: bool, task_id, url, start_date, error=None) -> None:
        # Получение значений для записи в бд новой строки:
        id = self.last_id

        self._insert_in_ml_model(
            id=id, task_id=task_id, url=url, start_date=start_date, end_date=time.time(), error=error
        )  # добавим датку в ml_model
        self._insert_in_results(id=id, human_check=predict) # добавим датку в results

        self.last_db_update = time.time()  # Обновление времени последнего обновления базы данных
        self.last_id += 1


    def _insert_in_ml_model(
        self,
        id,
        task_id,
        url,
        start_date,
        end_date,
        error
    ) -> None:
        # Формирование и выполнение SQL-запроса для вставки данных в бд

        insert_query = (
            f"INSERT INTO ml_model"
            "(id, task_id, url, start_date, end_date, result_id, errors) "
            "VALUES (%s, %s, %s, to_timestamp(%s), to_timestamp(%s), %s, %s);"
        )
        try:
            self.cursor.execute(
                insert_query,
                (   
                    id,
                    task_id,
                    url,
                    start_date,
                    end_date,
                    id,
                    error,
                )
            )
            self.connection.commit()
            logger.info(
                f"Successfully inserted data into ml_model PostgreSQL"
            )   
        except (Exception, psycopg2.Error) as error:
            logger.error(
                f"Error while inserting data into ml_model PostgreSQL: {error}"
            )   


    def _insert_in_results(
        self,
        id,
        human_check,
    ) -> None:
        # Формирование и выполнение SQL-запроса для вставки данных в бд
        insert_query = (
            f"INSERT INTO results"
            "(id, human_check) "
            "VALUES (%s, %s);"
        )
        try:
            self.cursor.execute(
                insert_query,
                (   
                    id,
                    human_check,
                )
            )
            self.connection.commit()
            logger.info(
                f"Successfully inserted data into results PostgreSQL"
            )   
        except (Exception, psycopg2.Error) as error:
            logger.error(
                f"Error while inserting data into results PostgreSQL: {error}"
            )   
