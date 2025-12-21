from django.urls import path

from . import views

app_name = 'game'
urlpatterns = [
    path('travel/start/<slug:global_location_slug>/<slug:sublocation_slug>/', views.start_travel, name='start_travel'),

    path('travel_status/', views.travel_status, name='travel_status'),


    path('teleport/<slug:global_location_slug>/<slug:sublocation_slug>/', views.teleport, name='teleport'),

    path('hunting-zones/<slug:global_location_slug>/<slug:sublocation_slug>', views.sublocation, name='sublocation'),
    

    path('hunting-zones/<slug:global_location_slug>/<slug:sublocation_slug>/<slug:monster_slug>/', views.attack_monster, name='attack_monster'),

    path('hunting-zones/<slug:global_location_slug>/', views.sublocations_list, name='sublocations_list'),
    path('hunting-zones/', views.hunting_zones, name='hunting_zones'),
    path('city/', views.city, name='city'),
    path('city/<slug:sublocation_slug>/', views.city_sublocation, name='city_sublocation'),
    path('trader/test/', views.trader_test, name='trader_test'), # Тестовая страница торговца
    path('trade/', views.trade_view, name='trade'),
]