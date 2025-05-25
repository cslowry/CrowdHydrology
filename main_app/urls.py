from django.urls import path

from main_app import graphs, receive_sms, survey, views

# Template Urls
app_name = "main_app"

urlpatterns = [
    path("sms/", receive_sms.incoming_sms, name="sms"),
    path("survey/", survey.incoming_survey, name="survey"),
    path("", views.index, name="index"),
    path("generate-graphs/", graphs.generate, name="generate-graphs"),
    path("data/", views.get_data, name="get-data"),
    path("download/", views.download, name="download"),
    # path('user_login/', views.user_login, name='user_login')
]
