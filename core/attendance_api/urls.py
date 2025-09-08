# from django.urls import path
# from .views import EnrollView, VerifyView, TaskResultView

# urlpatterns = [
#     path('enroll/', EnrollView.as_view(), name='enroll'),
#     path('verify/', VerifyView.as_view(), name='verify'),
#     path('result/<str:task_id>/', TaskResultView.as_view(), name='task-result'),
# ]
from django.urls import path
from .views import EnrollView, VerifyView, TaskResultView

urlpatterns = [
    path('enroll/', EnrollView.as_view(), name='enroll'),
    path('verify/', VerifyView.as_view(), name='verify'),
    path('task-result/<str:task_id>/', TaskResultView.as_view(), name='task-result'),
]