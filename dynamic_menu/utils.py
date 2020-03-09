from django.db import models


def populate(data, model: models.Model) -> list:
    """
    Reads a list and checks for children entries.

    Parameters
    ----------
    data: :class:`list`
        The result of reading a JSON file.
    model: :class:`models.Model`
        The model used to create the structure.

    Returns
    -------
    children: :class:`list`
        A list with all children created if there's any.
    """

    children = []

    for record in data:
        # Check for children
        if 'children' in record:
            children_data = record.pop('children', [])
            obj = model.objects.create(**record)
            obj_children = populate(children_data, model)
            for child in obj_children:
                child.parent = obj
                child.save()
        # If not children, just create
        else:
            obj = model.objects.create(**record)
        # Adding record
        children.append(obj)

    return children
