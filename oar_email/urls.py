from django.urls import path

from oar_email import views

app_name = 'oar_email'

urlpatterns = [
    path('<path:mail_template>', views.EmailView.as_view(), name='template'),
]
