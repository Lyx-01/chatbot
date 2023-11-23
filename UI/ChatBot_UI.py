import time
import streamlit as st
from streamlit_star_rating import st_star_rating
import requests

from Services.ChatService import ChatService
from Services.MessageService import MessageService
from NLP.Chatbot_v0_7 import chatbotv0
from Services.UserService import UserService

# Les informations d'authentification pour l'API
api_headers = {
    'X-TS-TENANT': '02411ebc-17ec-4d1c-b1ac-d1b5514ee629',
    'Authorization': 'BasicZm9vQGJhci5jb206c2VjcmV0'
}


def get_data_from_api(captor, start, end):
    """
      Récupère des données d'une API Prometheus pour un capteur donné dans une plage de temps spécifiée.

      Parameters:
      - captor (str): Nom du capteur pour lequel les données doivent être récupérées.
      - start (int): Timestamp de début de la plage de temps (en secondes depuis l'époque).
      - end (int): Timestamp de fin de la plage de temps (en secondes depuis l'époque).

      Returns:
      - pd.DataFrame or None: Un DataFrame Pandas contenant les données récupérées, ou None si la requête a échoué.

      Cette fonction utilise l'API Prometheus pour interroger les données d'un capteur spécifique
      dans une plage de temps donnée. Les résultats sont formatés en un DataFrame Pandas avec des colonnes
      'Start' et 'End' pour les valeurs temporelles. Les données sont groupées par clé de capteur.

      Si la requête réussit (statut HTTP 200), renvoie le DataFrame résultant.
      Sinon, renvoie None.

      """
    url = f"https://promql.tsorage-dev.cetic.be/api/v1/query_range?query={captor}&start={start}&end={end}"
    response = requests.get(url, headers=api_headers, verify=False)

    if response.status_code == 200:
        return response.json()
    else:
        return None


def bot_answer(u_input):
    if u_input == "Quelle sera la valeur prédite de CO2 dans la salle Turing dans 15 jours ?":
        answer = "La valeur prédite de co2 dans la salle Turing est de 684.581 ppm pour dans 15 jours."
    elif u_input == "Quelle était la température moyenne des derniers jours dans la salle Turing ?":
        answer = "La température moyenne des derniers jours dans la salle Turing est de 20.25°C."
    else:
        answer = "Je ne comprends pas votre demande."
    return answer


def registration_page(user_service):
    """
    Affiche une page d'inscription dans l'application Streamlit.

    Parameters:
    - user_service (object): Service utilisateur responsable de la gestion des utilisateurs.

    Utilise Streamlit pour créer un formulaire d'inscription avec les champs suivants :
    - Nom d'utilisateur
    - Mot de passe
    - Email
    - Prénom

    Lorsque le formulaire est soumis, vérifie que tous les champs obligatoires sont remplis.
    Si c'est le cas, utilise le service utilisateur pour enregistrer le nouvel utilisateur
    avec les informations fournies. Affiche un message de succès en cas d'inscription réussie.

    """
    with st.form("inscription"):
        st.title("Inscription")
        username = st.text_input("Nom d'utilisateur*", key="reg_username")
        password = st.text_input("Mot de passe*", type="password", key="reg_password")
        email = st.text_input("Email*", key="reg_email")
        name = st.text_input("Prénom*", key="reg_name")
        submitted = st.form_submit_button("S'inscrire")
        if submitted:
            if not username or not password or not email or not name:
                st.error("Veuillez remplir tous les champs marqués d'un astérisque.")
            else:
                user_service.register_user(username, password, email, name)
                st.success("Inscription réussie ! Vous pouvez maintenant vous connecter.")


def connection_form(user_service):
    """
    Affiche une page de connexion dans l'application Streamlit.

    Parameters:
    - user_service (object): Service utilisateur responsable de la gestion des utilisateurs.

    Utilise Streamlit pour créer un formulaire de connexion avec les champs suivants :
    - Nom d'utilisateur
    - Mot de passe

    Lorsque le formulaire de connexion est soumis, utilise le service utilisateur pour
    authentifier l'utilisateur en vérifiant les informations de connexion. Si l'authentification
    réussit, enregistre les informations de l'utilisateur dans la session Streamlit.

    """
    with st.form("login"):
        st.title("Connexion")
        username = st.text_input("Nom d'utilisateur")
        password = st.text_input("Mot de passe", type="password")
        login_button = st.form_submit_button("Se connecter")
        if login_button:
            user = user_service.authenticate_user(username, password)
            if user:
                st.session_state.user_authenticated = True  # L'utilisateur est connecté
                st.session_state.id = user['id']
                st.session_state.username = user['username']  # Stockage du nom d'utilisateur en session
                st.session_state.role = user['id_role']


def main():
    # data = get_data_from_api("dmway_water_pump_electric_meter_current", "2023-06-01T15:49:00.000Z",
    #                         "2023-06-15T15:49:59.000Z")
    user_service = UserService()
    # Afficher le formulaire de connexion si l'utilisateur n'est pas encore connecté
    if 'user_authenticated' not in st.session_state:
        st.session_state.user_authenticated = False

    # Si l'utilisateur est connecté, afficher les chats actifs
    if st.session_state.user_authenticated:
        col1, col2 = st.sidebar.columns([6, 4])  # Distribution de l'espace 6:4

        with st.sidebar:
            col1.title(f"{st.session_state.username}")
            st.divider()

        with col2:
            st.text('')
            if st.button("Déconnexion"):
                st.session_state.user_authenticated = False
                st.experimental_rerun()

        message_service = MessageService()
        chat_service = ChatService()

        new_chat = st.sidebar.button("Nouveau chat")

        if new_chat:
            chat_service.add_chat(st.session_state.id)

        # Récupérez les IDs de tous les chats actifs
        chat_ids = chat_service.get_active_chat_ids(st.session_state.id)
        chat_options = []

        if len(chat_ids) == 0:
            st.sidebar.text("Commencez par créer un chat...")
        else:
            # Créez une liste de tuples (chat_id, date_de_creation) pour chaque chat actif
            chat_creation_dates = [(chat_id, chat_service.get_creation_date(chat_id)) for chat_id in chat_ids]

            # Créez une liste de chaînes de texte pour les options de radio
            for chat_id, creation_date in chat_creation_dates:
                #    if chat_service.get_name(chat_id):
                #        chat_options.append(chat_service.get_name(chat_id) + f" - {creation_date}")
                chat_options.append(f"Chat {chat_id} - {creation_date}")

            # Sélectionnez le chat
            selected_chat = st.sidebar.radio("Choisissez un chat :", chat_options)

            # Obtenez l'ID du chat sélectionné
            chat_id = int(selected_chat.split()[1])

            # Affichez le titre du chat
            st.title(f'CETIChat - Chat {chat_id}')

            # CHANGEMENT DE NOM DE CHAT
            # Champ de saisie pour renommer le chat
            #   new_name = st.text_input("Renommer le chat :")

            # Si un nouveau nom est saisi, mettez à jour le nom du chat
            #   if new_name:
            #       chat_service.rename_chat(new_name, chat_id)

            st.divider()

            # Suppression d'un chat
            delete_button = st.sidebar.button("Supprimer ce chat")
            if delete_button:
                chat_service.deactivate_chat(chat_id)
                st.experimental_rerun()

            chat_history = message_service.get_messages_from_chat(chat_id)
            with st.chat_message("assistant"):
                st.empty().markdown("Bonjour, je suis CETIChat ! Que puis-je faire pour vous aujourd'hui ?")
            # Réaffichage de l'historique de message quand on navigue entre les conversations
            ordered_messages = sorted(chat_history, key=lambda x: x["sent_at"])  # Tri des messages par le champ sent_at

            for message in ordered_messages:
                if message["id_user"] == 1:  # Vérifier si le message est du bot
                    message_role = "assistant"  # Définir le rôle comme "assistant"
                else:
                    message_role = "user"  # Sinon c'est un message de l'utilisateur

                message_content = message["content"]  # Récupérer le contenu du message

                with st.chat_message(message_role):
                    st.markdown(message_content)

                    if message_role == "assistant":
                        rating_key = f"rating_{message['id']}"
                        comment_key = f"comment_{message['id']}"

                        # Afficher les étoiles de rating et récupérer sa valeur
                        rating = st_star_rating(label="", maxValue=5, defaultValue=0,
                                                key=rating_key, size=20)

                        if rating:
                            # Afficher le champ de commentaire et récupérer sa valeur
                            comment = st.text_input("Laissez un commentaire (optionnel)", key=comment_key)
                            message_id = message["id"]
                            message_service.save_rating(rating, comment, message_id)
            # USER
            user_input = st.chat_input("Entrez votre message...")
            if user_input:
                st.chat_message("user").markdown(user_input)
                # Ajout du message de l'utilisateur à l'historique de conversation
                message_service.save_message(user_input, chat_id, st.session_state.id)

                # BOT
                # Affichage de la réponse du BOT
                with st.chat_message("assistant"):
                    with st.spinner('Veuillez patienter...'):
                        message_placeholder = st.empty()
                        full_response = ""
                        bot_response = chatbotv0(user_input)
                        print(bot_response)
                        # Simuler une écriture en live du bot
                        for chunk in bot_response.get('message').split():
                            full_response += chunk + " "
                            time.sleep(0.05)
                            # Ajout d'un curseur pour plus d'immersion
                            message_placeholder.markdown(full_response + "▌")
                        message_placeholder.markdown(full_response)

                        # Insérez la réponse du bot dans la base de données
                        message_service.save_message(full_response, chat_id, 1)
                        st.experimental_rerun()

    else:
        connection_form(user_service)
        registration_page(user_service)


if __name__ == "__main__":
    main()
