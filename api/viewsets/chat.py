from distutils.util import strtobool as to_bool

from django.contrib.auth import get_user_model
from django.db.models import QuerySet
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import mixins, status, viewsets
from rest_framework.request import Request
from rest_framework.response import Response

from chat.models import Chat, ChatMessage

from ..serializers.chat import (ChatMessageRequestSerializer, ChatMessageSerializer, ChatSerializer,
                                NestedChatMessageSerializer, NestedChatSerializer)

User = get_user_model()


@extend_schema_view(
    list=extend_schema(summary='List chats', description='List all chats user is member of.'),
)
class ChatViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer

    def get_queryset(self) -> QuerySet:
        user = self.request.user
        qs = super().get_queryset().filter(
            users__in=[user],
        )
        return qs

    @extend_schema(
        summary='Get chat',
        parameters=[
            OpenApiParameter(
                name='nested', type=bool, location=OpenApiParameter.QUERY,
                description='If true, returns chat with messages as JSON instead of IDs.',
            )
        ],
        examples=[
            OpenApiExample(
                name='Retrieve messages as IDs',
                response_only=True,
                value={
                    'id': 1,
                    'name': 'Example Chat 1',
                    'users': [1, 2],
                    'chat_message_set': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                    'entry_created_at': '2020-01-01T00:00:00Z',
                    'entry_updated_at': '2020-01-01T00:00:00Z',
                },
            ),
            OpenApiExample(
                name='Retrieve messages as JSON',
                response_only=True,
                value={
                    'id': 1,
                    'name': 'Example Chat 1',
                    'users': [1, 2],
                    'chat_message_set': [
                        {
                            'id': 1,
                            'chat': 1,
                            'message': 'Hello, world!',
                            'author': {
                                'id': 1,
                                'username': 'admin',
                                'email': 'admin@oilandrope-project.com',
                                'first_name': 'Admin',
                                'last_name': 'Oil & Rope',
                            },
                            'entry_created_at': '2020-01-01T00:00:00Z',
                            'entry_updated_at': '2020-01-01T00:00:00Z',
                        },
                    ],
                    'entry_created_at': '2020-01-01T00:00:00Z',
                    'entry_updated_at': '2020-01-01T00:00:00Z',
                },
            ),
        ],
    )
    def retrieve(self, request: Request, *args, **kwargs):
        """
        Retrieve chat by given ID if user is member of it.
        """

        if to_bool(request.query_params.get('nested', 'false')):
            self.serializer_class = NestedChatSerializer
        return super().retrieve(request, *args, **kwargs)


@extend_schema(
    parameters=[
        OpenApiParameter(
            name='chat_pk', type=int, location=OpenApiParameter.PATH,
            description='A unique integer value identifying this chat.',
        ),
    ]
)
@extend_schema_view(
    retrieve=extend_schema(summary='Get message', description='Get message in given chat ID by given ID.'),
)
class ChatMessageNestedViewSet(mixins.CreateModelMixin, viewsets.ReadOnlyModelViewSet):
    queryset = ChatMessage.objects.all()
    serializer_class = NestedChatMessageSerializer

    def get_queryset(self):
        qs = super().get_queryset().filter(
            chat__id=self.kwargs['chat_pk'],
            chat__users__in=[self.request.user],
        )
        return qs

    @extend_schema(
        summary='List messages',
        parameters=[
            OpenApiParameter(
                name='nested', type=bool, location=OpenApiParameter.QUERY,
                description='If true, returns author as JSON instead of ID.',
            )
        ],
        examples=[
            OpenApiExample(
                name='Retrieve author as ID',
                response_only=True,
                value={
                    'id': 1,
                    'chat': 1,
                    'message': 'Hello, world!',
                    'author': 1,
                    'entry_created_at': '2020-01-01T00:00:00Z',
                    'entry_updated_at': '2020-01-01T00:00:00Z',
                },
            ),
            OpenApiExample(
                name='Retrieve author as JSON',
                response_only=True,
                value={
                    'id': 1,
                    'chat': 1,
                    'message': 'Hello, world!',
                    'author': {
                        'id': 1,
                        'username': 'admin',
                        'email': 'admin@oilandrope-project.com',
                        'first_name': 'Admin',
                        'last_name': 'Oil & Rope',
                    },
                    'entry_created_at': '2020-01-01T00:00:00Z',
                    'entry_updated_at': '2020-01-01T00:00:00Z',
                },
            ),
        ],
    )
    def list(self, request: Request, *args, **kwargs) -> Response:
        """
        Retrieve messages for given chat ID.
        """

        if not to_bool(request.query_params.get('nested', 'false')):
            self.serializer_class = ChatMessageSerializer
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary='Create message',
        request=ChatMessageRequestSerializer,
    )
    def create(self, request: Request, *args, **kwargs) -> Response:
        """
        Create message for given chat ID.
        Message will be created for current user.
        """

        # NOTE: We rewrite the create method to make sure that chat is valid and author is current user.
        self.serializer_class = ChatMessageRequestSerializer
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        new_msg_serializer = NestedChatMessageSerializer(obj)
        return Response(new_msg_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer) -> ChatMessage:
        # Regular user should not be able to set other author than themselves
        return serializer.save(author=self.request.user, chat_id=self.kwargs['chat_pk'])


class ChatMessageViewSet(viewsets.GenericViewSet):
    queryset = ChatMessage.objects.all()
    serializer_class = NestedChatMessageSerializer

    def get_queryset(self) -> QuerySet:
        qs = super().get_queryset().filter(
            author=self.request.user,
        )
        return qs

    @extend_schema(
        summary='Update message',
        request=ChatMessageRequestSerializer,
    )
    def partial_update(self, request: Request, *args, **kwargs) -> Response:
        """
        Update content of given message.
        """

        data_serializer = ChatMessageRequestSerializer(data=request.data)
        data_serializer.is_valid(raise_exception=True)
        serializer = self.get_serializer(self.get_object(), data=data_serializer.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data)
