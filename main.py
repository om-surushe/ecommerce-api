from fastapi import FastAPI, HTTPException, Depends
# import RedirectResponse from fastapi.responses
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from pydantic import BaseModel, Field
from typing import List
import json
import jwt
from datetime import datetime, timedelta
import uvicorn

description = """
An Ecommerce API powered by FastAPI, enabling user registration and login, product management, and cart functionality. Users can register, log in, add products to their cart, apply coupons for discounts, and view their cart contents.
"""


app = FastAPI(
    title="E-Commerce API",
    description=description,
    version="0.0.1",
    contact={
        "name": "Om Surushe",
        "url": "https://omsurushe.bio.link",
    },
)
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "thesecretyouwillneverguess"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

USERS_DATA_FILE = "users.json"
PRODUCTS_DATA_FILE = "products.json"
CARTS_DATA_FILE = "carts.json"
COUPONS_DATA_FILE = "coupons.json"

database_files = [USERS_DATA_FILE, PRODUCTS_DATA_FILE, CARTS_DATA_FILE, COUPONS_DATA_FILE]

# create database files if not exists
for file in database_files:
    try:
        with open(file) as f:
            pass
    except IOError:
        with open(file, "w") as f:
            json.dump({}, f)

# User model
class User(BaseModel):
    username:  str = Field(..., description="Unique username")
    password: str = Field(..., description="Password")

# Product model
class Product(BaseModel):
    productId: int = None
    image: str = Field(..., description="Image URL")
    name: str = Field(..., description="Product name")
    price: float = Field(..., description="Product price")
    quantity: int = Field(..., description="Product quantity")

# Cart model
class Cart(BaseModel):
    username: str = Field(..., description="Username")
    products: List[Product] = Field([], description="List of products in cart")
    total_price: float = Field(0, description="Total price of all products in cart")
    total_quantity: int = Field(0, description="Total quantity of all products in cart")

# Coupon model
class Coupon(BaseModel):
    code: str = Field(..., description="Coupon code")
    discount: float = Field(..., description="Discount amount")
    discount_type: str = Field(..., description="Discount type can be percentage or amount")
    description: str = Field(..., description="Coupon description")

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        return username
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_hashed_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def get_user(username: str):
    with open(USERS_DATA_FILE) as file:
        users = json.load(file)
        return users.get(username)

def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user or not verify_password(password, user.get("password")):
        return False
    return True

def create_access_token(username: str):
    expiry = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": username, "exp": expiry}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

# the default route should redirect to docs
@app.get("/")
def default():
    return RedirectResponse(url='/docs')

# register user
@app.post("/register")
def register(user: User):
    with open(USERS_DATA_FILE) as file:
        users = json.load(file)
        if user.username in users:
            raise HTTPException(status_code=400, detail="Username already exists")
        users[user.username] = {
            "username": user.username,
            "password": get_hashed_password(user.password)
        }
    with open(USERS_DATA_FILE, "w") as file:
        json.dump(users, file)
    return {"message": "User created successfully"}

# login user
@app.post("/login")
def login(user: User):
    if not authenticate_user(user.username, user.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    access_token = create_access_token(user.username)
    return {"access_token": access_token, "token_type": "bearer"}

# add product
@app.post("/add_product")
def add_product(product: Product, username: str = Depends(get_current_user)):
    with open(PRODUCTS_DATA_FILE) as file:
        products = json.load(file)
        product.productId = len(products) + 1
        products[product.productId] = product.dict()
    with open(PRODUCTS_DATA_FILE, "w") as file:
        json.dump(products, file)
    return {"message": "Product added successfully", "productId": product.productId}

# get all products
@app.get("/get_products")
def get_products(username: str = Depends(get_current_user)):
    with open(PRODUCTS_DATA_FILE) as file:
        products = json.load(file)
    return products

# add coupon
@app.post("/add_coupon")
def add_coupon(coupon: Coupon, username: str = Depends(get_current_user)):
    with open(COUPONS_DATA_FILE) as file:
        coupons = json.load(file)
        # check if coupon code already exists
        if coupon.code in coupons:
            raise HTTPException(status_code=400, detail="Coupon code already exists")
        # check the type of discount
        if coupon.discount_type in ["percentage", "amount"]:
            coupons[coupon.code] = coupon.dict()
        else:
            raise HTTPException(status_code=400, detail="Invalid discount type")
    with open(COUPONS_DATA_FILE, "w") as file:
        json.dump(coupons, file)
    return {"message": "Coupon added successfully"}

# get all coupons
@app.get("/get_coupons")
def get_coupons(username: str = Depends(get_current_user)):
    with open(COUPONS_DATA_FILE) as file:
        coupons = json.load(file)
    return coupons

# add product to cart with quantity and if quantity is not specified, it will be set to 1
@app.post("/add_to_cart")
def add_to_cart(productId: int, quantity: int = 1, username: str = Depends(get_current_user)):
    print(productId, quantity, username)
    with open(PRODUCTS_DATA_FILE) as file:
        products = json.load(file)
        product = products.get(str(productId))
        if not product:
            raise HTTPException(status_code=400, detail="Product not found")
        if product["quantity"] < quantity:
            raise HTTPException(status_code=400, detail="Product out of stock")
    with open(CARTS_DATA_FILE) as file:
        carts = json.load(file)
        cart = carts.get(username)
        newCart = False
        if not cart:
            cart = Cart(username=username)
            newCart = True
        # check if product is already in cart send already added message
        if not newCart:
            for p in cart["products"]:
                if p["productId"] == productId:
                    raise HTTPException(status_code=400, detail="Product already added to cart")
        product["quantity"] = quantity
        if not newCart:
            cart["products"].append(product)
            cart["total_price"] += product["price"] * quantity
            cart["total_quantity"] += quantity
            carts[username] = cart
        else:
            cart.products = [product]
            cart.total_price += product["price"] * quantity
            cart.total_quantity += quantity
            carts[username] = cart.dict()
    with open(CARTS_DATA_FILE, "w") as file:
        json.dump(carts, file)
    return {"message": "Product added to cart successfully",'cart':cart}

# update product quantity in cart
@app.put("/update_cart")
def update_cart(productId: int, quantity: int, username: str = Depends(get_current_user)):
    with open(PRODUCTS_DATA_FILE) as file:
        products = json.load(file)
        product = products.get(str(productId))
        if not product:
            raise HTTPException(status_code=400, detail="Product not found")
        if product["quantity"] < quantity:
            raise HTTPException(status_code=400, detail="Maximum quantity available is " + str(product["quantity"]))
    with open(CARTS_DATA_FILE) as file:
        carts = json.load(file)
        cart = carts.get(username)
        if not cart:
            raise HTTPException(status_code=400, detail="Cart not found")
        # check if product is already in cart send already added message
        for p in cart["products"]:
            if p["productId"] == productId:
                cart["total_price"] -= p["price"] * p["quantity"]
                cart["total_quantity"] -= p["quantity"]
                p["quantity"] = quantity
                cart["total_price"] += p["price"] * p["quantity"]
                cart["total_quantity"] += p["quantity"]
                carts[username] = cart
                with open(CARTS_DATA_FILE, "w") as file:
                    json.dump(carts, file)
                return {"message": "Cart updated successfully",'cart':cart}
        raise HTTPException(status_code=400, detail="Product not found in cart")

# delete product from cart
@app.delete("/delete_from_cart")
def delete_from_cart(productId: int, username: str = Depends(get_current_user)):
    with open(CARTS_DATA_FILE) as file:
        carts = json.load(file)
        cart = carts.get(username)
        if not cart:
            raise HTTPException(status_code=400, detail="Cart not found")
        # check if product is already in cart send already added message
        for p in cart["products"]:
            if p["productId"] == productId:
                cart["total_price"] -= p["price"] * p["quantity"]
                cart["total_quantity"] -= p["quantity"]
                cart["products"].remove(p)
                carts[username] = cart
                with open(CARTS_DATA_FILE, "w") as file:
                    json.dump(carts, file)
                return {"message": "Product deleted from cart successfully",'cart':cart}
        raise HTTPException(status_code=400, detail="Product not found in cart")

# get cart: returns aggregated cart information(total price, total quantity) along with the list of added product and coupon if applied
@app.get("/get_cart")
def get_cart(couponCode: str = None, username: str = Depends(get_current_user)):
    with open(CARTS_DATA_FILE) as file:
        carts = json.load(file)
        cart = carts.get(username)
        if not cart:
            raise HTTPException(status_code=400, detail="Cart not found")
        if couponCode:
            with open(COUPONS_DATA_FILE) as file:
                coupons = json.load(file)
                coupon = coupons.get(couponCode)
                if not coupon:
                    raise HTTPException(status_code=400, detail="Coupon not found")
                message = "Coupon applied successfully"
                if coupon["discount_type"] == "percentage":
                    cart["discounted_price"] = cart["total_price"] - (cart["total_price"] * coupon["discount"] / 100)
                    message += f" and {coupon['discount']}% discount applied"
                else:
                    if(cart["total_price"] < coupon["discount"]):
                        cart["discounted_price"] = 0
                        message += f" and you got the product for free"
                    else:
                        cart["discounted_price"] = cart["total_price"] - coupon["discount"]
                        message += f" and {coupon['discount']} discount applied"
                    
                cart["coupon"] = coupon
                carts[username] = cart
        else:
            message = "Checkout successful"
    with open(CARTS_DATA_FILE, "w") as file:
        json.dump(carts, file)
    # update the product quantity in products.json file
    with open(PRODUCTS_DATA_FILE) as file:
        products = json.load(file)
        for p in cart["products"]:
            products[str(p["productId"])]["quantity"] -= p["quantity"]
    return {"message": message, "cart": cart}

uvicorn.run(app, port = 8080, host = "0.0.0.0")