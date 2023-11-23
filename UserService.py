import bcrypt
from Services.DBConnection import DBConnection

BOT_NAME = 'CETIChat'


class UserService(DBConnection):
    def __init__(self):
        """
        Initialise une instance de la classe UserService en héritant des fonctionnalités de DBConnection.
        """
        super().__init__()

    def get_all_users(self):
        """
        Récupère toutes les informations sur les utilisateurs depuis la base de données.

        Returns:
        - dict: Un dictionnaire contenant les informations des utilisateurs avec les noms d'utilisateur comme clés.
        """
        self.connect()
        self.cur.execute('SELECT * FROM "USER"')
        users = self.cur.fetchall()
        self.close()

        user_data = {}
        column_names = [desc[0] for desc in self.cur.description]  # Noms des colonnes
        for user in users:
            user_dict = dict(zip(column_names, user))
            username = user_dict["username"]
            user_data[username] = {
                "mail": user_dict["mail"],
                "name": user_dict["name"],
                "password": user_dict["password"]
            }

        return user_data

    def authenticate_user(self, username, password):
        """
        Vérifie les informations d'authentification de l'utilisateur par rapport à la base de données.

        Parameters:
        - username (str): Le nom d'utilisateur.
        - password (str): Le mot de passe.

        Returns:
        - dict or None: Un dictionnaire contenant les informations de l'utilisateur si l'authentification réussit,
          sinon None.
        """
        self.connect()
        self.cur.execute('SELECT * FROM "USER" WHERE username = %s', (username,))
        user_data = self.cur.fetchone()
        self.close()
        if user_data:
            user_data_dict = {
                "id": user_data[0],
                "username": user_data[1],
                "password": user_data[2],
                "mail": user_data[3],
                "name": user_data[4],
                "is_active": user_data[5],
                "id_role": user_data[6]

            }
            # Vérifie le MDP haché
            if username != BOT_NAME and bcrypt.checkpw(password.encode('utf-8'), user_data_dict['password'].encode('utf-8')):
                return user_data_dict

        return None

    def register_user(self, username, password, mail, name):
        """
        Crée un nouvel utilisateur dans la base de données.

        Parameters:
        - username (str): Le nom d'utilisateur du nouvel utilisateur.
        - password (str): Le mot de passe du nouvel utilisateur.
        - mail (str): L'adresse e-mail du nouvel utilisateur.
        - name (str): Le nom du nouvel utilisateur.
        """
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        stored_password = hashed_password.decode('utf-8')
        self.connect()
        self.cur.execute(
            'INSERT INTO "USER" (username, id_role, password, mail, name, is_active) VALUES (%s, %s, %s, %s, %s, %s)',
            (username, 1, stored_password, mail, name, True)
        )
        self.close()

    def get_role(self, id_user):
        """
        Retourne le nom du rôle correspondant au user dans la base de données.

        Parameters:
        - id_user (int): L'identifiant de l'utilisateur.

        Returns:
        - str or None: Le nom du rôle de l'utilisateur, ou None si l'utilisateur n'est pas trouvé.
        """
        self.connect()
        self.cur.execute(
            'SELECT R.name FROM ROLES R'
            'INNER JOIN "USER" U ON U.id_role = R.id'
            'WHERE U.id = %s', (id_user,)
        )
        role_name = self.cur.fetchone()
        self.close()
        return role_name[0] if role_name else None
