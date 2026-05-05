"""MongoDB data access and domain logic."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

import mongomock
from bson import ObjectId
from bson.errors import InvalidId
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import PyMongoError

import config

logger = logging.getLogger("threadvibe.models")

_client: MongoClient | mongomock.MongoClient | None = None
_db: Database | None = None


def get_database() -> Database:
    """Create or reuse a MongoDB database connection."""
    global _client, _db
    if _db is not None:
        return _db
    try:
        if config.USE_MOCK_DB:
            _client = mongomock.MongoClient()
        else:
            _client = MongoClient(config.MONGO_URI)
            _client.admin.command("ping")
        _db = _client[config.MONGO_DB_NAME]
        init_indexes(_db)
        seed_products(_db)
        return _db
    except PyMongoError as exc:
        logger.exception("Database connection failed: %s", exc)
        raise


def get_collection(db: Database, name: str) -> Collection:
    """Return a collection reference from the database."""
    return db[name]


def init_indexes(db: Database) -> None:
    """Create indexes that enforce data constraints."""
    try:
        get_collection(db, config.USERS_COLLECTION).create_index("email", unique=True)
        get_collection(db, config.CART_COLLECTION).create_index("user_id")
        get_collection(db, config.WISHLIST_COLLECTION).create_index("user_id")
        get_collection(db, config.REVIEWS_COLLECTION).create_index("product_id")
        get_collection(db, config.CATEGORIES_COLLECTION).create_index("slug", unique=True)
    except PyMongoError as exc:
        logger.exception("Index creation failed: %s", exc)
        raise


def seed_products(db: Database) -> int:
    """Insert sample products when the catalog is empty."""
    try:
        collection = get_collection(db, config.PRODUCTS_COLLECTION)
        if collection.count_documents({}) > 0:
            return 0
        result = collection.insert_many(config.SAMPLE_PRODUCTS)
        cat_collection = get_collection(db, config.CATEGORIES_COLLECTION)
        if cat_collection.count_documents({}) == 0:
            cat_collection.insert_many(config.SAMPLE_CATEGORIES)
        return len(result.inserted_ids)
    except PyMongoError as exc:
        logger.exception("Product seeding failed: %s", exc)
        raise


def serialize_product(product: Dict[str, Any]) -> Dict[str, Any]:
    """Convert MongoDB product into JSON-safe data."""
    data = dict(product)
    data["id"] = str(data.pop("_id"))
    return data


def list_products(db: Database) -> List[Dict[str, Any]]:
    """Return all products in the catalog."""
    try:
        products = get_collection(db, config.PRODUCTS_COLLECTION).find()
        return [serialize_product(product) for product in products]
    except PyMongoError as exc:
        logger.exception("Listing products failed: %s", exc)
        raise


def get_product(db: Database, product_id: str) -> Optional[Dict[str, Any]]:
    """Fetch a single product by identifier."""
    try:
        product = get_collection(db, config.PRODUCTS_COLLECTION).find_one(
            {"_id": ObjectId(product_id)}
        )
        return serialize_product(product) if product else None
    except InvalidId:
        return None
    except PyMongoError as exc:
        logger.exception("Get product failed: %s", exc)
        raise


def list_categories(db: Database) -> List[Dict[str, Any]]:
    """Return all product categories."""
    try:
        categories = get_collection(db, config.CATEGORIES_COLLECTION).find()
        return [serialize_product(cat) for cat in categories]
    except PyMongoError as exc:
        logger.exception("Listing categories failed: %s", exc)
        raise


def get_products_by_category(db: Database, category_slug: str) -> List[Dict[str, Any]]:
    """Return products filtered by category."""
    try:
        products = get_collection(db, config.PRODUCTS_COLLECTION).find({"category": category_slug})
        return [serialize_product(product) for product in products]
    except PyMongoError as exc:
        logger.exception("Get products by category failed: %s", exc)
        raise


def search_products(db: Database, query: str) -> List[Dict[str, Any]]:
    """Search products by name or description."""
    try:
        regex = {"$regex": query, "$options": "i"}
        products = get_collection(db, config.PRODUCTS_COLLECTION).find({
            "$or": [{"name": regex}, {"description": regex}]
        })
        return [serialize_product(product) for product in products]
    except PyMongoError as exc:
        logger.exception("Search products failed: %s", exc)
        raise


def create_user(db: Database, user: Dict[str, Any]) -> str:
    """Create a new user document."""
    try:
        result = get_collection(db, config.USERS_COLLECTION).insert_one(user)
        return str(result.inserted_id)
    except PyMongoError as exc:
        logger.exception("Create user failed: %s", exc)
        raise


def find_user_by_email(db: Database, email: str) -> Optional[Dict[str, Any]]:
    """Find a user by email address."""
    try:
        return get_collection(db, config.USERS_COLLECTION).find_one({"email": email})
    except PyMongoError as exc:
        logger.exception("Find user failed: %s", exc)
        raise


def create_order(db: Database, order: Dict[str, Any]) -> str:
    """Insert a completed order into the database."""
    try:
        result = get_collection(db, config.ORDERS_COLLECTION).insert_one(order)
        return str(result.inserted_id)
    except PyMongoError as exc:
        logger.exception("Create order failed: %s", exc)
        raise


def get_user_orders(db: Database, user_email: str) -> List[Dict[str, Any]]:
    """Get all orders for a user, sorted newest first, with safe defaults."""
    try:
        col = get_collection(db, config.ORDERS_COLLECTION)
        # Match by session-linked field OR by the email typed at checkout
        raw = list(col.find(
            {"$or": [{"user_email": user_email}, {"customer.email": user_email}]}
        ))
        # Sort newest first in Python (avoids mongomock sort issues)
        raw.sort(key=lambda o: o.get("created_at", ""), reverse=True)

        orders = []
        for order in raw:
            o = serialize_product(order)
            # Ensure every field the template touches has a safe default
            o.setdefault("status", "pending")
            o.setdefault("payment_method", "card")
            o.setdefault("created_at", "")
            o.setdefault("user_email", user_email)

            # Normalize customer block
            customer = o.get("customer") or {}
            if not isinstance(customer, dict):
                customer = {}
            o["customer"] = {
                "name": customer.get("name", ""),
                "city": customer.get("city", ""),
                "country": customer.get("country", ""),
                "email": customer.get("email", user_email),
            }

            # Normalize totals block
            totals = o.get("totals") or {}
            if not isinstance(totals, dict):
                totals = {}
            o["totals"] = {
                "subtotal": float(totals.get("subtotal", 0)),
                "shipping": float(totals.get("shipping", 0)),
                "tax":      float(totals.get("tax", 0)),
                "total":    float(totals.get("total", 0)),
            }

            # Normalize each item — old orders only had product_id + quantity
            safe_items = []
            for item in (o.get("order_items") or o.get("items") or []):
                if not isinstance(item, dict):
                    continue
                safe_items.append({
                    "product_id": item.get("product_id", ""),
                    "name":       item.get("name", "Product"),
                    "image":      item.get("image", ""),
                    "price":      float(item.get("price", 0)),
                    "quantity":   int(item.get("quantity", 1)),
                })
            o["order_items"] = safe_items
            # Remove the raw "items" key so Jinja never sees the dict method collision
            o.pop("items", None)
            orders.append(o)

        return orders
    except PyMongoError as exc:
        logger.exception("Get user orders failed: %s", exc)
        raise


def add_to_wishlist(db: Database, user_id: str, product_id: str) -> bool:
    """Add a product to user's wishlist."""
    try:
        collection = get_collection(db, config.WISHLIST_COLLECTION)
        result = collection.update_one(
            {"user_id": user_id},
            {"$addToSet": {"product_ids": product_id}},
            upsert=True
        )
        return result.modified_count > 0 or result.upserted_id is not None
    except PyMongoError as exc:
        logger.exception("Add to wishlist failed: %s", exc)
        raise


def remove_from_wishlist(db: Database, user_id: str, product_id: str) -> bool:
    """Remove a product from user's wishlist."""
    try:
        collection = get_collection(db, config.WISHLIST_COLLECTION)
        result = collection.update_one(
            {"user_id": user_id},
            {"$pull": {"product_ids": product_id}}
        )
        return result.modified_count > 0
    except PyMongoError as exc:
        logger.exception("Remove from wishlist failed: %s", exc)
        raise


def get_wishlist(db: Database, user_id: str) -> List[str]:
    """Get user's wishlist product IDs."""
    try:
        collection = get_collection(db, config.WISHLIST_COLLECTION)
        wishlist = collection.find_one({"user_id": user_id})
        return wishlist.get("product_ids", []) if wishlist else []
    except PyMongoError as exc:
        logger.exception("Get wishlist failed: %s", exc)
        raise


def create_review(db: Database, review: Dict[str, Any]) -> str:
    """Create a product review."""
    try:
        result = get_collection(db, config.REVIEWS_COLLECTION).insert_one(review)
        return str(result.inserted_id)
    except PyMongoError as exc:
        logger.exception("Create review failed: %s", exc)
        raise


def get_product_reviews(db: Database, product_id: str) -> List[Dict[str, Any]]:
    """Get all reviews for a product."""
    try:
        reviews = get_collection(db, config.REVIEWS_COLLECTION).find({"product_id": product_id})
        return [serialize_product(review) for review in reviews]
    except PyMongoError as exc:
        logger.exception("Get product reviews failed: %s", exc)
        raise
