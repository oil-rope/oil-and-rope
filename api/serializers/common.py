from rest_framework import serializers


class MappedSerializerMixin:
    """
    This serializer allows to have more than one representation for an specific field.
    This intended to solve thing as JSON FullUser vs PrimaryKey value.

    Parameters
    ----------
    serializers_map: :class:`str`:
        Dictionary with field name and value to substitute.
    """

    serializers_map = None

    def __init__(self, *args, map_fields=None, **kwargs):
        """
        map_fields: :class:`list`
            List of fields to map. This fields must be registered in `serializers_map`.
        """

        self.map_fields = map_fields
        super(MappedSerializerMixin, self).__init__(*args, **kwargs)

    def override_fields(self, fields):
        mapped_fields = fields.copy()
        if self.map_fields:
            for field in self.map_fields:
                override_field = self.serializers_map[field]
                # TODO: This error is special due to RestFramework behavior, we gotta test it somehow
                if getattr(override_field, 'source', None) == field:  # pragma: no cover
                    # Avoiding AssertionError
                    setattr(override_field, 'source', None)
                mapped_fields[field] = override_field
        return mapped_fields

    def get_fields(self):
        fields = super().get_fields()
        fields = self.override_fields(fields)
        return fields


class WebSocketMessageSerializer(serializers.Serializer):
    """
    This serializer is used to send messages to the client.

    Parameters
    ----------
    type: :class:`str`
        Type of execution.
    """

    type = serializers.CharField(max_length=255, required=True)
    content = serializers.DictField(required=False)
