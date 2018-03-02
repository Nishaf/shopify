from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from .views import *

urlpatterns = [
    url(r'^$', login_required(Homepage.as_view(), login_url='login'), name='index'),
    url(r'^product_extractor/$', login_required(ProductExtractor.as_view(), login_url='login'), name='product_extractor'),
    url(r'^categories/$', login_required(ViewCategories.as_view(), login_url='login'), name='show_categories'),
    url(r'^view_category/$', login_required(ViewCategory.as_view(), login_url='login'), name='view_category'),
    url(r'^product/$', login_required(ViewProduct.as_view(), login_url='login'), name='view_product'),
    url(r'^products/$', login_required(ViewProducts.as_view(), login_url='login'), name='show_products'),
    url(r'^edit-settings/$', login_required(EditSettings.as_view(), login_url='login'), name='edit_settings'),
    url(r'^settings/$', login_required(ConfigureSettings.as_view(), login_url='login'), name='configure_settings'),
    url(r'^add_site/$', login_required(AddSites.as_view(), login_url='login'), name='add_site'),
    url(r'^sites/$', login_required(ViewSites.as_view(), login_url='login'), name='show_sites'),
    url(r'^add_user/$', login_required(AddUser.as_view(), login_url='login'), name='add_user'),
    url(r'^edit_user/$', login_required(EditUser.as_view(), login_url='login'), name='edit_user'),
    url(r'^delete_user/$', login_required(DeleteUser.as_view(), login_url='login'), name='delete_user'),
    url(r'^edit_password/$', login_required(EditPassword.as_view(), login_url='login'), name='edit_password'),
    url(r'^profile/$', login_required(UserProfile.as_view(), login_url='login'), name='profile'),
    url(r'^users/$', login_required(ViewUsers.as_view(), login_url='login'), name='show_users'),
    url(r'^search/$', login_required(Search.as_view(), login_url='login'), name='search'),
    url(r'^delete_group_user/$', login_required(DeleteGroupUser.as_view(), login_url='login'), name='delete_group_user'),
    url(r'^add_group_user/$', login_required(AddGroupUser.as_view(), login_url='login'), name='add_group_user'),
    url(r'^delete_group/$', login_required(DeleteGroup.as_view(), login_url='login'), name='delete_group'),
    url(r'^edit_group/$', login_required(EditGroup.as_view(), login_url='login'), name='edit_group'),
    url(r'^add_group/$', login_required(AddGroup.as_view(), login_url='login'), name='add_group'),
    url(r'^groups/$', login_required(Groups.as_view(), login_url='login'), name='show_groups'),
    url(r'^login/$', Login.as_view(), name='login'),
    url(r'^logout/$', Logout.as_view(), name='logout'),
    url(r'^signup/$', SignUp.as_view(), name='signup')
]

#(?P<product_title>.+)