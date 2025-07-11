class DBSecrets:
    """
    Class to hold sensitive information such as database credentials.
    This class should not be used in production code.
    """
    DB_USER = "etl"
    DB_PASSWORD = "etldevpass"
    DB_DSN = "localhost/xepdb1"
        