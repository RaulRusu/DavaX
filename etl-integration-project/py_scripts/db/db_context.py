import oracledb
from db.db_secrets import DBSecrets

class DBContext:
    def __init__(self, reuse_connection=False):
        self.user = DBSecrets.DB_USER
        self.password = DBSecrets.DB_PASSWORD
        self.dsn = DBSecrets.DB_DSN
        self.connection = None
        self.reuse_connection = reuse_connection

    def __enter__(self):
        if self.connection is None:
            self.connection = oracledb.connect(
                user=self.user,
                password=self.password,
                dsn=self.dsn
            )   
        return self.connection

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self.reuse_connection:
            self.close()

    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None