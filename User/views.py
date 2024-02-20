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

# Méthode pour enregistrer un utilisateur
@api_view(['POST'])
def user_registration(request):
    """
    Enregistre un nouvel utilisateur.
    
    Paramètres:
    - request : HttpRequest - la requête HTTP contenant les données de l'utilisateur à enregistrer.

    Retour:
    - HttpResponse : réponse HTTP avec le statut approprié et un message indiquant si l'utilisateur a été enregistré avec succès ou non.
    """
    if request.method == 'POST':
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            existing_user = User.objects.filter(email=request.data.get('email')).exists()
            if existing_user:
                return Response({"message": "Cet utilisateur existe déjà."}, status=status.HTTP_400_BAD_REQUEST)
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
    - request : HttpRequest - la requête HTTP contenant les informations d'identification de l'utilisateur (email et mot de passe).

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

        if user is not None and check_password(password, user.password):
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        else:
            return Response({'message': 'Email ou mot de passe incorrect'}, status=status.HTTP_401_UNAUTHORIZED)
    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

# Méthodes pour récupérer, mettre à jour et supprimer un utilisateur spécifique
@api_view(['GET', 'PUT', 'DELETE'])
def user_detail(request, cin):
   
    try:
        user = User.objects.get(cin=cin)
    except User.DoesNotExist:
        return Response({'message': 'Utilisateur non trouvé'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = UserSerializer(user)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



# Méthode pour vérifier l'existence d'un email
@api_view(['GET'])
def check_email(request):
   
    if request.method == 'GET':
        emails = request.GET.get('email')
        existing_user = User.objects.filter(email=emails).exists()
        return Response({"exists": existing_user}, status=status.HTTP_200_OK)

# Méthode pour vérifier l'existence d'un identifiant (cin)
@api_view(['GET'])
def check_identifient(request):
    
    if request.method == 'GET':
        identifient = request.GET.get('cin')
        existing_user = User.objects.filter(cin=identifient).exists()
        return Response({"exists": existing_user}, status=status.HTTP_200_OK)
