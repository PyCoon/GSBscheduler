# coding: utf-8
from baseschedule import Configuration, Datemanager, Cursor, Adapter, RecordManager, TimeCron
import datetime


Configuration.set_configuration(
    {
      'user': 'root',
      'password': '',
      'host': '127.0.0.1',
      'database': 'gsbfrais',
      'raise_on_warnings': True,
    }

)

def database_maj():
    """Fonction de mise à jour de la base de donnee, chaque embranchement conditionnel correspond a une tache"""
    while True:
        dtn=datetime.datetime.now()
        # Entre le premier et dix du mois, on met les fiche de frais à CL
        if dtn.day>1 and dtn.day<9:
            weird_month = Datemanager.get_weird_gsb_last_month()
            RecordManager.delete("update_fichefrais")
            RecordManager.record(
                Adapter.update("fichefrais", "idEtat", "CL", "mois={}".format(weird_month) )
                )
            RecordManager.save('update_fichefrais')
            TimeCron.schedule(RecordManager.execute, ("update_fichefrais"))
        if dtn.day==20:
            weird_month = Datemanager.get_weird_gsb_last_month()
            RecordManager.delete("update_fichefrais")
            RecordManager.record(
                Adapter.update("fichefrais", "idEtat", "RB", "mois={}".format(weird_month) )
                )
            RecordManager.save('update_fichefrais')
            TimeCron.schedule(RecordManager.execute, ("update_fichefrais"))
        # Attendre le prochain contrôle le lendemain
        time.sleep(86400)

# La fonction ne doit pas se déclendher lors d'un import
if __name__ == '__main__':
    database_maj()
