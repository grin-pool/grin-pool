#!/usr/bin/python3

from grinbase.constants.MysqlConstants import MysqlConstants
from grinbase.dbaccess import database
from grinbase.dbaccess.database import database_details
from grinbase.model.pool_utxo import Pool_utxo

if __name__ == '__main__':
    database.db = database_details(MYSQL_CONSTANTS=MysqlConstants())
    database.db.initialize()

#    for i in range(0,10):
#        tmp = Pool_utxo(id=str(i), address=str(i), amount=1.5*i)
#        database.db.createDataObj(tmp)


    utxo = Pool_utxo.getPayable(0)[0]
    print(utxo)
    locked_utxo = Pool_utxo.get_locked_by_id(utxo.id)
    print(locked_utxo)
    locked_utxo.amount=1.0
    database.db.getSession().begin_nested();
    locked_utxo.amount=7.0
    database.db.getSession().commit()
    database.db.getSession().commit()

    utxo = Pool_utxo.getPayable(0)[0]
    print(utxo)


#    for utxo in Pool_utxo.getPayable(0):
#        Pool_utxo.get_locked_by_id(utxo.id)
#        print(utxo)




