import pymysql
import io
import datetime

class DBConnection(object):
    def __init__(self, host='localhost', user='root', password='123456', db='thinkingapp'):
        super(DBConnection, self).__init__()
        self.connection = pymysql.connect(host=host,
                                    user=user,
                                    password=password,
                                    db=db,
                                    charset='utf8mb4',
                                    cursorclass=pymysql.cursors.DictCursor)
        self.sqlCmd = ""
        pass
    
    def Insertion(self,sql):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(sql)
            self.connection.commit()
            return True
        except Exception as ex:
            print('{}\n{}\n\n'.format(sql,str(ex)))

            current_time = datetime.datetime.now()
            with io.open(R"Insertion_Error_{:%Y%m%d_%H_%M}.log".format(current_time), 'a',encoding='utf-8') as f:
                f.write('{}\n{}\n\n'.format(sql,str(ex)))
            return False
    
    def selection(self,sql):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(sql)
                res = cursor.fetchall()
            self.connection.commit()
            return res
        except Exception as ex:
            print(ex)
    
    def close(self):
        self.connection.close()