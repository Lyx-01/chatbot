from datetime import datetime
from Services.DBConnection import DBConnection


class ChatService(DBConnection):
    def __init__(self):
        super().__init__()

    def add_chat(self, id_user):
        """
        Ajoute un nouveau chat à la base de données et renvoie son ID.

        Parameters:
        - id_user (int): L'identifiant de l'utilisateur associé au chat.

        Returns:
        - int: L'identifiant du chat nouvellement créé.
        """
        self.connect()
        # Insère un nouveau chat dans la table CHAT et récupère son ID
        self.cur.execute(
            "INSERT INTO CHAT (created_at) VALUES (%s) RETURNING id",
            (datetime.now(),)
        )
        chat_id = self.cur.fetchone()[0]
        # Associe l'utilisateur au nouveau chat dans la table USER_CHATS
        self.cur.execute(
            "INSERT INTO USER_CHATS (id_user, id_chat) VALUES (%s, %s)", (id_user, chat_id)
        )
        self.close()
        return chat_id

    def deactivate_chat(self, chat_id):
        """
        Désactive et supprime le chat spécifié de la base de données.

        Parameters:
        - chat_id (int): L'identifiant du chat à désactiver.
        """
        self.connect()
        # Met à jour le champ is_active dans la table CHAT pour désactiver le chat
        self.cur.execute(
            "UPDATE CHAT SET is_active = %s WHERE id = %s",
            (False, chat_id,)
        )
        self.close()

    def get_name(self, chat_id):
        """
        Récupère le nom du chat spécifié.

        Parameters:
        - chat_id (int): L'identifiant du chat.

        Returns:
        - str or None: Le nom du chat, ou None si le chat n'est pas trouvé.
        """
        self.connect()
        # Exécute une requête SQL pour récupérer le nom du chat à partir de la table CHAT
        self.cur.execute("SELECT LIBELLE FROM CHAT WHERE id = %s", (chat_id,))
        name = self.cur.fetchone()  # Récupère le résultat de la requête
        self.close()
        return name[0] if name else None

    def rename_chat(self, new_name, chat_id):
        """
        Renomme le chat spécifié avec le nouveau nom fourni.

        Parameters:
        - new_name (str): Le nouveau nom du chat.
        - chat_id (int): L'identifiant du chat à renommer.
        """
        self.connect()
        # Met à jour le champ libelle dans la table CHAT avec le nouveau nom
        self.cur.execute(
            "UPDATE CHAT SET libelle = %s WHERE id = %s", (new_name, chat_id,)
        )
        self.close()

    def get_creation_date(self, chat_id):
        """
        Récupère la date de création du chat spécifié.

        Parameters:
        - chat_id (int): L'identifiant du chat.

        Returns:
        - str: La date de création du chat au format 'YY-MM-DD HH:MI:SS'.
        """
        self.connect()
        # Exécute une requête SQL pour récupérer la date de création du chat à partir de la table CHAT
        self.cur.execute(
            "SELECT to_char(created_at,'YY-MM-DD HH:MI:SS') FROM CHAT WHERE id = %s",
            (chat_id,))
        chat_creation_date = self.cur.fetchone()[0]
        self.close()
        return chat_creation_date

    def get_active_chat_ids(self, id_user):
        """
        Récupère les ID de tous les chats actifs dans la base de données pour un utilisateur spécifié.

        Parameters:
        - id_user (int): L'identifiant de l'utilisateur.

        Returns:
        - list: Une liste d'identifiants de chats actifs pour l'utilisateur.
        """
        self.connect()
        # Exécute une requête SQL pour récupérer les ID de chats actifs pour un utilisateur spécifié
        self.cur.execute("SELECT C.id FROM CHAT C "
                         "INNER JOIN USER_CHATS UC ON UC.id_chat = C.id "
                         "WHERE C.is_active = %s AND UC.id_user = %s", (True, id_user,))
        chat_ids = [chat_id[0] for chat_id in self.cur.fetchall()]
        self.close()
        return chat_ids

    def get_total_chats(self):
        """
        Récupère le nombre total de chats dans la base de données.

        Returns:
        - int: Le nombre total de chats dans la base de données.
        """
        self.connect()
        # Exécute une requête SQL pour récupérer le nombre total de chats dans la table CHAT
        self.cur.execute(
            "SELECT COUNT(*) FROM CHAT"
        )
        total_chats = self.cur.fetchone()[0]
        self.close()
        return total_chats

    def get_active_chats(self, id_user):
        """
        Récupère les chats actifs dans la base de données appartenant à un utilisateur spécifié.

        Parameters:
        - id_user (int): L'identifiant de l'utilisateur.

        Returns:
        - list: Une liste de tuples représentant les chats actifs de l'utilisateur.
        """
        self.connect()
        # Exécute une requête SQL pour récupérer les chats actifs d'un utilisateur spécifié
        self.cur.execute(
            "SELECT * FROM CHAT C"
            "INNER JOIN USER_CHATS UC ON UC.id_chat = C.id"
            "WHERE c.is_active = true AND UC.id_user = %s", (id_user,)
        )
        active_chats = self.cur.fetchall()
        self.close()
        return active_chats
