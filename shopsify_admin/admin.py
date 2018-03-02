from django.contrib import admin
from shopsify_admin.models import *
from django.contrib.auth.models import Group
from django.contrib.auth.admin import GroupAdmin


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name','last_name')


class UserSetInline(admin.TabularInline):
    model = User.groups.through
    #raw_id_fields = ('user',)  # optional, if you have too many users

class CustomGroupAdmin(GroupAdmin):
    #inlines = [UserSetInline]
    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        if db_field.name == 'permissions':
            qs = kwargs.get('queryset', db_field.remote_field.model.objects)
            qs = qs.exclude(codename__in=(
                'add_permission',
                'change_permission',
                'delete_permission',
                'add_contenttype',
                'change_contenttype',
                'delete_contenttype',

                'add_session',
                'delete_session',
                'change_session',

                'add_logentry',
                'change_logentry',
                'delete_logentry',
            ))
            # Avoid a major performance hit resolving permission names which
            # triggers a content_type load:
            kwargs['queryset'] = qs.select_related('content_type')
        return super(GroupAdmin, self).formfield_for_manytomany(
            db_field, request=request, **kwargs)


class ProductAdmin(admin.ModelAdmin):
    list_display = ('url', 'website', 'title',)



admin.site.unregister(Group)

admin.site.register(UserGroups,CustomGroupAdmin)
admin.site.register(User)
admin.site.register(ShopifyProductModel, ProductAdmin)
admin.site.register(ShopifySettingsModel)
admin.site.register(ShopifySiteCategoryModel)
admin.site.register(ShopifySiteModel)