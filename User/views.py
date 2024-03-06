from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSerializer
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import check_password
from .models import User
import random
import string
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
from django.contrib import messages
from rest_framework.response import Response
from rest_framework.decorators import api_view
from urllib.parse import quote_plus
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.hashers import make_password

@api_view(['POST'])
def send_verification_code(request):
    email = request.data.get('email')
    if email:
        verification_code = get_random_string(length=6, allowed_chars='0123456789')
        # Send the email
        send_mail(
            'Code de vérification',
            f'Votre code de vérification est : {verification_code}',
            'rahmatezeghdenti@gmail.com',
            [email],
            fail_silently=False,
        )
        return Response({"message": "Email sent successfully"}, status=200)
    else:
        return Response({"message": "Email not provided in request"}, status=400)

   
@api_view(['POST'])
def user_registration(request):
    if request.method == 'POST':
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get('email')
            cin = serializer.validated_data.get('cin')
            
            existing_email = User.objects.filter(email=email).exists()
            existing_cin = User.objects.filter(cin=cin).exists()
            
            if existing_email:
                return Response({"message": "Un utilisateur avec cet e-mail existe déjà."}, status=status.HTTP_400_BAD_REQUEST)
            elif existing_cin:
                return Response({"message": "Un utilisateur avec ce CIN existe déjà."}, status=status.HTTP_400_BAD_REQUEST)
            else:
                serializer.save()
                response = Response(serializer.data, status=status.HTTP_201_CREATED)
                response["Access-Control-Allow-Origin"] = "*"  # Ajoute les en-têtes CORS
                return response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return HttpResponse(status=status.HTTP_405_METHOD_NOT_ALLOWED)

# Méthode pour l'authentification de l'utilisateur

@api_view(['POST'])
def user_login(request):
    """
    Authentifie un utilisateur existant.

    Paramètres:
    - request : HttpRequest - la requête HTTP contenant les informations d'identification de l'utilisateur (cin et mot de passe).

    Retour:
    - HttpResponse : réponse HTTP avec le statut approprié et un message indiquant si l'authentification a réussi ou non.
    """
    if request.method == 'POST':
        cin = request.data.get('cin')
        password = request.data.get('password')

        try:
            user = User.objects.get(cin=cin)
        except User.DoesNotExist:
            user = None

        if user is not None:
            if user.is_active:
                if check_password(password, user.password):
                    refresh = RefreshToken.for_user(user)
                    return Response({
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                    })
                else:
                    return Response({'message': 'Mot de passe incorrect'}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response({'message': 'Ce compte n\'est pas activé'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({'message': 'CIN incorrect'}, status=status.HTTP_401_UNAUTHORIZED)

    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['PUT'])
def validate_user_account(request, cin):
    """
    Valide le compte utilisateur en mettant à jour le champ "is_active" de False à True.

    Paramètres :
    - request : HttpRequest - la requête HTTP contenant les données de mise à jour.
    - user_id : int - l'identifiant de l'utilisateur dont le compte doit être validé.

    Retour :
    - HttpResponse : réponse HTTP avec le statut approprié et un message indiquant si la mise à jour a réussi ou non.
    """
    try:
        user = User.objects.get(cin=cin)
    except User.DoesNotExist:
        return Response({"message": "Utilisateur non trouvé"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        user.is_active = True
        user.save()
        return Response({"message": "Compte utilisateur validé avec succès"}, status=status.HTTP_200_OK)

    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)





@api_view(['POST'])
def send_Email(request):
    """
    Envoie un e-mail de récupération de mot de passe à l'utilisateur avec un lien sécurisé.

    Paramètres :
    - request : HttpRequest - la requête HTTP contenant l'adresse e-mail de l'utilisateur.

    Retour :
    - HttpResponse : réponse HTTP avec le statut approprié et un message indiquant si l'e-mail a été envoyé avec succès.
    """
    if request.method == 'POST':
        email = request.data.get('email')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"message": "Aucun utilisateur trouvé avec cette adresse e-mail"}, status=status.HTTP_404_NOT_FOUND)

        # Générer un code de récupération aléatoire
        recovery_code = ''.join(random.choices('0123456789', k=6))

        # Mettre à jour le code de récupération de l'utilisateur dans la base de données
        user.recovery_code = recovery_code
        user.save()

        # Envoyer l'e-mail de récupération de mot de passe
        subject = 'Réinitialisation de mot de passe'
        message = f'Utilisez le code suivant pour réinitialiser votre mot de passe : {recovery_code}'
        from_email = 'rahmatezeghdenti@gmail.com'  # Remplacez par votre adresse e-mail Gmail
        to_email = [user.email]
        

        send_mail(
            'Sujet de l\'email',
            'Corps du message.',
            'adminmira@coursenligne.info',
            ['rahmatezeghdenti@gmail.com'],
            fail_silently=False,
        )


        return Response({"message": "Un e-mail de récupération de mot de passe a été envoyé à votre adresse e-mail"}, status=status.HTTP_200_OK)

    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['GET'])
def inactive_users(request):
    """
    Récupère tous les utilisateurs ayant la valeur False dans le champ is_active.

    Retour :
    - HttpResponse : réponse HTTP avec la liste des utilisateurs inactifs et leur détails.
    """
    if request.method == 'GET':
        all_users = User.objects.all()
        inactive_users = [user for user in all_users if not user.is_active]
        serializer = UserSerializer(inactive_users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    




@api_view(['POST'])
def check_cin(request):
    if request.method == 'POST':
        cin = request.data.get('cin')
        if cin is None:
            return Response({"error": "No cin provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        users_with_cin = User.objects.filter(cin=cin)
        if not users_with_cin:  # If the queryset is empty
            return Response({"exists": False, "message": "No user found with the provided cin"}, status=status.HTTP_200_OK)
        
        return Response({"exists": True}, status=status.HTTP_200_OK)
    
@api_view(['POST'])
def check_email(request):
    if request.method == 'POST':
        email = request.data.get('email')
        if email is None:
            return Response({"error": "No email provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        users_with_email = User.objects.filter(email=email)
        if not users_with_email:
            return Response({"exists": False, "message": "No user found with the provided email"}, status=status.HTTP_200_OK)
        
        return Response({"exists": True}, status=status.HTTP_200_OK)




# Méthode pour vérifier l'existence d'un identifiant (cin)
@api_view(['GET'])
def check_identifient(request, cin):
    if request.method == 'GET':
        try:
           user = User.objects.get(cin=cin)
        except User.DoesNotExist:
            return Response({"message": "Utilisateur non trouvé"}, status=status.HTTP_404_NOT_FOUND)

from django.contrib.sessions.models import Session
from django.http import JsonResponse

# Méthode pour démarrer une session pour un utilisateur
@api_view(['POST'])
def start_session(request):
    """
    Démarre une session pour l'utilisateur actuel.
    """
    if request.method == 'POST':
        # Start a session
        request.session['is_authenticated'] = True
        return JsonResponse({'message': 'Session started successfully'}, status=200)
    return JsonResponse({'error': 'Method not allowed'}, status=405)



# Méthode pour vérifier si l'utilisateur a une session active
@api_view(['GET'])
def check_session(request):
    """
    Vérifie si l'utilisateur a une session active.
    """
    if request.method == 'GET':
        is_authenticated = request.session.get('is_authenticated', False)
        return JsonResponse({'is_authenticated': is_authenticated}, status=200)

# Méthode pour terminer la session de l'utilisateur
@api_view(['POST'])
def end_session(request):
    """
    Termine la session de l'utilisateur.
    """
    if request.method == 'POST':
        # End the session
        request.session.flush()
        return JsonResponse({'message': 'Session ended successfully'}, status=200)
    return JsonResponse({'error': 'Method not allowed'}, status=405)


 # Password Reset Views
 # Password Reset Views
 # Password Reset Views
 # Password Reset Views
 # Password Reset Views
 # Password Reset Views
 # Password Reset Views
 # Password Reset Views
 # Password Reset Views
 # Password Reset Views
 # Password Reset Views
 # Password Reset Views


@api_view(['GET'])
def reset_password_users(request):
    """
    Récupère tous les utilisateurs ayant la valeur False dans le champ is_active.

    Retour :
    - HttpResponse : réponse HTTP avec la liste des utilisateurs inactifs et leur détails.
    """
    if request.method == 'GET':
        all_users = User.objects.all()
        reset_password_user = [user for user in all_users if  user.reset_password]
        serializer = UserSerializer(reset_password_user, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['PUT'])
def demande_reset_password(request, cin):
    """
    Valide le compte utilisateur en mettant à jour le champ "is_active" de False à True.

    Paramètres :
    - request : HttpRequest - la requête HTTP contenant les données de mise à jour.
    - user_id : int - l'identifiant de l'utilisateur dont le compte doit être validé.

    Retour :
    - HttpResponse : réponse HTTP avec le statut approprié et un message indiquant si la mise à jour a réussi ou non.
    """
    try:
        user = User.objects.get(cin=cin)
    except User.DoesNotExist:
        return Response({"message": "Utilisateur non trouvé"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        user.reset_password = True
        user.save()
        return Response({"message": "Demande envoye  avec succès"}, status=status.HTTP_200_OK)

    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)



@api_view(['PUT'])
def reset_password(request, cin):
    try:
        user = User.objects.get(cin=cin)
    except User.DoesNotExist:
        return Response({"message": "Utilisateur non trouvé"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        # Génération d'un nouveau mot de passe aléatoire
        new_password = ''.join(random.choices(string.ascii_letters + string.digits + string.punctuation, k=8))
        
        # Mise à jour du mot de passe dans la base de données
        user.password = make_password(new_password)
        user.reset_password = False
        user.save()
        
        return Response({"message": "Mot de passe réinitialisé avec succès", "new_password": new_password}, status=status.HTTP_200_OK)

    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
