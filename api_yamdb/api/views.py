from rest_framework import status, filters, viewsets, mixins
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from rest_framework_simplejwt.tokens import AccessToken
from django.db.models import Avg

from reviews.models import User, Title, Genre, Category, Review
from .filters import TitleFilter
from .serializers import (
    UserSerializer,
    SignupSerializer,
    TokenSerializer,
    CategorySerializer,
    GenreSerializer,
    CreateTitleSerializer,
    TitleSerializer,
    ReviewSerializer,
    CommentSerializer,
)
from .permissions import IsAdmin, IsAdminOrRead, IsAdminOrModeratorOrRead
from api_yamdb.settings import DEFAULT_FROM_EMAIL, SUBJECT, MESSAGE

MIXINS_VIEWSET_LIST = (
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'
    permission_classes = (IsAdmin,)

    @action(
        methods=['get', 'patch'],
        detail=False,
        permission_classes=(IsAuthenticated,),
    )
    def me(self, request):
        if request.method == 'GET':
            serializer = UserSerializer(request.user)
            return Response(serializer.data)
        serializer = UserSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(role=request.user.role)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    serializer = SignupSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user, created = User.objects.get_or_create(
        email=serializer.validated_data['email'],
        username=serializer.validated_data['username'],
    )
    confirmation_code = default_token_generator.make_token(user)

    send_mail(
        SUBJECT,
        MESSAGE.format(confirmation_code),
        DEFAULT_FROM_EMAIL,
        [user.email],
    )
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def get_token(request):
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = get_object_or_404(
        User,
        username=serializer.validated_data['username'],
    )
    if not default_token_generator.check_token(
            user,
            serializer.validated_data['confirmation_code']):
        return Response(status=status.HTTP_400_BAD_REQUEST)
    token = AccessToken.for_user(user)
    data = {
        'token': str(token),
    }
    return Response(data)


class CategoryViewSet(*MIXINS_VIEWSET_LIST):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrRead]
    filter_backends = (filters.SearchFilter,)
    search_fields = ('=name',)
    lookup_field = ('slug')


class GenreViewSet(*MIXINS_VIEWSET_LIST):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    filter_backends = [filters.SearchFilter]
    permission_classes = [IsAdminOrRead]
    search_fields = ('=name',)
    lookup_field = ('slug')


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all().annotate(
        rating=Avg('reviews__score')).order_by('-id')
    permission_classes = [IsAdminOrRead]
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return CreateTitleSerializer
        return TitleSerializer


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAdminOrModeratorOrRead,)

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        review_id = self.kwargs.get('review_id')

        return (get_object_or_404(Review, id=review_id, title_id=title_id)
                .comments.all())

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        review_id = self.kwargs.get('review_id')

        review = get_object_or_404(Review, id=review_id, title_id=title_id)
        serializer.save(author=self.request.user, review=review)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (IsAdminOrModeratorOrRead,)

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        return get_object_or_404(Title, id=title_id).reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)
