import os
from dotenv import load_dotenv

load_dotenv()


# ==========================================
# API CONFIGURATION
# ==========================================

BASE_URL = "https://dummyjson.com"

USERNAME = os.getenv("DUMMYJSON_USERNAME")
PASSWORD = os.getenv("DUMMYJSON_PASSWORD")


# ==========================================
# EXTRACTION CONFIGURATION
# ==========================================

PAGE_SIZE = 10

MAX_RETRIES = 3

REQUEST_TIMEOUT = 30


# ==========================================
# PRODUCT SCHEMA
# ==========================================

PRODUCT_SCHEMA = {
    "id": {
        "column": "product_id",
        "type": "int"
    },

    "title": {
        "column": "product_name",
        "type": "string"
    },

    "description": {
        "column": "description",
        "type": "string"
    },

    "price": {
        "column": "price",
        "type": "float"
    },

    "discountPercentage": {
        "column": "discount_percentage",
        "type": "float"
    },

    "rating": {
        "column": "rating",
        "type": "float"
    },

    "stock": {
        "column": "stock",
        "type": "int"
    },

    "brand": {
        "column": "brand",
        "type": "string"
    },

    "category": {
        "column": "category",
        "type": "string"
    },

    "sku": {
        "column": "sku",
        "type": "string"
    },

    "weight": {
        "column": "weight",
        "type": "float"
    },

    "warrantyInformation": {
        "column": "warranty_information",
        "type": "string"
    },

    "shippingInformation": {
        "column": "shipping_information",
        "type": "string"
    },

    "availabilityStatus": {
        "column": "availability_status",
        "type": "string"
    },

    "returnPolicy": {
        "column": "return_policy",
        "type": "string"
    },

    "minimumOrderQuantity": {
        "column": "minimum_order_quantity",
        "type": "int"
    }
}