from django.db.models import QuerySet
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import mixins, status, viewsets
from rest_framework.request import Request
from rest_framework.response import Response

from chat.models import Chat, ChatMessage

from ..serializers.chat import (ChatMessageCreateRequestSerializer, ChatMessageSerializer,
                                ChatMessageUpdateRequestSerializer, ChatSerializer)


@extend_schema_view(
    list=extend_schema(summary='List chats', description='List all chats user is member of.'),
    retrieve=extend_schema(summary='Get chat', description='Retrieve chat by given ID if user is member of it.')
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


@extend_schema(parameters=[
    OpenApiParameter(
        name='chat_pk', type=int, location=OpenApiParameter.PATH,
        description='A unique integer value identifying this chat.',
    ),
])
@extend_schema_view(
    list=extend_schema(summary='List messages', description='Retrieve messages for given chat ID.'),
    retrieve=extend_schema(summary='Get message', description='Get message in given chat ID by given ID.'),
)
class ChatMessageViewSet(mixins.CreateModelMixin, viewsets.ReadOnlyModelViewSet):
    queryset = ChatMessage.objects.all()
    serializer_class = ChatMessageSerializer

    def get_queryset(self) -> QuerySet:
        qs: QuerySet = super().get_queryset().filter(
            chat__id=self.kwargs['chat_pk'],
            chat__users__in=[self.request.user],
        )
        qs = qs.order_by('-entry_created_at')
        # User can only edit their own messages
        if self.action == 'partial_update':
            qs = qs.filter(author=self.request.user)
        return qs

    @extend_schema(
        summary='Create message',
        request=ChatMessageCreateRequestSerializer,
    )
    def create(self, request: Request, *args, **kwargs) -> Response:
        """
        Create message for given chat ID.
        Message will be created for current user.
        """

        # NOTE: We rewrite the create method to make sure that chat is valid and author is current user.
        serializer = ChatMessageCreateRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        new_msg_serializer = self.get_serializer(instance=obj)
        return Response(new_msg_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @extend_schema(
        summary='Update message',
        request=ChatMessageUpdateRequestSerializer,
    )
    def partial_update(self, request: Request, *args, **kwargs) -> Response:
        """
        Update content of given message.
        """

        data_serializer = ChatMessageUpdateRequestSerializer(data=request.data)
        data_serializer.is_valid(raise_exception=True)
        serializer = self.get_serializer(instance=self.get_object(), data=data_serializer.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data)

    def perform_create(self, serializer) -> ChatMessage:
        # Regular user should not be able to set other author than themselves
        return serializer.save(author=self.request.user, chat_id=self.kwargs['chat_pk'])
