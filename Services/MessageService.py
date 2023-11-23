from Services.DBConnection import DBConnection
from datetime import datetime


class MessageService(DBConnection):
    def __init__(self):
        super().__init__()

    def save_message(self, content, chat_number, id_user):
        """
        Enregistre un nouveau message dans la base de données.

        Parameters:
        - content (str): Le contenu du message.
        - chat_number (int): Le numéro du chat auquel le message est associé.
        - id_user (int): L'identifiant de l'utilisateur qui a envoyé le message.
        """
        self.connect()
        # Exécute une requête SQL pour insérer un nouveau message dans la table MESSAGE
        self.cur.execute(
            "INSERT INTO MESSAGE (content, sent_at, id_chat, id_user, id_message_code) VALUES (%s, %s, %s, %s, %s)",
            (content, datetime.now(), chat_number, id_user, 1)
        )
        self.close()

    def get_rating_value(self, message_id):
        """
        Récupère la valeur du rating associée à un message spécifique.

        Parameters:
        - message_id (int): L'identifiant du message.

        Returns:
        - int or None: La valeur du rating associée au message, ou None si aucune valeur n'est trouvée.
        """
        self.connect()
        # Exécute une requête SQL pour récupérer la valeur du rating à partir de la table RATING
        self.cur.execute(
            "SELECT R.VALUE FROM RATING R"
            " INNER JOIN MESSAGE M ON M.ID_RATING = R.ID"
            " WHERE M.ID = %s", (message_id,)
        )
        rating_value = self.cur.fetchone()
        self.close()
        return rating_value

    def save_rating(self, value, comment, message_id):
        """
        Enregistre un nouveau rating dans la base de données et lie le rating au message correspondant.

        Parameters:
        - value (int): La valeur du rating.
        - comment (str): Le commentaire associé au rating.
        - message_id (int): L'identifiant du message auquel le rating est associé.
        """
        # Si la valeur du rating est 0, le rating n'est pas enregistré
        if value == 0:
            return
        self.connect()
        # Exécute une requête SQL pour enregistrer un nouveau rating dans la table RATING
        self.cur.execute(
            "SELECT id_rating FROM MESSAGE WHERE id = %s", (message_id,)
        )
        id_rating_result = self.cur.fetchone()

        if id_rating_result == (None,):
            # Si le message n'a pas encore de rating, crée un nouveau rating
            self.cur.execute(
                "INSERT INTO RATING (value, comment) VALUES (%s, %s) RETURNING id",
                (value, comment)
            )
            rating_id = self.cur.fetchone()[0]
        else:
            # Si le message a déjà un rating, met à jour le rating existant
            id_rating = id_rating_result[0]
            self.cur.execute(
                "UPDATE RATING SET value = %s, comment = %s WHERE id = %s",
                (value, comment, id_rating)
            )
            rating_id = id_rating

        # Lie le rating au message dans la table MESSAGE
        self.cur.execute(
            "UPDATE MESSAGE SET id_rating = %s WHERE id = %s",
            (rating_id, message_id)
        )
        self.close()

    def get_all_messages(self):
        """
        Récupère tous les messages depuis la base de données.

        Returns:
        - list: Une liste de dictionnaires représentant tous les messages dans la base de données.
        """
        self.connect()
        # Exécute une requête SQL pour récupérer tous les messages de la table MESSAGE
        self.cur.execute(
            "SELECT * FROM MESSAGE"
        )
        columns = [desc[0] for desc in self.cur.description]  # Noms des colonnes
        # Convertit les résultats en une liste de dictionnaires
        messages = [dict(zip(columns, row)) for row in self.cur.fetchall()]
        self.close()
        return messages

    def get_messages_from_chat(self, chat_number):
        """
        Récupère tous les messages d'un chat spécifique depuis la base de données.

        Parameters:
        - chat_number (int): Le numéro du chat.

        Returns:
        - list: Une liste de dictionnaires représentant les messages du chat spécifié.
        """
        self.connect()
        # Exécute une requête SQL pour récupérer tous les messages d'un chat spécifique de la table MESSAGE
        self.cur.execute(
            "SELECT * FROM MESSAGE WHERE id_chat = %s", (chat_number,)
        )
        columns = [desc[0] for desc in self.cur.description]  # Noms des colonnes
        # Convertit les résultats en une liste de dictionnaires
        messages = [dict(zip(columns, row)) for row in self.cur.fetchall()]
        self.close()
        return messages
