"""Flask application entrypoint and route definitions."""

from __future__ import annotations

import logging
import secrets
from datetime import datetime
from typing import Any, Dict

from flask import (
    Flask,
    Response,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash
from pymongo.errors import DuplicateKeyError, PyMongoError

import config
import models

logger = logging.getLogger("threadvibe.app")


def setup_logging() -> None:
    """Configure application-wide logging settings."""
    logging.basicConfig(level=config.LOG_LEVEL, format="%(levelname)s:%(name)s:%(message)s")


def ensure_csrf_token() -> str:
    """Ensure a CSRF token exists for the current session."""
    token = session.get(config.CSRF_SESSION_KEY)
    if not token:
        token = secrets.token_urlsafe(24)
        session[config.CSRF_SESSION_KEY] = token
    return token


def validate_csrf(token: str | None) -> bool:
    """Validate a submitted CSRF token against the session."""
    return bool(token) and token == session.get(config.CSRF_SESSION_KEY)


def get_cart() -> Dict[str, int]:
    """Fetch the cart from session storage."""
    return session.get(config.CART_SESSION_KEY, {})


def save_cart(cart: Dict[str, int]) -> None:
    """Persist the cart back into session storage."""
    session[config.CART_SESSION_KEY] = cart


def cart_totals(products: list[Dict[str, Any]], cart: Dict[str, int]) -> Dict[str, float]:
    """Calculate subtotal, shipping, tax, and total for cart items."""
    subtotal = 0.0
    for product in products:
        qty = cart.get(product["id"], 0)
        subtotal += product["price"] * qty
    shipping = config.SHIPPING_FLAT if subtotal > 0 else 0.0
    tax = subtotal * config.TAX_RATE
    total = subtotal + shipping + tax
    return {
        "subtotal": subtotal,
        "shipping": shipping,
        "tax": tax,
        "total": total,
    }


def build_cart_view(products: list[Dict[str, Any]], cart: Dict[str, int]) -> list[Dict[str, Any]]:
    """Attach cart quantities to product data for rendering."""
    view = []
    for product in products:
        if product["id"] in cart:
            entry = dict(product)
            entry["quantity"] = cart[product["id"]]
            view.append(entry)
    return view


def _reseed_if_needed(db: Any) -> None:
    """Drop and re-seed products if they still use old image names without extension."""
    try:
        col = db[config.PRODUCTS_COLLECTION]
        sample = col.find_one({})
        if sample and not str(sample.get("image", "")).endswith((".png", ".jpg", ".webp")):
            col.drop()
            db[config.CATEGORIES_COLLECTION].drop()
            models.seed_products(db)
            logger.info("Products re-seeded with updated image filenames.")
    except Exception as exc:
        logger.warning("Re-seed check failed: %s", exc)


def create_app(config_override: Dict[str, Any] | None = None) -> Flask:
    """Create and configure the Flask application."""
    setup_logging()
    if config_override:
        config.apply_overrides(config_override)

    app = Flask(__name__)
    app.secret_key = config.SECRET_KEY or ""

    @app.template_filter("inr")
    def inr_format(value: float) -> str:
        """Format a number in Indian currency style (e.g. 1,49,999)."""
        try:
            s = f"{int(round(value)):,}"
            # Convert standard comma grouping to Indian grouping
            parts = s.split(",")
            if len(parts) <= 2:
                return s
            # Last group stays 3 digits, rest are 2 digits
            result = parts[-1]
            if len(parts) >= 2:
                result = parts[-2] + "," + result
            for p in reversed(parts[:-2]):
                result = p + "," + result
            return result
        except (TypeError, ValueError):
            return str(value)

    db = models.get_database()
    # Re-seed if products still have old image names (no extension)
    _reseed_if_needed(db)

    @app.before_request
    def _ensure_csrf() -> None:
        """Generate a CSRF token before handling any request."""
        ensure_csrf_token()

    @app.context_processor
    def inject_globals() -> Dict[str, Any]:
        """Expose configuration values to templates."""
        cart = get_cart()
        user_email = session.get("user_email")
        return {
            "site_name": config.SITE_NAME,
            "currency": config.DEFAULT_CURRENCY,
            "csrf_token": session.get(config.CSRF_SESSION_KEY),
            "cart_count": sum(cart.values()) if cart else 0,
            "config": config,
            "logged_in": bool(user_email),
            "user_email": user_email,
        }

    @app.get("/")
    def index() -> str:
        """Render the homepage with featured products."""
        products = models.list_products(db)
        featured = [p for p in products if p.get("featured", False)]
        categories = models.list_categories(db)
        return render_template("index.html", products=featured[:4], categories=categories)

    @app.get("/products")
    def products_page() -> str:
        """Render the products listing page."""
        category = request.args.get("category")
        search = request.args.get("search")
        if search:
            products = models.search_products(db, search)
        elif category:
            products = models.get_products_by_category(db, category)
        else:
            products = models.list_products(db)
        categories = models.list_categories(db)
        return render_template("products.html", products=products, categories=categories, 
                             active_category=category, search_query=search)

    @app.get("/product/<product_id>")
    def product_detail(product_id: str) -> str:
        """Render a product detail page."""
        product = models.get_product(db, product_id)
        if not product:
            flash("Product not found.", "error")
            return redirect(url_for("products_page"))
        reviews = models.get_product_reviews(db, product_id)
        user_email = session.get("user_email")
        in_wishlist = False
        if user_email:
            wishlist = models.get_wishlist(db, user_email)
            in_wishlist = product_id in wishlist
        return render_template("product.html", product=product, reviews=reviews, in_wishlist=in_wishlist)

    @app.get("/cart")
    def cart_view() -> str:
        """Render the cart view."""
        products = models.list_products(db)
        cart = get_cart()
        totals = cart_totals(products, cart)
        items = build_cart_view(products, cart)
        return render_template("cart.html", items=items, totals=totals)

    @app.post("/cart/add")
    def cart_add() -> Response:
        """Add a product to the cart using JSON payload."""
        payload = request.get_json(silent=True) or {}
        product_id = str(payload.get("product_id", ""))
        try:
            quantity = int(payload.get("quantity", 1))
        except ValueError:
            return jsonify({"error": "Invalid quantity"}), 400
        if not validate_csrf(payload.get(config.CSRF_FIELD)):
            return jsonify({"error": "Invalid CSRF token"}), 400
        product = models.get_product(db, product_id)
        if not product:
            return jsonify({"error": "Product not found"}), 404
        cart = get_cart()
        cart[product_id] = cart.get(product_id, 0) + max(quantity, 1)
        save_cart(cart)
        return jsonify({"cart_count": sum(cart.values())})

    @app.post("/cart/update")
    def cart_update() -> Response:
        """Update cart quantities via JSON payload."""
        payload = request.get_json(silent=True) or {}
        product_id = str(payload.get("product_id", ""))
        try:
            quantity = int(payload.get("quantity", 1))
        except ValueError:
            return jsonify({"error": "Invalid quantity"}), 400
        if not validate_csrf(payload.get(config.CSRF_FIELD)):
            return jsonify({"error": "Invalid CSRF token"}), 400
        cart = get_cart()
        if quantity <= 0:
            cart.pop(product_id, None)
        else:
            cart[product_id] = quantity
        save_cart(cart)
        return jsonify({"cart_count": sum(cart.values())})

    @app.get("/checkout")
    def checkout() -> str:
        """Render the checkout form."""
        products = models.list_products(db)
        cart = get_cart()
        totals = cart_totals(products, cart)
        items = build_cart_view(products, cart)
        return render_template("checkout.html", items=items, totals=totals)

    @app.post("/checkout")
    def checkout_submit() -> str:
        """Process the checkout form and create an order."""
        form = request.form
        if not validate_csrf(form.get(config.CSRF_FIELD)):
            flash("Invalid CSRF token.", "error")
            return redirect(url_for("checkout"))
        required_fields = ["name", "email", "address", "city", "country", "zip"]
        if not all(form.get(field) for field in required_fields):
            flash("Please complete all required fields.", "error")
            return redirect(url_for("checkout"))
        cart = get_cart()
        if not cart:
            flash("Your cart is empty.", "error")
            return redirect(url_for("cart_view"))
        products = models.list_products(db)
        totals = cart_totals(products, cart)
        items = build_cart_view(products, cart)
        order = {
            "user_email": session.get("user_email", form.get("email")),
            "customer": {
                "name": form.get("name"),
                "email": form.get("email"),
                "address": form.get("address"),
                "city": form.get("city"),
                "country": form.get("country"),
                "zip": form.get("zip"),
                "notes": form.get("notes", ""),
            },
            "order_items": [
                {
                    "product_id": item["id"],
                    "name": item["name"],
                    "image": item["image"],
                    "price": item["price"],
                    "quantity": item["quantity"],
                }
                for item in items
            ],
            "totals": totals,
            "payment_method": form.get("payment_method", "card"),
            "status": "pending",
            "created_at": datetime.utcnow().isoformat(),
        }
        try:
            order_id = models.create_order(db, order)
            save_cart({})
            return redirect(url_for("payment_page", order_id=order_id))
        except PyMongoError as exc:
            logger.exception("Order creation failed: %s", exc)
            flash("We could not place your order. Please try again.", "error")
            return redirect(url_for("checkout"))

    @app.get("/payment/<order_id>")
    def payment_page(order_id: str) -> str:
        """Render demo payment page."""
        return render_template("payment.html", order_id=order_id)

    @app.post("/payment/process")
    def process_payment() -> Response:
        """Process demo payment."""
        payload = request.get_json(silent=True) or {}
        if not validate_csrf(payload.get(config.CSRF_FIELD)):
            return jsonify({"error": "Invalid CSRF token"}), 400
        # Demo payment - always succeeds
        return jsonify({"success": True, "message": "Payment processed successfully"})

    @app.get("/login")
    def login_form() -> str:
        """Render the login form."""
        return render_template("login.html")

    @app.post("/login")
    def login_submit() -> str:
        """Authenticate user credentials."""
        form = request.form
        if not validate_csrf(form.get(config.CSRF_FIELD)):
            flash("Invalid CSRF token.", "error")
            return redirect(url_for("login_form"))
        email = form.get("email", "")
        password = form.get("password", "")
        user = models.find_user_by_email(db, email)
        if not user or not check_password_hash(user.get("password_hash", ""), password):
            flash("Invalid email or password.", "error")
            return redirect(url_for("login_form"))
        session["user_email"] = email
        flash("Welcome back!", "success")
        return redirect(url_for("index"))

    @app.get("/register")
    def register_form() -> str:
        """Render the registration form."""
        return render_template("register.html")

    @app.post("/register")
    def register_submit() -> str:
        """Handle user registration submission."""
        form = request.form
        if not validate_csrf(form.get(config.CSRF_FIELD)):
            flash("Invalid CSRF token.", "error")
            return redirect(url_for("register_form"))
        if not form.get("email") or not form.get("password"):
            flash("Email and password are required.", "error")
            return redirect(url_for("register_form"))
        user = {
            "name": form.get("name", ""),
            "email": form.get("email"),
            "password_hash": generate_password_hash(form.get("password", "")),
        }
        try:
            models.create_user(db, user)
            flash("Registration successful. Please log in.", "success")
            return redirect(url_for("login_form"))
        except DuplicateKeyError:
            flash("Email already registered.", "error")
            return redirect(url_for("register_form"))
        except PyMongoError as exc:
            logger.exception("User registration failed: %s", exc)
            flash("Registration failed. Try a different email.", "error")
            return redirect(url_for("register_form"))

    @app.get("/logout")
    def logout() -> str:
        """Log the user out and clear session state."""
        session.pop("user_email", None)
        flash("Logged out successfully.", "success")
        return redirect(url_for("index"))

    @app.get("/profile")
    def profile() -> str:
        """Render user profile page."""
        user_email = session.get("user_email")
        if not user_email:
            flash("Please log in to view your profile.", "error")
            return redirect(url_for("login_form"))
        user = models.find_user_by_email(db, user_email)
        orders = models.get_user_orders(db, user_email)
        wishlist_ids = models.get_wishlist(db, user_email)
        wishlist_products = []
        for product_id in wishlist_ids:
            product = models.get_product(db, product_id)
            if product:
                wishlist_products.append(product)
        return render_template("profile.html", user=user, orders=orders, wishlist=wishlist_products)

    @app.post("/wishlist/add")
    def wishlist_add() -> Response:
        """Add a product to wishlist."""
        user_email = session.get("user_email")
        if not user_email:
            return jsonify({"error": "Please log in"}), 401
        payload = request.get_json(silent=True) or {}
        product_id = str(payload.get("product_id", ""))
        if not validate_csrf(payload.get(config.CSRF_FIELD)):
            return jsonify({"error": "Invalid CSRF token"}), 400
        models.add_to_wishlist(db, user_email, product_id)
        return jsonify({"success": True})

    @app.post("/wishlist/remove")
    def wishlist_remove() -> Response:
        """Remove a product from wishlist."""
        user_email = session.get("user_email")
        if not user_email:
            return jsonify({"error": "Please log in"}), 401
        payload = request.get_json(silent=True) or {}
        product_id = str(payload.get("product_id", ""))
        if not validate_csrf(payload.get(config.CSRF_FIELD)):
            return jsonify({"error": "Invalid CSRF token"}), 400
        models.remove_from_wishlist(db, user_email, product_id)
        return jsonify({"success": True})

    @app.post("/review/add")
    def review_add() -> str:
        """Add a product review."""
        user_email = session.get("user_email")
        if not user_email:
            flash("Please log in to leave a review.", "error")
            return redirect(url_for("login_form"))
        form = request.form
        if not validate_csrf(form.get(config.CSRF_FIELD)):
            flash("Invalid CSRF token.", "error")
            return redirect(request.referrer or url_for("index"))
        product_id = form.get("product_id")
        rating = int(form.get("rating", 5))
        comment = form.get("comment", "")
        review = {
            "product_id": product_id,
            "user_email": user_email,
            "rating": rating,
            "comment": comment,
            "created_at": datetime.utcnow().isoformat(),
        }
        models.create_review(db, review)
        flash("Review added successfully.", "success")
        return redirect(url_for("product_detail", product_id=product_id))

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
