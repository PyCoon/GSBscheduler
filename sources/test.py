import unittest
import os
import datetime
import sqlite3
import time

import mysql.connector
from mysql.connector import errorcode

from baseschedule import Configuration, Datemanager, Cursor, Adapter, RecordManager, TimeCron

config={
                'user': 'test',
                'password': '2bSf8v9vUKugHjaA',
                'host': '127.0.0.1',
                'database': 'test',
                'raise_on_warnings': True,
                    }


def delete_test_base():
    """Delete entire test database"""
    Configuration.set_configuration(config)
    deletion_request ="""DROP TABLE xtest;"""
    RecordManager.record(
        Adapter.raw_sql_request(deletion_request)
    )
    RecordManager.execute()

def set_up_test_base():
    """Create test database"""
    Configuration.set_configuration(config)
    timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    creation_request ="CREATE TABLE xtest (id INT(6) UNSIGNED AUTO_INCREMENT PRIMARY KEY, nom VARCHAR(180) NOT NULL, datestamp TIMESTAMP NOT NULL);"
    insertion_request = "INSERT INTO xtest (nom, datestamp) VALUES ('toto', '"+ str(timestamp) + "');"
    RecordManager.record(
        Adapter.raw_sql_request(creation_request)
    )
    RecordManager.record(
            Adapter.raw_sql_request(insertion_request)
        )
    RecordManager.execute()

class TestConfigurationClass(unittest.TestCase):

    def test_set_config(self):
        dico={
              'user': 'zerg',
              'password': 'toto',
              'host': '127.0.0.1',
              'database': 'gbzé',
              'raise_on_warnings': True,
        }
        Configuration.set_configuration(dico)
        self.assertEqual(dico, Configuration.connexion_data)



class TestAdapter(unittest.TestCase):

    def setUp(self):
        set_up_test_base()

    def tearDown(self):
        delete_test_base()



    def test_insert(self):
        """Test de la fonction d'insertion"""
        timestamp1 = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
        timestamp2 = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
        RecordManager.record(
            Adapter.insert('xtest',
                [('jerry', timestamp1 ), ('levy', timestamp2)],
                ('nom', 'datestamp')
            )
        )
        RecordManager.execute()
        cnx_object = mysql.connector.connect(**config)
        cursor = cnx_object.cursor()
        query = ("SELECT datestamp FROM xtest WHERE nom='jerry'")
        cursor.execute(query)
        result = cursor.fetchone()
        cursor.close()
        cnx_object.close()
        self.assertEqual(timestamp1, result[0].strftime('%Y-%m-%d %H:%M:%S'))

    def test_update(self):
        """Test de la fonction de mise à jour"""
        timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
        RecordManager.record(
            Adapter.update('xtest', 'datestamp', timestamp, condition="nom='toto'")
        )
        RecordManager.execute()
        cnx_object = mysql.connector.connect(**config)
        cursor = cnx_object.cursor()
        query = ("SELECT datestamp FROM xtest")
        cursor.execute(query)
        result = cursor.fetchone()
        cursor.close()
        cnx_object.close()
        self.assertEqual(timestamp, result[0].strftime('%Y-%m-%d %H:%M:%S'))

class TestRecordManager(unittest.TestCase):

    def setUp(self):
        RecordManager.clear()
    def tearDown(self):
        RecordManager.clear()

    def test_record(self):
        """Vérifie l'enregistrement des requêtes"""
        RecordManager.record("SELECT * FROM test")
        RecordManager.record("SELECT * FROM test")
        self.assertEqual(len(RecordManager._queue), 2)

    def test_save_and_file_loading(self):
        """Teste la fonction de sauvegarde et le chargement du fichier de save et son exécution"""
        set_up_test_base()
        timestamp1 = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
        RecordManager.record(
            Adapter.insert('xtest',
                [('bibi', timestamp1 )],
                ('nom', 'datestamp')
            )
        )
        RecordManager.delete('test_save')
        RecordManager.save('test_save')
        RecordManager.execute('test_save')
        cnx_object = mysql.connector.connect(**config)
        cursor = cnx_object.cursor()
        query = ("SELECT datestamp FROM xtest WHERE nom='bibi'")
        cursor.execute(query)
        result = cursor.fetchone()
        cursor.close()
        cnx_object.close()
        self.assertEqual(timestamp1, result[0].strftime('%Y-%m-%d %H:%M:%S'))
        delete_test_base()


if __name__ == '__main__':
    try:
        delete_test_base()
    except:
        pass
    unittest.main()
