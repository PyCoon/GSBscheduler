Base Schedule
=====================

Librairie de classes permettant de:

 - Mapper certaines fonctionnalité SQL (dévelopé pour MySQL)
 - Sauvegarder un ensemble de requêtes dans des fichiers pour exécution programmées.


Documentation
---------------------

Configurer la connexion, exécuter une requête:

```python
config={
  'user': 'test',
  'password': '2bSf8v9vUKugHjaA',
  'host': '127.0.0.1',
  'database': 'test',
  'raise_on_warnings': True,
}
Configuration.set_configuration(config)
insertion_request = "INSERT INTO xxx (nom, prenom) VALUES ('foo', 'bar');"
RecordManager.record(
          Adapter.raw_sql_request(insertion_request)
      )
  RecordManager.execute()
```

Enregistrer des reqêtes:

```python
RecordManager.record(
          Adapter.raw_sql_request(insertion_request)
      )
RecordManager.save('user_maj')
```

Executer un jeu de requête enregistré:

```python
RecordManager.execute('user_maj')
```



Tests
---------------------

python3.4 src/test.py

Dépendances
---------------------

#### Windows

[mysqlconnector](https://dev.mysql.com/downloads/connector/odbc/)
[python3.4](https://www.python.org/downloads/)

#### Linux
  - apt-get install build-essential libssl-dev libffi-dev python3-dev
  - pip install mysql-connector==2.1.4


TEST BASE DE DONNEE
======================

Crée un utilisateur spécifique pour les tests qui créera une base vide.
```SQL
CREATE USER 'test'@'%' IDENTIFIED WITH mysql_native_password AS '***';GRANT USAGE ON *.* TO 'test'@'%' REQUIRE NONE WITH MAX_QUERIES_PER_HOUR 0 MAX_CONNECTIONS_PER_HOUR 0 MAX_UPDATES_PER_HOUR 0 MAX_USER_CONNECTIONS 0;CREATE DATABASE IF NOT EXISTS `test`;GRANT ALL PRIVILEGES ON `test`.* TO 'test'@'%';
```
