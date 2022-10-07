from rest_framework import serializers


class ApiVersionSerializer(serializers.Serializer):
    version = serializers.CharField(required=True)
    powered_by = serializers.CharField(required=True)
    drf_version = serializers.CharField(required=True)
    using_version = serializers.CharField(required=False)


class URLResolverSerializer(serializers.Serializer):
    """
    Serializer for getting URL from resolver.

    Parameters
    ----------
    resolver: :class:`str`
        Resolver name.
    params: :class:`dict`
        Any parameters to pass to resolver.
    """

    resolver = serializers.CharField(required=True)
    params = serializers.DictField(required=False)


class URLResolverResponseSerializer(serializers.Serializer):
    """
    Serializer for resulting URL from resolver.
    This specific serializer is used for DRF-YASG.

    Parameters
    ----------
    url: :class:`str`
        Resolved URL.
    """

    url = serializers.CharField(required=True)


class DiceRollSerializer(serializers.Serializer):
    """
    Serializer for rolling dice.

    Parameters
    ----------
    roll: :class:`str`
        Dice notation.
    """

    roll = serializers.CharField(required=True)


class DiceRollResponseSerializer(serializers.Serializer):
    """
    Serializer for resulting dice roll.
    This specific serializer is used for DRF-YASG.

    Parameters
    ----------
    result: :class:`int`
        Result of dice roll.
    rolls: :class:`dict`
        Dictionary of rolls with results.
    """

    result = serializers.IntegerField(required=True)
    rolls = serializers.DictField(required=True)
