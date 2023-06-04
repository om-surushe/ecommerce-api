Certainly! Here's the updated version of the README file with the deployed API link and the missing endpoints:

# Looper Backend Test

This repository contains the backend code for the Looper application. It provides API endpoints for user registration, login, managing products, coupons, and the shopping cart.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

To run this project, you need to have the following software installed on your system:

- Python (version 3.8 or above)
- pip (Python package installer)

### Installation

Follow these steps to set up the project:

1. Clone the repository to your local machine:

   ```
   git clone https://github.com/your-username/ecommerce-api.git
   ```

2. Change to the project directory:

   ```
   cd ecommerce-api
   ```

3. Install the required dependencies:

   ```
   pip install -r requirements.txt
   ```

4. Start the server:

   ```
   python main.py
   ```

   The server will run on `http://localhost:8000`.

## API Endpoints

### Register

- **Endpoint:** `/register`
- **Method:** POST
- **Description:** Register a new user.
- **Request Body:**
  ```json
  {
    "username": "username",
    "password": "password"
  }
  ```

### Login

- **Endpoint:** `/login`
- **Method:** POST
- **Description:** Authenticate a user.
- **Request Body:**
  ```json
  {
    "username": "username",
    "password": "password"
  }
  ```

### Add Product

- **Endpoint:** `/add_product`
- **Method:** POST
- **Description:** Add a new product.
- **Request Body:**
  ```json
  {
    "image": "https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=780&q=80",
    "name": "Paneer",
    "price": 250,
    "quantity": 100
  }
  ```

### List all Products

- **Endpoint:** `/get_products`
- **Method:** GET
- **Description:** Get a list of all products.

### Add Coupon

- **Endpoint:** `/add_coupon`
- **Method:** POST
- **Description:** Add a new coupon.
- **Request Body:**
  ```json
  {
    "code": "looper25",
    "discount": 25,
    "discount_type": "percentage", // or "amount"
    "description": "Get 25 off"
  }
  ```

### List all Coupons

- **Endpoint:** `/get_coupons`
- **Method:** GET
- **Description:** Get a list of all coupons.

### Add a Product to Cart

- **Endpoint:** `/add_to_cart?productId=1`
- **Method:** POST
- **Description:** Add a product to the shopping cart.

### Update Product Quantity in the Cart

- **Endpoint:** `/update_cart?productId=1&quantity=50`
- **Method:** PUT
- **Description:** Update the quantity of a product in the shopping cart.

### Delete Product from Cart

- **Endpoint:** `/delete_from_cart?productId=1`
- **Method:** DELETE
-

 **Description:** Remove a product from the shopping cart.

### Get Cart

- **Endpoint:** `/get_cart`
- **Method:** GET
- **Description:** Retrieve the shopping cart contents, including the list of products and total price. To apply a coupon code for a discount, include the `coupon` query parameter in the URL, e.g., `/get_cart?coupon=looper25`. The response will include the discounted price if a valid coupon code is provided.

## Links

- Deployed API: [E-commerce API on Replit](https://ecommerce-api.om-pravinpravin.repl.co/docs)
- Postman Documentation: [E-commerce API on Postman](https://crimson-space-855487.postman.co/workspace/New-Team-Workspace~112b8954-25d6-4db8-a946-671daa31f633/collection/17084954-4a527a09-97c4-4fd7-b8aa-be2e3d17302e?action=share&creator=17084954)
- Postman Collection: [postman.json](postman.json)

```

## Contributing

Contributions are welcome! If you find any issues or want to add new features, please submit a pull request.