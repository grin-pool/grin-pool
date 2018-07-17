from grinbase.constants.MysqlConstants import MysqlConstants
from grinbase.dbaccess import database
from grinbase.dbaccess.database import database_details
from grinbase.model.UnspentTransactionOutput import UnspentTxOutput

if __name__ == '__main__':
    database.db = database_details(MYSQL_CONSTANTS=MysqlConstants())
    database.db.initialize()

    for i in range(0,10):
        tmp = UnspentTxOutput(id=str(i), address=str(i), amount=1.5*i)
        database.db.createDataObj(tmp)


    for utxo in UnspentTxOutput.getAll():
        print(utxo)




