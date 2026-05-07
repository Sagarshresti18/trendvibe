# ThreadVibe - Modern Clothing E-Commerce Platform

A professional clothing e-commerce website built with Flask, MongoDB, and modern web technologies.

## Features

### 🎨 Modern Design
- Clean, professional interface
- Dark/Light mode toggle
- Responsive design for all devices
- Smooth animations and transitions

### 🛍️ E-Commerce Features
- Product catalog with 10 clothing items
- Category filtering (Men's, Women's, Accessories, Footwear, Activewear)
- Product search functionality
- Shopping cart management
- Wishlist functionality
- Product reviews and ratings
- Size and color selection

### 👤 User Management
- User registration and login
- Secure password hashing
- User profile with order history
- Wishlist management
- CSRF protection

### 💳 Payment Integration
- Demo payment page
- Multiple payment methods (Card, PayPal)
- Order processing
- Order history tracking

### 🗄️ Database Structure
Separate MongoDB collections for:
- **users** - User accounts
- **products** - Product catalog
- **orders** - Order history
- **carts** - Shopping carts
- **reviews** - Product reviews
- **categories** - Product categories
- **wishlists** - User wishlists

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Edit `.env` file:
```env
MONGO_URI=mongodb://localhost:27017/
MONGO_DB_NAME=threadvibe_db
SECRET_KEY=your-secret-key
USE_MOCK_DB=false
```

**Note:** Set `USE_MOCK_DB=true` to use in-memory database for testing without MongoDB.

### 3. Add Product Images
Place your clothing images in `static/assets/` folder with names:
- `img1.jpg` - Classic Denim Jacket
- `img2.jpg` - Floral Summer Dress
- `img3.jpg` - Slim Fit Chinos
- `img4.jpg` - Leather Crossbody Bag
- `img5.jpg` - Running Sneakers
- `img6.jpg` - Yoga Leggings
- `img7.jpg` - Wool Blend Coat
- `img8.jpg` - Cotton T-Shirt Pack
- `img9.jpg` - Silk Scarf
- `img10.jpg` - Athletic Shorts

A `placeholder.jpg` will be used if images are not found.

### 4. Run the Application
```bash
python app.py
```

### 5. Access the Website
Open your browser and navigate to: **http://localhost:5000**

## Project Structure

```
threadvibe/
├── static/
│   ├── assets/          # Product images (img1.jpg - img10.jpg)
│   ├── css/
│   │   └── style.css    # Main stylesheet with dark mode
│   └── js/
│       └── main.js      # JavaScript functionality
├── templates/
│   ├── base.html        # Base template with navigation
│   ├── index.html       # Homepage
│   ├── products.html    # Products listing
│   ├── product.html     # Product detail
│   ├── cart.html        # Shopping cart
│   ├── checkout.html    # Checkout page
│   ├── payment.html     # Demo payment page
│   ├── login.html       # Login page
│   ├── register.html    # Registration page
│   └── profile.html     # User profile
├── app.py               # Main Flask application
├── models.py            # Database models
├── config.py            # Configuration
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables
└── README.md            # This file
```

## Key Features Explained

### Dark/Light Mode Toggle
- Click the sun/moon icon in the header to toggle themes
- Theme preference is saved in localStorage
- Smooth transitions between themes

### Demo Payment
- After checkout, you'll be redirected to a demo payment page
- Click "Process Payment" to simulate payment
- Order will be saved to your profile

### Wishlist
- Click the heart icon on any product to add to wishlist
- Requires login
- View wishlist in your profile

### Product Filtering
- Filter by category from homepage or products page
- Search products by name or description
- View product details with size and color options

## Technologies Used

- **Backend:** Flask 3.0.3
- **Database:** MongoDB with PyMongo
- **Authentication:** Werkzeug Security
- **Frontend:** HTML5, CSS3, JavaScript (Vanilla)
- **Fonts:** Inter, Playfair Display (Google Fonts)

## Color Scheme

### Light Mode
- Primary: #2563eb (Blue)
- Background: #ffffff (White)
- Text: #1f2937 (Dark Gray)

### Dark Mode
- Primary: #3b82f6 (Light Blue)
- Background: #111827 (Dark)
- Text: #f9fafb (Light Gray)

## Security Features

- CSRF protection on all forms
- Password hashing with Werkzeug
- Secure session management
- Input validation
- XSS prevention

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Development

### Running in Development Mode
```bash
python app.py
```
flask --app app run  

### Using Mock Database
Set `USE_MOCK_DB=true` in `.env` to use in-memory database for testing.

## Production Deployment

1. Set strong `SECRET_KEY` in `.env`
2. Use production MongoDB instance
3. Set `USE_MOCK_DB=false`
4. Configure proper HTTPS
5. Set up proper error logging

## License

This project is created for educational purposes.

## Support

For issues or questions, please open an issue in the repo.
---

**ThreadVibe - Where Style Meets Comfort** 🛍️
