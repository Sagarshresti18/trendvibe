"""Application configuration and environment loading."""

from __future__ import annotations

import os
from typing import Any, Dict

from dotenv import load_dotenv

load_dotenv()

# Site Configuration
SITE_NAME: str = "ThreadVibe"
SITE_MARK: str = "TV"
SITE_TAGLINE: str = "Where Style Meets Comfort"
DEFAULT_CURRENCY: str = "₹"
SHIPPING_FLAT: float = 99.0
TAX_RATE: float = 0.18
PRODUCTS_PER_PAGE: int = 12

# Session Keys
CSRF_FIELD: str = "csrf_token"
CSRF_SESSION_KEY: str = "csrf_session_token"
CART_SESSION_KEY: str = "cart_items"

# MongoDB Configuration
MONGO_URI: str | None = os.getenv("MONGO_URI")
MONGO_DB_NAME: str | None = os.getenv("MONGO_DB_NAME")
SECRET_KEY: str | None = os.getenv("SECRET_KEY")
USE_MOCK_DB: bool = os.getenv("USE_MOCK_DB", "false").lower() == "true"
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

# Collection Names
USERS_COLLECTION: str = "users"
PRODUCTS_COLLECTION: str = "products"
ORDERS_COLLECTION: str = "orders"
CART_COLLECTION: str = "carts"
REVIEWS_COLLECTION: str = "reviews"
CATEGORIES_COLLECTION: str = "categories"
WISHLIST_COLLECTION: str = "wishlists"

# Sample Categories
SAMPLE_CATEGORIES: list[dict[str, Any]] = [
    {"name": "Men's Wear", "slug": "mens", "description": "Stylish clothing for men"},
    {"name": "Women's Wear", "slug": "womens", "description": "Elegant fashion for women"},
    {"name": "Accessories", "slug": "accessories", "description": "Complete your look"},
    {"name": "Footwear", "slug": "footwear", "description": "Step in style"},
    {"name": "Activewear", "slug": "activewear", "description": "Comfort meets performance"},
]

# Sample Products (10 clothing items)
SAMPLE_PRODUCTS: list[dict[str, Any]] = [
    {
        "name": "Classic Denim Jacket",
        "price": 7499.00,
        "category": "mens",
        "rating": 4.8,
        "stock": 25,
        "image": "img1.png",
        "description": "Timeless denim jacket with a modern fit. Perfect for layering.",
        "sizes": ["S", "M", "L", "XL", "XXL"],
        "colors": ["Blue", "Black"],
        "featured": True,
    },
    {
        "name": "Floral Summer Dress",
        "price": 5999.00,
        "category": "womens",
        "rating": 4.9,
        "stock": 30,
        "image": "img2.png",
        "description": "Lightweight floral dress perfect for summer days.",
        "sizes": ["XS", "S", "M", "L", "XL"],
        "colors": ["Pink", "Blue", "Yellow"],
        "featured": True,
    },
    {
        "name": "Slim Fit Chinos",
        "price": 4499.00,
        "category": "mens",
        "rating": 4.6,
        "stock": 40,
        "image": "img3.png",
        "description": "Comfortable slim fit chinos for everyday wear.",
        "sizes": ["28", "30", "32", "34", "36"],
        "colors": ["Khaki", "Navy", "Black"],
        "featured": False,
    },
    {
        "name": "Leather Crossbody Bag",
        "price": 10999.00,
        "category": "accessories",
        "rating": 4.7,
        "stock": 15,
        "image": "img4.png",
        "description": "Premium leather crossbody bag with adjustable strap.",
        "sizes": ["One Size"],
        "colors": ["Brown", "Black", "Tan"],
        "featured": True,
    },
    {
        "name": "Running Sneakers",
        "price": 8499.00,
        "category": "footwear",
        "rating": 4.8,
        "stock": 35,
        "image": "img5.png",
        "description": "Lightweight running sneakers with superior cushioning.",
        "sizes": ["7", "8", "9", "10", "11", "12"],
        "colors": ["White", "Black", "Gray"],
        "featured": True,
    },
    {
        "name": "Yoga Leggings",
        "price": 3799.00,
        "category": "activewear",
        "rating": 4.9,
        "stock": 50,
        "image": "img6.png",
        "description": "High-waisted yoga leggings with moisture-wicking fabric.",
        "sizes": ["XS", "S", "M", "L", "XL"],
        "colors": ["Black", "Navy", "Purple"],
        "featured": False,
    },
    {
        "name": "Wool Blend Coat",
        "price": 14999.00,
        "category": "womens",
        "rating": 4.7,
        "stock": 12,
        "image": "img7.png",
        "description": "Elegant wool blend coat for cold weather.",
        "sizes": ["S", "M", "L", "XL"],
        "colors": ["Camel", "Black", "Gray"],
        "featured": False,
    },
    {
        "name": "Cotton T-Shirt Pack",
        "price": 2999.00,
        "category": "mens",
        "rating": 4.5,
        "stock": 60,
        "image": "img8.png",
        "description": "Pack of 3 premium cotton t-shirts.",
        "sizes": ["S", "M", "L", "XL", "XXL"],
        "colors": ["White", "Black", "Gray"],
        "featured": False,
    },
    {
        "name": "Silk Scarf",
        "price": 3299.00,
        "category": "accessories",
        "rating": 4.6,
        "stock": 28,
        "image": "img9.png",
        "description": "Luxurious silk scarf with elegant patterns.",
        "sizes": ["One Size"],
        "colors": ["Red", "Blue", "Gold"],
        "featured": False,
    },
    {
        "name": "Athletic Shorts",
        "price": 2499.00,
        "category": "activewear",
        "rating": 4.4,
        "stock": 45,
        "image": "img10.png",
        "description": "Breathable athletic shorts for training and sports.",
        "sizes": ["S", "M", "L", "XL"],
        "colors": ["Black", "Navy", "Red"],
        "featured": False,
    },
]


def check_keys() -> bool:
    """Validate the presence of critical environment configuration."""
    return all([MONGO_URI, MONGO_DB_NAME, SECRET_KEY])


def apply_overrides(overrides: Dict[str, Any]) -> None:
    """Override configuration values at runtime for tests or tooling."""
    for key, value in overrides.items():
        if hasattr(__import__(__name__), key):
            setattr(__import__(__name__), key, value)
