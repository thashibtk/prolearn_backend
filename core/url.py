from django.urls import path
from .views import AdminProfileView, SignupView, LoginView, OTPSendView, OTPVerifyView,DashboardView, UpdateUserView,create_user, delete_user, get_users,AdminLoginView, AdminLogoutView,toggle_freeze_user 

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('otp/send/', OTPSendView.as_view(), name='otp-send'),
    path('otp/verify/', OTPVerifyView.as_view(), name='otp-verify'),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),

    path('admin/create-user/', create_user, name="create-user"),
    path('admin/users/', get_users, name="get-users"),
    path('admin-login/', AdminLoginView.as_view(), name="admin-login"),
    path("admin/logout/", AdminLogoutView.as_view(), name="admin-logout"),
    path("admin/profile/", AdminProfileView.as_view(), name="admin-profile"),
    path("admin/delete-user/<int:user_id>/", delete_user, name="delete-user"),
    path("admin/update-user/<int:user_id>/", UpdateUserView.as_view(), name="update-user"),
    path('admin/toggle-freeze/<int:user_id>/', toggle_freeze_user, name='toggle-freeze'),
    
]
