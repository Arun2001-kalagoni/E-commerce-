import datetime
import os
import re

from flask import Flask, render_template, request, session, redirect

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
APP_ROOT = APP_ROOT + "/static"

import pymongo

from bson import ObjectId

myClient = pymongo.MongoClient('mongodb://localhost:27017/')
# mydb = myClient["OnlineShopping"]
mydb = myClient["ElectronicEcommerce"]
category_col = mydb["Category"]
brand_col = mydb["Brand"]
product_col = mydb["Products"]
deliver_boy_col = mydb["DeliverBoy"]
customer_order_col = mydb["CustomerOrder"]
customer_order_list_col = mydb["CustomerOrderList"]
customer_col = mydb["Customer"]

app = Flask(__name__)
app.secret_key = "onlineshopping"


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/adminLogin")
def adminLogin():
    return render_template("adminLogin.html")


@app.route("/customerLogin")
def customerLogin():
    return render_template("customerLogin.html")


@app.route("/deliver_boy_login")
def deliver_boy_login():
    return render_template("deliver_boy_login.html")


@app.route("/aLogin1", methods=['post'])
def aLogin1():
    user_name = request.form.get("user_name")
    password = request.form.get("password")

    if user_name == 'admin' and password == 'admin':
        session['role'] = 'admin'
        return render_template("ahome.html")
    else:
        return render_template("message.html", msg='Invalid Login Details', color='bg-danger')


@app.route("/logout")
def logout():
    session.clear()
    return render_template("home.html")


@app.route("/ahome")
def ahome():
    return render_template("ahome.html")


@app.route("/addCategory")
def addCategory():
    category_name = request.args.get('category_name')
    if category_name != None:
        category_name = category_name.lower()
        query = {"category_name": category_name}
        count = category_col.count_documents(query)
        if count == 0:
            category_col.insert_one(query)
        else:
            return render_template("message.html", msg="This Category Exist", color="text-danger")
    categories = category_col.find()
    return render_template("addCategory.html", categories=categories)


@app.route("/addBrand")
def addBrand():
    brand_name = request.args.get('brand_name')
    if brand_name != None:
        brand_name = brand_name.lower()
        query = {"brand_name": brand_name}
        count = brand_col.count_documents(query)
        if count == 0:
            brand_col.insert_one(query)
        else:
            return render_template("message.html", msg="This Brand Exist", color="text-danger")
    brands = brand_col.find()
    return render_template("addBrand.html", brands=brands)


@app.route("/addProduct")
def addProduct():
    categories = category_col.find()
    brands = brand_col.find()
    return render_template("addProduct.html", categories=categories, brands=brands)


@app.route("/addProduct1", methods=['post'])
def addProduct1():
    product_name = request.form.get("product_name")
    price = request.form.get("price")
    available_quantity = request.form.get("available_quantity")
    warranty = request.form.get("warranty")
    serial_number = request.form.get("serial_number")
    category_id = request.form.get("category_id")
    brand_id = request.form.get("brand_id")
    picture = request.files.get("picture")
    path = APP_ROOT + "/Product/" + picture.filename
    picture.save(path)
    about_item = request.form.get("about_item")
    query = {"$or": [{"serial_number": serial_number}]}
    count = product_col.count_documents(query)
    if count > 0:
        return render_template("message.html", msg="Serial Number " + serial_number + " Exists", color='text-danger')
    else:
        product_col.insert_one({"product_name": product_name, "price": price, "available_quantity": available_quantity,
                                "warranty": warranty, "serial_number": serial_number, "about_item": about_item,
                                "picture": picture.filename, "category_id": ObjectId(category_id),
                                "brand_id": ObjectId(brand_id)})
        return render_template("message.html", msg="Product Added Successfully", color='text-primary')


@app.route("/viewProducts")
def viewProducts():
    category_id = request.args.get("category_id")
    product_name = request.args.get("product_name")
    query = {}
    if session['role'] == 'admin':
        if category_id is None:
            category_id == 'all'
        if product_name is None:
            product_name = ''
        elif category_id == 'all' and product_name != 'all':
            rgx = re.compile(".*" + product_name + ".*", re.IGNORECASE)
            query = {"product_name": rgx}
        elif category_id != 'all' and product_name == 'all':
            query = {"category_id": ObjectId(category_id)}
        elif category_id != 'all' and product_name != 'all':
            rgx = re.compile(".*" + product_name + ".*", re.IGNORECASE)
            query = {"product_name": rgx, "category_id": ObjectId(category_id)}
    elif session['role'] == 'customer':
        if category_id is None:
            category_id == 'all'
        if product_name is None:
            product_name = ''
        elif category_id == 'all' and product_name != 'all':
            rgx = re.compile(".*" + product_name + ".*", re.IGNORECASE)
            query = {"product_name": rgx}
        elif category_id != 'all' and product_name == 'all':
            query = {"category_id": ObjectId(category_id)}
        elif category_id != 'all' and product_name != 'all':
            rgx = re.compile(".*" + product_name + ".*", re.IGNORECASE)
            query = {"product_name": rgx, "category_id": ObjectId(category_id)}
    products = product_col.find(query)
    categories = category_col.find()
    products = list(products)
    if len(products) == 0:
        return render_template("message.html", msg='Product Not Available')
    return render_template("viewProducts.html", get_brand_id_by_product=get_brand_id_by_product,
                           get_category_id_by_product=get_category_id_by_product, str=str, products=products,
                           categories=categories, category_id=category_id, product_name=product_name)


def get_category_id_by_product(category_id):
    category = category_col.find_one({"_id": ObjectId(category_id)})
    return category


def get_brand_id_by_product(brand_id):
    brand = brand_col.find_one({"_id": ObjectId(brand_id)})
    return brand


@app.route("/editProduct", methods=['post'])
def editProduct():
    product_id = ObjectId(request.form.get("product_id"))
    product = product_col.find_one({"_id": ObjectId(product_id)})
    return render_template("editProduct.html", product_id=product_id, product=product)


@app.route("/editProduct1", methods=['post'])
def editProduct1():
    product_id = ObjectId(request.form.get("product_id"))
    price = request.form.get("price")
    available_quantity = request.form.get("available_quantity")
    query = {"$set": {"price": price, "available_quantity": available_quantity}}
    product_col.update_one({"_id": ObjectId(product_id)}, query)
    return viewProducts()


@app.route("/customer_reg")
def customer_reg():
    return render_template("customer_reg.html")


@app.route("/customer_reg1", methods=['post'])
def customer_reg1():
    name = request.form.get("name")
    email = request.form.get("email")
    password = request.form.get("password")
    phone = request.form.get("phone")
    gender = request.form.get("gender")
    address = request.form.get("address")
    customer_wallet = request.form.get("customer_wallet")
    query = {"$or": [{"email": email}, {"phone": phone}]}
    query_count = customer_col.count_documents(query)
    if query_count == 0:
        customer_col.insert_one({"name": name, "email": email, "phone": phone, "password": password, "gender": gender,
                                 "customer_wallet": customer_wallet, "address": address})
        return render_template("message.html", msg="Registered Successfully", color='text-success')
    else:
        return render_template("message.html", msg="Duplicate Customer Details", color='text-danger')


@app.route("/addDeliverBoy")
def addDeliverBoy():
    return render_template("addDeliverBoy.html")


@app.route("/addDeliverBoy1", methods=['post'])
def addDeliverBoy1():
    name = request.form.get("name")
    email = request.form.get("email")
    password = request.form.get("password")
    phone = request.form.get("phone")
    address = request.form.get("address")
    picture = request.files.get("picture")
    path = APP_ROOT + "/DeliverBoy/" + picture.filename
    picture.save(path)
    query = {"$or": [{"email": email}, {"phone": phone}]}
    query_count = deliver_boy_col.count_documents(query)
    if query_count == 0:
        deliver_boy_col.insert_one(
            {"name": name, "email": email, "phone": phone, "password": password, "picture": picture.filename,
             "address": address})
        return render_template("message.html", msg="DeliveryBoy  Added", color='text-success')
    else:
        return render_template("message.html", msg="Duplicate DeliveryBoy Details", color='text-danger')


@app.route("/viewDeliverBoy")
def viewDeliverBoy():
    deliver_boys = deliver_boy_col.find()
    deliver_boys = list(deliver_boys)
    if len(deliver_boys) == 0:
        return render_template("message.html", msg='DeliverBoys Not Available')
    return render_template("viewDeliverBoy.html", deliver_boys=deliver_boys)


@app.route("/deliver_boy_login1", methods=['post'])
def deliver_boy_login1():
    email = request.form.get("email")
    password = request.form.get("password")
    query = {"email": email, "password": password}
    total_count = deliver_boy_col.count_documents(query)
    if total_count > 0:
        results = deliver_boy_col.find(query)
        for result in results:
            session['deliveryboy_id'] = str(result['_id'])
            session['role'] = "deliveryboy"
            return render_template("dhome.html")
    else:
        return render_template("message.html", msg="Invalid login details", color='text-danger')


@app.route("/customerLogin1", methods=['post'])
def customerLogin1():
    email = request.form.get("email")
    password = request.form.get("password")
    query = {"email": email, "password": password}
    total_count = customer_col.count_documents(query)
    if total_count > 0:
        results = customer_col.find(query)
        for result in results:
            session['customer_id'] = str(result['_id'])
            session['role'] = "customer"
            return render_template("chome.html")
    else:
        return render_template("message.html", msg="Invalid login details", color='text-danger')


@app.route("/dhome")
def dhome():
    return render_template("dhome.html")


@app.route("/chome")
def chome():
    return render_template("chome.html")


@app.route("/addCart", methods=['post'])
def addCart():
    quantity = request.form.get("quantity")
    product_id = ObjectId(request.form.get("product_id"))
    customer_id = session['customer_id']
    query = {"customer_id": ObjectId(customer_id), "order_status": 'cart'}
    a = customer_order_col.count_documents(query)
    if a == 0:
        query2 = {"customer_id": ObjectId(customer_id), "order_status": 'cart', "date": datetime.datetime.now()}
        result = customer_order_col.insert_one(query2)
        customer_order_id = result.inserted_id
    else:
        customer_order = customer_order_col.find_one({"customer_id": ObjectId(customer_id), "order_status": 'cart'})
        customer_order_id = customer_order['_id']
    query3 = {'customer_order_id': ObjectId(customer_order_id), "product_id": ObjectId(product_id),
              "product_status": 'cart'}
    count = customer_order_list_col.count_documents(query3)
    if count > 0:
        customer_order_list = customer_order_list_col.find_one(
            {'customer_order_id': ObjectId(customer_order_id), "product_id": ObjectId(product_id),
             "product_status": 'cart'})
        Quantity = int(customer_order_list['quantity']) + int(quantity)
        query4 = {'$set': {"quantity": Quantity}}
        print(query4)
        print({'customer_order_id': ObjectId(customer_order_id), "product_id": ObjectId(product_id)}, query4)
        result10 = customer_order_list_col.update_one(
            {'customer_order_id': ObjectId(customer_order_id), "product_id": ObjectId(product_id)}, query4)
        print(result10)
        item = product_col.find_one({'_id': ObjectId(product_id)})
        quantity = int(item['available_quantity']) - int(quantity)
        query7 = {"$set": {"available_quantity": quantity}}
        update2 = product_col.update_one({'_id': ObjectId(product_id)}, query7)
        return render_template("message.html", msg='Quantity Updated In Cart', color='text-info')
    else:
        query6 = {'customer_order_id': ObjectId(customer_order_id), "product_id": ObjectId(product_id),
                  "product_status": 'cart', "quantity": quantity}
        result2 = customer_order_list_col.insert_one(query6)
        item = product_col.find_one({'_id': ObjectId(product_id)})
        quantity = int(item['available_quantity']) - int(quantity)
        query8 = {"$set": {"available_quantity": quantity}}
        update3 = product_col.update_one({'_id': ObjectId(product_id)}, query8)
        return render_template("message.html", msg='Item Added To Cart', color='text-success')


@app.route("/viewOrders")
def viewOrders():
    status = request.args.get("status")
    query = {}
    if session['role'] == 'customer':
        if status == 'Cart':
            query = {"customer_id": ObjectId(session['customer_id']), "order_status": 'cart'}
        elif status == 'Ordered':
            query = {"$or": [{"order_status": 'Assigned To DeliverBoy'}, {"order_status": 'Ordered'},
                             {"order_status": 'Order Delivered'}], "customer_id": ObjectId(session['customer_id'])}
        elif status == 'History':
            query = {"customer_id": ObjectId(session['customer_id']), "order_status": 'Order Received'}
    elif session['role'] == 'admin':
        if status == 'Ordered':
            query = {"$or": [{"order_status": 'Assigned To DeliverBoy'}, {"order_status": 'Ordered'},
                             {"order_status": 'Order Delivered'}]}
        elif status == 'History':
            query = {"order_status": 'Order Received'}
    elif session['role'] == 'deliveryboy':
        if status == 'Ordered':
            query = {"$or": [{"order_status": 'Assigned To DeliverBoy'}, {"order_status": 'Order Delivered'}],
                     "deliver_boy_id": ObjectId(session['deliveryboy_id'])}
        elif status == 'History':
            query = {"deliver_boy_id": ObjectId(session['deliveryboy_id']), "order_status": 'Order Received'}
    customer_orders = customer_order_col.find(query)
    customer_orders = list(customer_orders)
    if len(customer_orders) == 0:
        return render_template("message.html", msg='No Orders')
    return render_template("viewOrders.html", get_delivery_boy_by_customer_order=get_delivery_boy_by_customer_order,
                           float=float, getCategories=getCategories,
                           getProduct_by_orders_list=getProduct_by_orders_list,
                           getOrdered_Items_list_by_customer_order_id=getOrdered_Items_list_by_customer_order_id,
                           customer_orders=customer_orders,
                           get_customer_by_customer_orders=get_customer_by_customer_orders)


def get_customer_by_customer_orders(customer_id):
    customer = customer_col.find_one({"_id": ObjectId(customer_id)})
    return customer


def getOrdered_Items_list_by_customer_order_id(customer_order_id):
    orders_lists = customer_order_list_col.find({"customer_order_id": ObjectId(customer_order_id)})
    return orders_lists


def getProduct_by_orders_list(product_id):
    products = product_col.find({"_id": ObjectId(product_id)})
    return products


def getCategories(category_id):
    categories = category_col.find({"_id": ObjectId(category_id)})
    return categories


def get_delivery_boy_by_customer_order(deliver_boy_id):
    deliver_boy = deliver_boy_col.find_one({"_id": ObjectId(deliver_boy_id)})
    return deliver_boy


@app.route("/removeCart")
def removeCart():
    customer_order_list_id = ObjectId(request.args.get("customer_order_list_id"))
    customer_order_list = customer_order_list_col.find_one({'_id': ObjectId(customer_order_list_id)})
    product_id = customer_order_list['product_id']
    customer_order_id = customer_order_list['customer_order_id']
    product = product_col.find_one({'_id': ObjectId(product_id)})
    available_quantity = int(product['available_quantity']) + int(customer_order_list['quantity'])
    query_quantity = {"$set": {"available_quantity": available_quantity}}
    result = product_col.update_one({'_id': ObjectId(product_id)}, query_quantity)
    result2 = customer_order_list_col.delete_one({"_id": ObjectId(customer_order_list_id)})
    count = customer_order_list_col.count_documents({"customer_order_id": ObjectId(customer_order_id)})
    if count == 0:
        customer_order_col.delete_one(
            {"_id": ObjectId(customer_order_id), "customer_id": ObjectId(session['customer_id'])})
    return redirect("/viewOrders?status=Cart")


@app.route("/order_now")
def order_now():
    customer_order_id = (request.args.get("customer_order_id"))
    totalPrice = request.args.get("totalPrice")
    return render_template("order_now.html", customer_order_id=customer_order_id, totalPrice=totalPrice)


@app.route("/order_now1", methods=['post'])
def order_now1():
    totalPrice = request.form.get("totalPrice")
    customer = customer_col.find_one({"_id": ObjectId(session['customer_id'])})
    customer_wallet = customer['customer_wallet']
    if int(customer_wallet) <= int(customer_wallet):
        customer_wallet = 0
    else:
        customer_wallet = float(customer_wallet) - float(totalPrice)
    query3 = {"$set": {"customer_wallet": customer_wallet}}
    customer_col.update_one({"_id": ObjectId(ObjectId(session['customer_id']))}, query3)
    customer_order_id = (request.form.get("customer_order_id"))
    customer_order_list = customer_order_list_col.find_one({'customer_order_id': ObjectId(customer_order_id)})
    print(customer_order_list)
    customer_order_list_id = customer_order_list['_id']
    query = {"$set": {"order_status": 'Ordered'}}
    query1 = {"$set": {"product_status": 'Ordered'}}
    customer_order_col.update_one({'_id': ObjectId(customer_order_id)}, query)
    customer_order_list_col.update_one({'_id': ObjectId(customer_order_list_id)}, query1)
    return redirect("/viewOrders?status=Ordered")


@app.route("/dispatch_order")
def dispatch_order():
    customer_order_id = ObjectId(request.args.get("customer_order_id"))
    delivery_boys = deliver_boy_col.find()
    return render_template("dispatch_order.html", customer_order_id=customer_order_id, delivery_boys=delivery_boys)


@app.route("/dispatch_order1", methods=['post'])
def dispatch_order1():
    customer_order_id = ObjectId(request.form.get("customer_order_id"))
    deliver_boy_id = ObjectId(request.form.get("deliver_boy_id"))
    query = {"$set": {"order_status": 'Assigned To DeliverBoy', "deliver_boy_id": ObjectId(deliver_boy_id)}}
    customer_order_col.update_one({"_id": ObjectId(customer_order_id)}, query)
    return redirect("/viewOrders?status=Ordered")


@app.route("/make_as_delivered")
def make_as_delivered():
    customer_order_id = ObjectId(request.args.get("customer_order_id"))
    deliver_date = datetime.datetime.now()
    query = {"$set": {"order_status": 'Order Delivered', "deliver_date": deliver_date}}
    customer_order_col.update_one({"_id": ObjectId(customer_order_id)}, query)
    return redirect("/viewOrders?status=Ordered")


@app.route("/make_as_received")
def make_as_received():
    customer_order_id = ObjectId(request.args.get("customer_order_id"))
    query = {"$set": {"order_status": 'Order Received'}}
    customer_order_col.update_one({"_id": ObjectId(customer_order_id)}, query)
    return redirect("/viewOrders?status=History")


app.run(debug=True)
