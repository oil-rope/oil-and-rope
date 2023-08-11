from typing import TYPE_CHECKING, Protocol

import django.db.models
import django.forms.forms
import django.http.request

if TYPE_CHECKING:
    class HasRequestProtocol(Protocol):
        """
        Declares for a class that has `request` object. Basically a typing for :class:`django.view.base.View`.
        """

        @property
        def request(self) -> django.http.request.HttpRequest: ...

    class HasModelProtocol(Protocol):
        """
        Declares for a CBW that interacts with models. This basically everything that inherits from
        :class:`django.views.generic.detail.SingleObjectMixin`.
        """

        @property
        def model(self) -> django.db.models.Model: ...

    class HasObjectProtocol(Protocol):
        """
        Declares for a CBW that has an object. This basically everything that inherits from
        :class:`django.views.generic.detail.BaseDetailView`.
        """

        @property
        def object(self) -> django.db.models.Model: ...

    class HasFormMixinLogic(Protocol):
        """
        Declares for a CBW that has an object. This basically everything that inherits from
        :class:`django.views.generic.detail.FormMixin`.
        """

        def form_valid(self, form: django.forms.forms.Form) -> django.http.HttpResponseRedirect: ...
        def form_invalid(self, form: django.forms.forms.Form) -> django.http.HttpResponse: ...
else:
    class HasRequestProtocol(Protocol):
        ...

    class HasModelProtocol(Protocol):
        ...

    class HasObjectProtocol(Protocol):
        ...

    class HasFormMixinLogic(Protocol):
        ...
