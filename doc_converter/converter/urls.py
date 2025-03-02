from django.urls import path
from .views import ConversionHistoryView, ConversionHistoryDeleteUpdateView, ConversionListCreateView, AdminConversionHistoryView

urlpatterns = [
    path("convert/", ConversionListCreateView.as_view(), name="convert"),
    path("history/", ConversionHistoryView.as_view(), name="conversion-history"),
    path("history/<int:pk>/", ConversionHistoryDeleteUpdateView.as_view(), name="conversion-detail"),
    path("history/all/", AdminConversionHistoryView.as_view(), name="all-history"),
    
]


