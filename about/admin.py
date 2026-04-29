from django.contrib import admin
from .models import About, Strength, Milestone, Project, Gallery, TeamMember

@admin.register(About)
class AboutAdmin(admin.ModelAdmin):
    list_display    = ['title', 'founded_year', 'employee_count', 'updated_at']
    readonly_fields = ['updated_at']

@admin.register(Strength)
class StrengthAdmin(admin.ModelAdmin):
    list_display  = ['title', 'icon', 'order', 'is_active']
    list_filter   = ['is_active']
    search_fields = ['title']
    ordering      = ['order']

@admin.register(Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    list_display  = ['year', 'title', 'tags', 'order']
    ordering      = ['year', 'order']
    search_fields = ['title', 'tags']

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display  = ['title', 'client', 'tag', 'year', 'is_featured', 'created_at']
    list_filter   = ['is_featured', 'year']
    search_fields = ['title', 'client', 'tag']

@admin.register(Gallery)
class GalleryAdmin(admin.ModelAdmin):
    list_display = ['title', 'order', 'is_active', 'created_at']
    list_filter  = ['is_active']

@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display  = ['name', 'role', 'social_platform', 'order', 'is_active']
    list_filter   = ['is_active', 'social_platform']
    search_fields = ['name', 'role']
    ordering      = ['order']