from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from .models import *


class AccountAdmin(UserAdmin):
    list_display = ('email', 'name', 'last_login', 'is_admin', 'is_applicant', 'is_company')
    search_fields = ('email', 'name')
    readonly_fields = ('date_joined', 'last_login')

    filter_horizontal = ()
    ordering = ('email',)
    # list_filter = ()
    fieldsets = ()
    list_filter = ('is_admin', 'is_active', 'is_applicant', 'is_company')
    # fieldsets = (
    #     (None, {'fields': ('email', 'password', 'date_joined', 'last_login', )}),
    #     ('Info', {'fields': ('name',)}),
    #     ('Permissions', {'fields': ('is_admin', 'is_applicant' 'is_company')}),
    # )


class ApplicantProfileAdmin(UserAdmin):
    list_display = ('user', 'phone', 'gender',)
    search_fields = ('user',)
    readonly_fields = ()

    filter_horizontal = ()
    ordering = ()
    fieldsets = ()
    list_filter = ('gender',)


class SkillSetAdmin(UserAdmin):
    list_display = ('user', 'skill_title', 'proficiency')
    search_fields = ('user', 'skill_title',)
    readonly_fields = ()

    filter_horizontal = ()
    ordering = ()
    fieldsets = ()
    list_filter = ()



admin.site.register(User, AccountAdmin)
admin.site.register(ApplicantProfileModel, ApplicantProfileAdmin)
admin.site.register(CompanyProfileModel)
admin.site.register(WorkExperienceModel)
admin.site.register(EducationModel)
admin.site.register(SkillSetModel, SkillSetAdmin)
admin.site.register(ReferenceModel)
admin.site.register(LanguageModel)
admin.site.register(AwardModel)
