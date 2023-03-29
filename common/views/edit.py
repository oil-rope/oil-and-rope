from typing import Any, Callable, Optional, cast

from django.contrib.admin.utils import NestedObjects
from django.db import models, router
from django.views.generic.edit import DeleteView


class DeletedObjectsView(DeleteView):
    """
    This view works the same as :class:`~django.views.generic.edit.DeleteView` but with the additional of adding to the
    context all related objects that will be also deleted (because of CASCADE).
    Also a base template is generated using the model as contextual object for creating title and dynamic information.
    """

    template_name = 'common/layout/base_confirm_delete.html'

    def get_deleted_objects(
            self,
            obj: Optional[models.Model] = None,
    ):
        """
        Gets the objects that are going to be deleted because of CASCADE from given `obj`.
        If `obj` is not given then it will fallback into
        :method:`~django.views.generic.detail.SingleObjectMixin.get_object`.
        """

        if not obj:
            obj = cast(models.Model, self.object)

        using = router.db_for_write(obj._meta.model)
        obj_as_list = [obj]  # Since `NestedObjects` requires a list we parse it
        collector = NestedObjects(using=using, origin=obj_as_list)
        collector.collect(obj_as_list)

        to_delete = collector.nested(self.get_format_callback())

        return to_delete

    def get_format_callback(self) -> Optional[Callable[[models.Model], str]]:
        """
        Placeholder that will allow to return a function that will be used to format the output on the entities to
        delete.

        Returns
        ----------
        format_func: :class:`Callable[[models.Model], str]`
            The function use for getting the format. It's mandatory to receive one parameter that will be the object.
        """

        return None

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context_data = super().get_context_data(**kwargs)
        context_data.update({
            'to_delete': self.get_deleted_objects(),
        })
        return context_data
