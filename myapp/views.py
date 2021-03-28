from django.shortcuts import render
from bson.json_util import dumps, loads
from django.shortcuts import redirect

import requests
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.decorators import login_required

# Create your views here.
from django.http import HttpResponse
from django.template import Context, loader
from .models import Product
from .models import User

from selenium import webdriver
from time import sleep

import pymongo

client = pymongo.MongoClient(
    "mongodb+srv://omani-user:*****@cluster0.beihp.mongodb.net/test?authSource=admin&replicaSet=atlas-10j1kw-shard-0&readPreference=primary&appname=MongoDB%20Compass&ssl=true")

# Database Name
db = client["product_database"]

# Collection Name
col = db["myapp_product"]

################################################ Database section  ##################################################
# save data to the MongoDB


def save_data(region, state, village, zone, price, area, contract, type, source, year):
    product = Product(
        region=region,
        state=state,
        village=village,
        zone=zone,
        price=price,
        area=area,
        contract=contract,
        type=type,
        source=source,
        year=year
    )
    product.save()


def save_user(user_id, user_name, user_user_name, user_email, user_phone, user_pass):
    user = User(
        user_id=user_id,
        user_name=user_name,
        user_user_name=user_user_name,
        user_email=user_email,
        user_phone=user_phone,
        user_pass=user_pass
    )
    user.save()


def read_user():
    datas = User.objects.all()
    return datas


def delete_user(id):
    User.objects.filter(user_id=id).delete()


def update_user(id, name, user_name, email, phone, password):
    User.objects.filter(user_id=id).update(user_name=name, user_user_name=name,
                                           user_email=email, user_phone=phone, user_pass=password)
################################################ End database section  ##################################################

################################################ Login section  ##################################################
# page view


def index(request):
    login_status = ''
    request.session['login_status'] = 'false'
    if(request.POST):
        if request.POST.get('logined_username'):
            name = request.POST.get('logined_username')
            password = request.POST.get('logined_password')
            # password = make_password(password)
            print(password)
            pass_db = ''
            try:
                pass_db = User.objects.get(user_user_name=name).user_pass
                if(check_password(password, pass_db)):
                    login_status = 'Successful!'
                    request.session['login_status'] = 'true'
                    print(request.session['login_status'])
                    return redirect('/dashboard')
                else:
                    login_status = 'Wrong password! Please try again'
            except:
                login_status = 'This user name does not exist!'
            # if pass_db == password:
            #     print('Login successful')
            #     return redirect('/dashboard')
            # else:
            #     login_status = 'Wrong password! Please retry it.'
    else:
        print('Wrong password')
    return render(request, 'login.html', {'login_status': login_status})
################################################ End section  ##################################################

################################################ Dashboard section  ##################################################
# dashboard view


def dashboard(request):
    print(request.session['login_status'])
    if request.session['login_status'] == 'false':
        return redirect('/')
    # Get all number of items by the contract
    else:
        swap_num = seperate_data_by_contract('SWAP')
        sale_num = seperate_data_by_contract('SALE')
        mortgage_num = seperate_data_by_contract('MORTGAGE')

        # get the total number of items
        product_number = col.find().count()

        region_data = request.GET.get('region', '')
        # get total area by the region filtering
        total_area_on_region = get_all_area_in_region(region_data)
        # get contract number by the region filtering
        total_contact_on_region = get_contract_data_on_region(region_data)
        # get the number per contract filter for the pie chart
        sale_in_region = get_contract_number_in_region(region_data, 'SALE')
        mortgage_in_region = get_contract_number_in_region(
            region_data, 'MORTGAGE')
        swap_in_region = get_contract_number_in_region(region_data, 'SWAP')

        state = request.GET.get('state', '')
        data_in_year_num = []
        for year in range(2015, 2022):
            all_price = 0
            price_per_year = Product.objects.filter(year=year)
            if(state != ''):
                price_per_year &= Product.objects.filter(state=state)
            data_tranded_value = price_per_year.values_list('price', flat=True)
            for item in data_tranded_value:
                all_price += item
            print(all_price)
            if(len(price_per_year) != 0):
                tranded_value = all_price/len(price_per_year)
            else:
                tranded_value = 0
            data_in_year_num.append(tranded_value)

        return render(request, 'dashboard.html', {
            'total': product_number,
            'sale': sale_num,
            'swap': swap_num,
            'mortgage': mortgage_num,
            'size_per_year': data_in_year_num,
            'total_area': total_area_on_region,
            'total_contract_number': total_contact_on_region,
            'selected_region': region_data,
            'sale_in_region': sale_in_region,
            'mortgage_in_region': mortgage_in_region,
            'swap_in_region': swap_in_region,
            'selected_state': state
        })
# functions for the dashboard


def seperate_data_by_contract(property):
    datas = Product.objects.filter(contract=property)
    return datas.count()


def get_all_area_in_region(region):
    datas = []
    if region == '':
        datas = Product.objects.all().values_list('area', flat=True)
    else:
        datas = Product.objects.filter(region=region).values_list(
            'area', flat=True) | Product.objects.filter(region=(region+' ')).values_list('area', flat=True)
    area_sum = 0
    for item in datas:
        area_sum += item
    return area_sum


def get_data_by_year(year):
    datas = Product.objects.all().filter(year=year)
    return datas


def get_contract_data_on_region(region):
    datas = []
    if region == '':
        datas = Product.objects.all()
    else:
        datas = Product.objects.filter(
            region=region) | Product.objects.filter(region=(region + ' '))
    contract_num = len(datas)
    return contract_num


def get_contract_number_in_region(region, contract_type):
    datas = []
    if region == '':
        datas = Product.objects.all().filter(contract=contract_type)
    else:
        datas = Product.objects.filter(region=region).filter(
            contract=contract_type) | Product.objects.filter(region=(region+' ')).filter(contract=contract_type)
    number_by_contract = len(datas)
    return number_by_contract


def get_tranded_value():
    print('')
################################################  End Dashboard section  ##################################################

################################################  Data view section  ##################################################
# data page view


def data(request):
    if request.session['login_status'] == 'false':
        return redirect('/')
    else:
        page_index = request.GET.get('index', '')
        if(page_index == ''):
            page_index = 1

        filter_from = ''
        filter_to = ''
        filter_region = ''
        filter_state = ''
        filter_village = ''
        filter_zone = ''
        filter_min = ''
        filter_max = ''
        filter_housing = 'on'
        filter_external = 'on'
        filter_sale = 'on'
        filter_mortgage = 'on'
        filter_swap = 'on'
        filter_type = ''

        if(request.GET):
            # get filter form data
            filter_from = request.GET.get('from', '')
            filter_to = request.GET.get('to', '')
            filter_region = request.GET.get('region', '')
            filter_state = request.GET.get('state', '')
            filter_village = request.GET.get('village', '')
            filter_zone = request.GET.get('zone', '')
            filter_min = request.GET.get('min', '')
            filter_max = request.GET.get('max', '')
            filter_housing = request.GET.get('housing', '')
            filter_external = request.GET.get('external', '')
            filter_sale = request.GET.get('sale', '')
            filter_mortgage = request.GET.get('mortgage', '')
            filter_swap = request.GET.get('swap', '')
            filter_type = request.GET.get('type', '')

        [data, num] = data_filtering(filter_from, filter_to, filter_region, filter_state, filter_village, filter_zone,
                                     filter_min, filter_max, filter_housing, filter_external, filter_sale, filter_mortgage, filter_swap, filter_type)
        temp = pagenation(int(page_index), data)
        num_per_page = len(temp)

        return render(request, 'data.html', {
            'page_index': page_index,
            'data': temp,
            'num': num,
            'num_per_page': num_per_page,
            'filter_from': filter_from,
            'filter_to': filter_to,
            'filter_region': filter_region,
            'filter_state': filter_state,
            'filter_village': filter_village,
            'filter_zone': filter_zone,
            'filter_min': filter_min,
            'filter_max': filter_max,
            'filter_housing': filter_housing,
            'filter_external': filter_external,
            'filter_sale': filter_sale,
            'filter_mortgage': filter_mortgage,
            'filter_swap': filter_swap,
            'filter_type': filter_type
        })


def data_filtering(fr, to, region, state, village, zone, min, max, housing, external, sale, mortgage, swap, type):
    if(region != ''):
        datas = Product.objects.filter(
            region=region) | Product.objects.filter(region=region+' ')
    else:
        datas = Product.objects.all()
    if(state != ''):
        datas &= Product.objects.filter(state=' '+state+' ')
    if(village != ''):
        datas &= Product.objects.filter(village=village)
    if(zone != ''):
        datas &= Product.objects.filter(zone=zone)
    print(housing)
    if(housing != 'on'):
        datas &= Product.objects.exclude(source='MINISTRY_OF_HOUSING')
    if(external != 'on'):
        datas &= Product.objects.exclude(source='EXTERNAL_WEBSITES')
    if(sale != 'on'):
        datas &= Product.objects.exclude(contract='SALE')
    if(mortgage != 'on'):
        datas &= Product.objects.exclude(contract='MORTGAGE')
    if(swap != 'on'):
        datas &= Product.objects.exclude(contract='SWAP')

    if(type != ''):
        print(type)
        if(type == 'Agricultural'):
            datas &= Product.objects.filter(type=" Farm ")
        if(type == 'Commercial'):
            datas &= (Product.objects.filter(type=" Office ") | Product.objects.filter(type=" Hotel ") | Product.objects.filter(type=" Shop ") | Product.objects.filter(
                type=" Restaurant ") | Product.objects.filter(type=" Coffee Shop  ") | Product.objects.filter(type=" Super Market  ") | Product.objects.filter(type=" Commercial  "))
        if(type == 'Residential'):
            datas &= (Product.objects.filter(type=" Residential "))
        if(type == 'Residential/Commercial'):
            datas &= (Product.objects.filter(type=" Mixed Use "))
        if(type == 'Others'):
            datas &= (Product.objects.filter(type=" Others ")
                      | Product.objects.filter(type=" Other "))
        if(type == 'Industrial'):
            datas &= (Product.objects.filter(type=" Industrial "))
        if(type == 'Governmental'):
            datas &= (Product.objects.filter(type=" Governmental "))
        if(type == 'Tourist'):
            datas &= (Product.objects.filter(type=" Tourist "))
    if(min != ''):
        if(max != ''):
            datas &= Product.objects.filter(price__range=(int(min), int(max)))
    if(fr != ''):
        if(to != ''):
            datas &= Product.objects.filter(year__range=(int(fr), int(to)))
    num = len(datas)
    return datas, num


def pagenation(index, data):
    temp = []
    num = len(data)
    fr = (index-1)*30
    to = index*30
    if(num < to):
        to = num
    for i in range(fr, to):
        temp.append(data[i])
    return temp
################################################  End Data view section  ##################################################


################################################  User section  ##################################################
# user page view
def user(request):
    if request.session['login_status'] == 'false':
        return redirect('/')
    else:
        datas = read_user()
        if(request.GET):
            user_name = request.GET.get('name', '')
            user_email = request.GET.get('email', '')
            user_user_name = request.GET.get('username', '')
            user_phone = request.GET.get('phone', '')
            user_password = request.GET.get('password', '')
            user_password = make_password(user_password)
            #user_id, user_name, user_user_name, user_email, user_phone, user_pass
            if(user_name != ''):
                save_user('', user_name, user_user_name,
                          user_email, user_phone, user_password)
        return render(request, 'users.html', {'data': datas})

################################################  End User section  ##################################################


################################################  User Edit section  ##################################################
# edit user page view
def edituser(request):
    if request.session['login_status'] == 'false':
        return redirect('/')
    else:
        return render(request, 'user-edit.html')

################################################  End User Edit section  ##################################################

################################################  Scraping view section  ##################################################
# the function for scraping


def scraping(request):
    if request.session['login_status'] == 'false':
        return redirect('/')
    else:
        start_scrapy = "false"
        start_scrapy = request.GET['start']
        if(start_scrapy == "true"):
            scraper()
            get_data_from_api(request)
        return render(request, 'scrapy.html')
################################################  End Scraping view section  ##################################################


################################################  Scraping  section  ##################################################
# -- open browser
options = webdriver.ChromeOptions()
options.add_argument("headless")  # headless  --start-maximized
driver = webdriver.Chrome(options=options)

# data scraper


def scraper():
    item = []
    driver.get("https://om.opensooq.com/en/real-estate-for-sale/all")
    print('Scraper is runing now....')
    sleep(5)

    # Get the item number
    array_string_item = driver.find_element_by_xpath(
        '//*[@id="title_wrap"]/span').get_attribute('textContent').strip().split(' ')
    item_number = array_string_item[6]
    print(item_number)

    # Get item property
    for pages in range(1, int(int(item_number)/30)):  # int(int(item_number)/30)
        try:
            driver.get(
                "https://om.opensooq.com/en/real-estate-for-sale/all?page=" + str(pages) + "&per-page=30")
            sleep(3)
            arr_all_list = driver.find_elements_by_xpath(
                '//*[@id="gridPostListing"]/li')
            print(len(arr_all_list))
            for temp_list in arr_all_list:
                try:
                    string_data_line_array = temp_list.find_element_by_class_name(
                        'rectLiDetails') .text.strip().splitlines()
                    if(find_price_property(string_data_line_array)):
                        property_price = int(
                            find_price_property(string_data_line_array))
                    else:
                        property_price = 0
                    # print(property_price)
                    string_first_line = ''
                    string_second_line = ''
                    if property_price == 0:
                        string_first_line = string_data_line_array[1]
                        string_second_line = string_data_line_array[2]
                    else:
                        string_first_line = string_data_line_array[2]
                        string_second_line = string_data_line_array[3]
                    string_first_line_to_array = string_first_line.split(' | ')
                    string_second_line_to_array = string_second_line.split(
                        ' | ')
                    # print(string_first_line_to_array, string_second_line_to_array)

                    if(string_first_line_to_array[0] != ''):
                        property_region = string_first_line_to_array[0]
                    else:
                        property_region = ''
                    if(string_first_line_to_array[1] != ''):
                        property_state = string_first_line_to_array[1]
                    else:
                        property_state = ''

                    property_area = 0
                    flag = -1
                    if find_area_property(string_second_line_to_array):
                        property_area = find_area_property(
                            string_second_line_to_array)
                    else:
                        property_area = 0

                    property_type = ''

                    if len(string_second_line_to_array) < 1:
                        property_type = ''
                    else:
                        if string_second_line_to_array[1].find('m2') == -1:
                            property_type = string_second_line_to_array[1]
                        else:
                            property_type = string_second_line_to_array[2]

                    #region, state, village, zone, price, area, contract, type, source, year
                    save_data(property_region, property_state, '', '', property_price,
                              property_area, 'SALE', property_type, 'EXTERNAL_WEBSITES', 2021)
                except Exception as e:
                    print('Error ocurred! ')
            else:
                print('One page ended!')

        except:
            print('Error orrcur in loading pages!')

    else:
        print('Can not load this page data!')

# Search the area property in string array


def find_area_property(string_array):
    for cell in string_array:
        flag = cell.find('m2')
        if(flag != -1):
            cell = cell.strip().replace('m2', '')
            return cell
            break
    return ''

# Search the price value in string array


def find_price_property(string_array):
    for cell in string_array:
        flag = cell.find('RO')
        if(flag != -1):
            cell = cell.strip().replace('RO', '')
            cell = cell.replace(',', '')
            return cell
            break
    return ''
################################################  End Scraping  section  ##################################################


################################################  API  section  ##################################################
def get_data_from_api(request):
    response = requests.get('https://real-estate-oman-test.herokuapp.com/data')
    geodata = response.json()
    for item in geodata['data']:
        #item['type'], item['region'], 0, item['state'], item['contract'], item['area'], item['year'], item['zone']
        #region, state, village, zone, price, area, contract, type, source, year
        save_data(item['region'], item['state'], item['village'], item['zone'], item['price'],
                  item['area'], item['contract'], item['type'], 'MINISTRY_OF_HOUSING', item['year'])

################################################  End API  section  ##################################################
