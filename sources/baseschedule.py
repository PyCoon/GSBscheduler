# coding: utf-8
import os
from threading import Timer
import time
import datetime

import mysql.connector
from mysql.connector import errorcode


class SaveEverExist(BaseException):
    """Raise on a save file ever exist on disk, prevent overide"""
    def __init__(self, message):
        super(SaveEverExist, self).__init__(message)

class Configuration:
    """Configuration spacename"""
    connexion_data =  {
      'user': 'root',
      'password': '',
      'host': '127.0.0.1',
      'database': '',
      'raise_on_warnings': True,
    }

    script_dir=os.path.dirname(os.path.realpath(__file__))
    os.chdir(script_dir)

    def set_configuration(config_dict):
        """ Configuration setter"""
        Configuration.connexion_data = config_dict



class DatabaseConnection:
    """MySQL connection manager, don't prevent forget to close database connection"""
    def __init__(self):
        try:
            self.config = Configuration.connexion_data
        except ImportError:
            raise BaseException("Must define a configuration on Configuration object.")


        self.cnx_object = ''
    def __enter__(self):
        if not (type(self.cnx_object)==mysql.connector.connection.MySQLConnection) :
            try:
              self.cnx_object = mysql.connector.connect(**self.config)
              DatabaseConnection = self.cnx_object.DatabaseConnection()
              # Retorune le curseur utilisable
              return DatabaseConnection
            except mysql.connector.Error as err:
              if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Erreur dans le nom d'utilisateur ou le mot de passe.")
              elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("La base de donnée demandée n'existe pas.")
              else:
                print(err)



    def __exit__(self, type, value, traceback):
        self.cnx_object.commit()
        self.cnx_object.close()


def parse_iterable_on_printable_str(iterable, with_quote=True):
    """Convert an itérable to a printable tuple string"""

    if type(iterable)==(tuple or list):
        if not with_quote:
            return_str="({})".format(', '.join(elmt for elmt in iterable))
        else:
            return_str="({})".format(', '.join(repr(elmt) for elmt in iterable))
    elif iterable==None:
        return_str=0
    else:
        return_str="{}".format(', '.join(elmt for elmt in iterable))

    return return_str


class Adapter:
    """Adaptateur à la base, permet d'effectuer les requêtes"""

    def insert(into, values, column_name=''):
        """Insertion, dans la table, value peut être une liste de tuple"""
        # Ici on parse les colonnes et valeurs avec une lambda
        str_column_name=parse_iterable_on_printable_str(column_name, with_quote=False)
        str_value= parse_iterable_on_printable_str([ parse_iterable_on_printable_str(i) for i in values ])
        raw_sql = """INSERT INTO {str_into} {str_column_name} VALUES {str_value};""".format(
            str_into=into,
            str_column_name=str_column_name,
            str_value=str_value
        )
        return raw_sql

    def update(into, column, value, condition=''):
        if  condition!='': condition='WHERE '+condition
        raw_sql = """UPDATE {into} SET {column}={value} {condition} ;""".format(
                into=into,
                column=column,
                value=repr(value),
                condition=condition
            )
        return raw_sql

    def delete(into, condition=''):
        raw_sql = """DELETE FROM {into} WHERE {condition};""".format(
            into=into,
            condition=condition
        )
        return raw_sql

    def raw_sql_request(raw_sql=''):
        return raw_sql

class RecordManager:
    """Classes d'enregistrement et d'execution de requêtes SQL. Attention, la création d'ensemble de requêtes ne doit pas être faite lors d'accès concurents."""
    _queue = []
    _save_dir = 'old/'
    if not os.path.isdir(_save_dir): os.mkdir(_save_dir)

    @classmethod
    def get_save_name(cls, name):
        """Gen a filename for a save"""
        filename = cls._save_dir+name+'.txt'
        return filename

    @classmethod
    def record(cls, raw_sql):
        """Enregistre la requette dans la queue"""
        cls._queue.append(raw_sql)

    @classmethod
    def save(cls, save_name):
        """Sauvegarde les requêtes de la queue puis la vide"""
        filename = cls.get_save_name(save_name)
        if os.path.isfile(filename) and  os.path.isfile(filename) and os.path.getsize(filename) > 0 :
            raise SaveEverExist("Save name '{}' ever exist choose another or delete this one.".format(save_name))
        else:
            with open(cls.get_save_name(save_name), 'w') as fil:
                print(cls._queue)
                fil.write('\r'.join(cls._queue))
            cls._queue = []


    @classmethod
    def delete(cls, save_name):
        """Suprime brutalement la sauvegarde"""
        try:
            os.remove(cls.get_save_name(save_name))
        except FileNotFoundError:
            pass


    @classmethod
    def list(cls):
        """Liste les sauvegardes disponnibles"""
        '\n'.join(i.replace('.txt', '') for i in os.list(cls._save_dir))

    @classmethod
    def get_queue(cls):
        return cls._queue

    @classmethod
    def execute(cls, save_name=''):
        """Execute les requêtes dans la queue ou une sauvegarde si spécifiée en paramètre. Vide la queue."""
        if save_name=='':
            req_list=cls._queue
        else:
            with open(cls.get_save_name(save_name), 'r') as fil:
                req_list = fil.read().split('\r')
        with DatabaseConnection() as conn:
            for req in req_list:
                try:
                    # A implémenter: objet de retour permettant de lire le résultat: la methode actuelle n'est pas fiable.
                    DatabaseConnection = conn.execute(req)
                    result = DatabaseConnection.fetchall()
                    DatabaseConnection.close()
                except AttributeError:
                    result=[]

        cls._queue=[]
        return result

    @classmethod
    def clear(cls):
        cls._queue=[]



class Datemanager:
    """ Namespace for date functions"""
    def get_weird_gsb_last_month():
        dtn=datetime.datetime.now()
        str_year, str_month = str(dtn.year), str(dtn.month-1)
        if not len(str_month)>1:
            str_month= '0'+str_month

        last_weird_month = str_year + str_month
        return last_weird_month


class TimeCron:
    """Scheduler asynchrone, les taches crées sont déclenchées le lendemain à 00h"""
    def __init__(self):
        self.current_task=''
    def schedule(function, arguments):
        # get date du jour
        dtn=datetime.datetime.now()
        # calcul date début script (lendemain 00h)
        mddt = datetime.datetime(dtn.year, dtn.month, dtn.day+1, 0, 0, 0, 0)
        # Conversion en timestamp
        first_ts=time.mktime(mddt.timetuple())
        wait = first_ts-time.now()
        # On lance le scheduler
        Timer(wait, function, arguments).start()
        self.current_task=mddt
