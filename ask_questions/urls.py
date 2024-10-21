from django.contrib import admin
from django.urls import path, re_path
from django.conf import settings
from django.views.static import serve
from ask_questions_app import views as v1

urlpatterns = [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
    path('admin/', admin.site.urls),
    path('', v1.index, name='index'),
    path('api/get_reddit_answers/', v1.get_reddit_answers, name='get_reddit_answers'),
    path('api/get_stackoverflow_answers/', v1.get_stackoverflow_answers, name='get_stackoverflow_answers'),
    path('translate-question/', v1.translate_question, name='translate_question'),
    path('generate-report/', v1.generate_report_and_send_email, name='generate_report'),
    path('speak/', v1.speak_text, name='speak'),
]
