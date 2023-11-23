import psycopg2


class DBConnection:
    def __init__(self):
        """
        Initialise une instance de la classe DBConnection avec les paramètres de connexion par défaut.
        """
        self.host = ""
        self.database = ""
        self.user = ""
        self.password = ""
        self.conn = None
        self.cur = None

    def connect(self):
        """
        Établit une connexion à la base de données PostgreSQL en utilisant les paramètres spécifiés.
        Initialise également un curseur pour exécuter des requêtes SQL.
        """
        self.conn = psycopg2.connect(
            host=self.host,
            database=self.database,
            user=self.user,
            password=self.password
        )
        self.cur = self.conn.cursor()

    def close(self):
        """
        Commit toutes les modifications dans la base de données, puis ferme la connexion et le curseur.
        """
        self.conn.commit()
        self.conn.close()
