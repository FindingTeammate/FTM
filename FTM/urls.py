from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("User",views.UserView)
router.register("Profile", views.ProfileView)
router.register("WorkExp", views.WorkExpView)
router.register("Reviews", views.ReviewsView)

urlpatterns = [
    path('api/', include(router.urls), name = 'create-profile'),
    path("get-details/",views.UserDetailAPI.as_view(), name = "get-details"),
    path('register/', views.RegisterUserAPIView.as_view(), name = "register"),
    path('get-profile/', views.GetProfile.as_view(), name = 'get-profile'),
]
