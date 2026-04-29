from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('login/',  views.dashboard_login,  name='login'),
    path('logout/', views.dashboard_logout, name='logout'),
    path('',        views.dashboard_home,   name='home'),

    # Pages
    path('pages/',                  views.pages_list,   name='pages_list'),
    path('pages/create/',           views.pages_create, name='pages_create'),
    path('pages/<int:pk>/edit/',    views.pages_edit,   name='pages_edit'),
    path('pages/<int:pk>/delete/',  views.pages_delete, name='pages_delete'),

    # Blog
    path('blog/',                            views.blog_list,           name='blog_list'),
    path('blog/create/',                     views.blog_create,         name='blog_create'),
    path('blog/<int:pk>/edit/',              views.blog_edit,           name='blog_edit'),
    path('blog/<int:pk>/delete/',            views.blog_delete,         name='blog_delete'),
    path('blog/categories/',                 views.blog_categories,     name='blog_categories'),
    path('blog/categories/create/',          views.blog_cat_create,     name='blog_category_create'),
    path('blog/categories/<int:pk>/edit/',   views.blog_cat_edit,       name='blog_category_edit'),
    path('blog/categories/<int:pk>/delete/', views.blog_cat_delete,     name='blog_category_delete'),

    # Enquiries
    path('enquiries/',                 views.enquiry_list,   name='enquiry_list'),
    path('enquiries/<int:pk>/',        views.enquiry_detail, name='enquiry_detail'),
    path('enquiries/<int:pk>/delete/', views.enquiry_delete, name='enquiry_delete'),

    # Portfolio
    path('portfolio/',                              views.portfolio_list,       name='portfolio_list'),
    path('portfolio/categories/',                   views.portfolio_categories, name='portfolio_categories'),
    path('portfolio/categories/create/',            views.portfolio_cat_create, name='portfolio_cat_create'),
    path('portfolio/categories/<int:pk>/edit/',     views.portfolio_cat_edit,   name='portfolio_cat_edit'),
    path('portfolio/categories/<int:pk>/delete/',   views.portfolio_cat_delete, name='portfolio_cat_delete'),
    path('portfolio/items/create/',                 views.portfolio_create,     name='portfolio_item_create'),
    path('portfolio/items/<int:pk>/edit/',          views.portfolio_edit,       name='portfolio_item_edit'),
    path('portfolio/items/<int:pk>/delete/',        views.portfolio_delete,     name='portfolio_item_delete'),

    # Careers
    path('careers/',                 views.careers_list,   name='careers_list'),
    path('careers/create/',          views.careers_create, name='careers_create'),
    path('careers/<int:pk>/edit/',   views.careers_edit,   name='careers_edit'),
    path('careers/<int:pk>/delete/', views.careers_delete, name='careers_delete'),

    # Contact
    path('contact/', views.contact_info, name='contact_info'),

    # About — Info
    path('about/', views.about_info, name='about_info'),

    # About — Strengths
    path('about/strengths/',                 views.strengths_list,  name='strengths_list'),
    path('about/strengths/create/',          views.strength_create, name='strength_create'),
    path('about/strengths/<int:pk>/edit/',   views.strength_edit,   name='strength_edit'),
    path('about/strengths/<int:pk>/delete/', views.strength_delete, name='strength_delete'),

    # About — Milestones
    path('about/milestones/',                 views.milestones_list,  name='milestones_list'),
    path('about/milestones/create/',          views.milestone_create, name='milestone_create'),
    path('about/milestones/<int:pk>/edit/',   views.milestone_edit,   name='milestone_edit'),
    path('about/milestones/<int:pk>/delete/', views.milestone_delete, name='milestone_delete'),

    # About — Team
    path('about/team/',                 views.team_list,   name='team_list'),
    path('about/team/create/',          views.team_create, name='team_create'),
    path('about/team/<int:pk>/edit/',   views.team_edit,   name='team_edit'),
    path('about/team/<int:pk>/delete/', views.team_delete, name='team_delete'),

    # About — Gallery
    path('about/gallery/',                   views.gallery_list,   name='gallery_list'),
    path('about/gallery/upload/',            views.gallery_upload, name='gallery_upload'),
    path('about/gallery/<int:pk>/delete/',   views.gallery_delete, name='gallery_delete'),

    # About — Projects
    path('about/projects/',                  views.projects_list,  name='projects_list'),
    path('about/projects/create/',           views.project_create, name='project_create'),
    path('about/projects/<int:pk>/edit/',    views.project_edit,   name='project_edit'),
    path('about/projects/<int:pk>/delete/',  views.project_delete, name='project_delete'),

    # AJAX
    path('ajax/toggle/', views.ajax_toggle, name='ajax_toggle'),
]