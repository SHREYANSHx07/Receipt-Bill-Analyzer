from django.urls import path
from . import views

app_name = 'processor'

urlpatterns = [
    # File upload and parsing
    path('upload/', views.UploadView.as_view(), name='upload'),
    
    # Record management
    path('records/', views.RecordListView.as_view(), name='records'),
    path('records/<uuid:id>/', views.RecordDetailView.as_view(), name='record_detail'),
    
    # Search functionality
    path('search/', views.SearchView.as_view(), name='search'),
    
    # Statistics
    path('stats/', views.StatsView.as_view(), name='stats'),
    
    # Export functionality
    path('export/', views.export_data, name='export'),
    
    # Data management
    path('clear/', views.clear_all_data, name='clear_all_data'),
] 