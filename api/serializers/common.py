class MappedSerializerMixin:
    """
    This serializer allows to have more than one representation for an specific field.
    This intended to solve thing as JSON FullUser vs PrimaryKey value.

    Parameters
    ----------
    serializers_map: :class:`str`:
        Dictionary with field name and value to substitude.
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
                mapped_fields[field] = self.serializers_map[field]
        return mapped_fields

    def get_fields(self):
        fields = super(MappedSerializerMixin, self).get_fields()
        fields = self.override_fields(fields)
        return fields
