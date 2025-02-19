from django.urls import path
from .views import SignupView, LoginView, OTPSendView, OTPVerifyView,DashboardView

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('otp/send/', OTPSendView.as_view(), name='otp-send'),
    path('otp/verify/', OTPVerifyView.as_view(), name='otp-verify'),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
]
