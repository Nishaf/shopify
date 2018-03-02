from django.shortcuts import render, redirect, HttpResponse
from django.views.generic import View
from django.contrib.auth import authenticate, login, logout
from .models import *
from django.http import JsonResponse
from .forms import UserForm, SettingsForm, AddSiteForm, ProfileForm, PasswordForm, ProductExtractorForm, EditUserForm, GroupForm
import io, csv
from django.utils.encoding import smart_text
from shopify.views import start
from providers.request_browser import Browser
from shopify_scrapers.shopify_product import SProduct

product_extractor = SProduct()
download_browser = Browser()


class Homepage(View):
    def get(self, request):
        if request.user.is_authenticated:
            return render(request, 'app-blog-single.html', {'user': User.objects.get(username=request.user)})
        else:
            return render(request, 'page-login.html')


class Login(View):
    def get(self, request):
        return render(request, 'page-login.html')

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('index')
            else:
                return render(request, 'page-login.html', {'message': 'Invalid login'})
        print('invalid')
        return render(request, 'page-login.html', {'message': 'Invalid login'})


class SignUp(View):
    def get(self, request):
        user = UserForm()
        return render(request, 'page-register.html', {'user_form': user})

    def post(self, request):
        form = UserForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            username= form.cleaned_data['username']
            password = form.cleaned_data['password']
            group = form.cleaned_data['group_name']
            user.set_password(password)
            user.customer = False
            user.save()
            g = UserGroups.objects.get(name=group)
            user.groups.add(g)
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('index')
        context = {
            "user_form": form,
        }
        print('form not valid')
        return render(request, 'page-register.html', context)


class Logout(View):
    def get(self,request):
        logout(request)
        return redirect('index')


class ViewUsers(View):
    def get(self, request):
        return render(request, 'show_users.html', {'users': User.objects.all()})


class EditPassword(View):
    def get(self, request):
        password_form = PasswordForm()
        return render(request, 'edit_password.html', {'password_form': password_form})

    def post(self, request):
        form = PasswordForm(request.POST, instance=User.objects.get(username=request.user))
        if form.is_valid():
            user_form = form.save(commit=False)
            password = form.cleaned_data['password']
            user_form.set_password(password)
            user_form.save()
            user = authenticate(username=User.objects.get(username=request.user), password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('index')
        context = {
            "password_form": form,
        }
        return render(request, 'edit_password.html', context)


class AddUser(View):
    def get(self, request):
        user = UserForm()
        return render(request, 'add_user.html', {'user_form': user})

    def post(self, request):
        form = UserForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            password = form.cleaned_data['password']
            group = form.cleaned_data['group_name']
            user.set_password(password)
            user.customer = False
            user.save()
            g = UserGroups.objects.get(name=group)
            user.groups.add(g)
            return redirect('show_users')

        context = {
            "user_form": form,
        }
        print('form not valid')
        return render(request, 'add_user.html', context)



class DeleteUser(View):
    def get(self, request):
        username = request.GET.get('username')
        if username is not None:
            User.objects.filter(username=username).delete()
            return JsonResponse({'res': 'saved'})
        else:
            return JsonResponse({'res': 'error'})

class ViewProducts(View):
    def get(self, request):
        products = ShopifyProductModel.objects.all()
        print(len(products))
        return render(request, 'products.html', {'products': products})


class ConfigureSettings(View):
    def get(self, request):
        return render(request, 'settings.html', {'settings': ShopifySettingsModel.objects.all()})


class EditSettings(View):
    def get(self, request):
        setting = ShopifySettingsModel.objects.all()[0]
        print(setting.name)
        form = SettingsForm(instance=setting)
        return render(request, 'edit_settings.html', {'settings_form': form})

    def post(self, request):
        setting = ShopifySettingsModel.objects.all()[0]
        form = SettingsForm(request.POST, instance=setting)
        if form.is_valid():
            form.save()
            return redirect('configure_settings')


class ViewSites(View):
    def get(self, request):
        try:
            start = request.session['start_scraper']
            request.session['start_scraper'] = False
        except:
            start = False

        return render(request, 'show_sites.html', {'sites': ShopifySiteModel.objects.all(), 'start': start})


class AddSites(View):
    def get(self, request):
        return render(request, 'add_sites.html', {'add_site_form': AddSiteForm()})

    def post(self, request):
        print('Here')
        form = AddSiteForm(request.POST)

        if form.is_valid():
            form.save()
            print('saving')
            request.session['start_scraper'] = True
            return redirect('show_sites')


        return render(request, 'add_sites.html', {'add_site_form': form})


class ViewCategories(View):
    def get(self, request):
        tags_set = set()
        products = ShopifyProductModel.objects.all()
        for i in products:
            if i.tags is not None:
                tags = i.tags.split(',') if ',' in i.tags else i.tags
                for i in tags:
                    tags_set.add(i.lower().strip())

        return render(request, 'show_categories.html', {'tags_set': tags_set})


class ViewCategory(View):
    def get(self, request):
        category = request.GET['category']
        print(category)
        products_set = set()
        products = ShopifyProductModel.objects.all()
        for i in products:
            if i.tags is not None:
                tags = i.tags.split(',') if ',' in i.tags else i.tags
                for tag in tags:
                    if tag.lower().strip() == category:
                        print('here')
                        products_set.add(i)

        return render(request, 'products.html', {'products': products_set})


class ProductExtractor(View):
    def get(self, request):
        return render(request, 'product_extractor.html')

    def post(self, request):
        images = request.POST.get('download_images')
        info = request.POST.get('download_info')
        print('HI')
        print(images, info)
        try:
            url = request.POST['url'] if 'url' in request.POST else None
            download_images = True if images is not None else False
            download_info = True if info is not None else False
            product_info = product_extractor.get_product_info(url)
            if not product_info:
                return
            f = io.StringIO()
            writer = csv.writer(f)
            header = ['Title', 'Body(HTML)', 'Category', 'Tags', 'Url', 'Description', 'Price', 'Sale price',
                      'Currency', 'Option']
            i = 1
            if download_images:
                while i < len(product_info['Images']) + 1:
                    header.append('Image %s' % i)
                    i += 1
                i = 1
            writer.writerow(header)
            tags = product_info['Title'].replace(' ', ',') if product_info['Title'] else None

            if len(product_info['Options']) > 0:
                for option in product_info['Options']:
                    data = [smart_text(product_info['Title'], encoding='utf-8'),
                            smart_text(product_info['html'], encoding='utf-8'),
                            smart_text(product_info['Category'], encoding='utf-8'),
                            smart_text(tags, encoding='utf-8'),
                            smart_text(product_info['Url'], encoding='utf-8'),
                            smart_text(product_info['Description'], encoding='utf-8'),
                            smart_text(product_info['Price'], encoding='utf-8'),
                            smart_text(product_info['Sale price'], encoding='utf-8'),
                            smart_text(product_info['Currency'], encoding='utf-8'),
                            smart_text(option.replace('\n', ''), encoding='utf-8'),
                        ]
                    if download_images:
                        for image in product_info['Images']:
                            data.append(smart_text(image, encoding='utf-8'))
                    writer.writerow(data)
            else:
                data = [smart_text(product_info['Title'], encoding='utf-8'),
                    smart_text(product_info['html'], encoding='utf-8'),
                    smart_text(product_info['Category'], encoding='utf-8'),
                    smart_text(tags, encoding='utf-8'),
                    smart_text(product_info['Url'], encoding='utf-8'),
                    smart_text(product_info['Description'], encoding='utf-8'),
                    smart_text(product_info['Price'], encoding='utf-8'),
                    smart_text(product_info['Sale price'], encoding='utf-8'),
                    smart_text(product_info['Currency'], encoding='utf-8'),
                    smart_text('', encoding='utf-8'),
                ]
                if download_images:
                    for image in product_info['Images']:
                        data.append(smart_text(image, encoding='utf-8'))
                writer.writerow(data)

            f.seek(0)
            now_str = datetime.now().strftime("%Y-%m-%d-%H%M%S")
            if download_images and product_info['Images'] is not None:
                if download_info:
                    zip_stream = download_browser.download_images(product_info['Images'], f)
                else:
                    zip_stream = download_browser.download_images(product_info['Images'])
                zip_stream.seek(0)
                response = HttpResponse(zip_stream, content_type="application/x-zip-compressed")
                response_file_name = 'product' if download_info else 'images'
                response['Content-Disposition'] = 'attachment; filename=%s-%s.zip' % (response_file_name, now_str)
                return response
            response = HttpResponse(f, content_type="text/csv")
            response['Content-Disposition'] = 'attachment; filename=product-%s.csv' % now_str
            return response
        except Exception as ex:
            return render(request, 'product_extractor.html', {'error': 'Some error occured while extracting product.\n'
                                                                       'Please try again!'})


class UserProfile(View):
    def get(self, request):
        profileform = ProfileForm(instance=User.objects.get(username=request.user))
        return render(request, 'profile.html', {'profile_form': profileform})

    def post(self, request):
        form = UserForm(request.POST, request.FILES, instance=User.objects.get(username=request.user))
        if form.is_valid():
            form.save()
            return redirect('index')

        context = {
            "profile_form": form,
        }
        print('form not valid')
        return render(request, 'profile.html', context)


class ScrapingTool(View):
    def get(self, request):
        return render(request, 'scraping_tool.html',{'sites':ShopifySiteModel.objects.al})


class ViewProduct(View):
    def get(self, request):
        product_title = request.GET['product_name']
        product_url = request.GET['product_url']
        product = ShopifyProductModel.objects.filter(title=product_title, url=product_url)[0]
        product.images = product.images.split(';') if ';' in product.images else product.images
        return render(request, 'view_product.html', {'product': product})


class Search(View):
    def post(self, request):
        search_query = request.POST['search-query']
        products, sites = [], []
        if search_query and len(search_query):
            print('Hi')
            products = ShopifyProductModel.objects.filter(title__contains=search_query)
            sites = ShopifySiteModel.objects.filter(name__contains=search_query)
            print(len(products), len(sites))
        return HttpResponse(render(request, 'user_search.html', {'products': products, 'sites': sites}))


class Groups(View):
    def get(self, request):
        groups = UserGroups.objects.all()
        return render(request, 'show_groups.html', {'groups': groups})


class DeleteGroup(View):
    def get(self, request):
        try:
            group = request.GET['group']
            UserGroups.objects.filter(name=group).delete()
            return JsonResponse({'res': 'deleted'})
        except:
            return JsonResponse({'res': 'error'})

class AddGroup(View):
    def get(self, request):
        groupform = GroupForm()
        return render(request, 'add_group.html', {'group_form': groupform})

    def post(self, request):
        groupform = GroupForm(request.POST)
        if groupform.is_valid():
            groupform.save()
            return redirect('show_groups')

        return render(request, 'add_group.html', {'group_form': groupform})


class EditGroup(View):
    def get(self, request):
        group = UserGroups.objects.get(name=request.GET['group_name'])
        return render(request, 'edit_group.html', {'group': group})


class DeleteGroupUser(View):
    def get(self, request):
        username = request.GET['username']
        group_name = request.GET['group']
        try:
            group = UserGroups.objects.filter(name=group_name)[0]
            group.user_set.remove((User.objects.get(username=username)).id)
            return JsonResponse({'res': 'deleted'})
        except:
            print('Error')
            return JsonResponse({'res': 'error'})


class AddGroupUser(View):
    def get(self, request):
        try:
            error = request.session['user_error']
            request.session['user_error'] = ''
        except:
            error = ''
        return render(request, 'add_group_user.html', {'group': request.GET['group'], 'error': error})

    def post(self, request):
        username = request.POST['username']
        group_name = request.POST['group']
        print(group_name, username)
        group = UserGroups.objects.get(name=group_name)
        members = [user.username for user in group.user_set.all()]

        if username not in members:
            try:
                id = User.objects.get(username=username).id
            except:
                request.session['user_error'] = 'User not registered!!'
                return redirect('/panel/add_group_user/?group=' + group_name)

            group.user_set.add(id)
            group.save()
            return redirect('show_groups')
        else:
            request.session['user_error'] = 'User already present in the Group!'
            return redirect('/panel/add_group_user/?group=' + group_name)

class EditUser(View):
    def get(self, request):
        username = request.GET['username']
        user = User.objects.get(username=username)
        userform = EditUserForm(instance=user)
        return render(request, 'edit_user.html', {'user_form': userform, 'username': username})

    def post(self, request):
        print('HI')
        username = request.POST['username']
        form = UserForm(request.POST, request.FILES, instance=User.objects.get(username=username))
        if form.is_valid():
            form.save()
            return redirect('index')

        context = {
            "user_form": form,
        }
        print('form not valid')
        return render(request, 'edit_user.html', context)

