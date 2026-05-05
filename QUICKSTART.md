# ThreadVibe - Quick Start Guide

## 🚀 Get Started in 3 Minutes

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Add Product Images
1. Navigate to `static/assets/` folder
2. Add 10 clothing images named: `img1.jpg`, `img2.jpg`, ... `img10.jpg`
3. Add `placeholder.jpg` for fallback
4. See `static/assets/README.txt` for image requirements

**Quick Tip:** If you don't have images yet, the site will show placeholder text. You can add images later!

### Step 3: Run the Application
```bash
python app.py
```

### Step 4: Open Your Browser
Navigate to: **http://localhost:5000**

## ✨ That's It!

The application will:
- ✅ Automatically create sample products
- ✅ Set up MongoDB collections
- ✅ Use in-memory database if MongoDB is not available
- ✅ Seed categories and products

## 🎯 Test the Features

### 1. Browse Products
- Visit homepage to see featured products
- Click "Shop" to see all products
- Use category filters on the left sidebar

### 2. Create an Account
- Click "Sign Up" in the header
- Fill in your details
- You'll be redirected to login

### 3. Add to Cart
- Click "Add to Cart" on any product
- Watch the cart count update
- Visit cart to review items

### 4. Add to Wishlist (Requires Login)
- Click the heart icon on products
- View wishlist in your profile

### 5. Checkout & Payment
- Go to cart and click "Proceed to Checkout"
- Fill in shipping details
- Click "Place Order"
- You'll be redirected to demo payment page
- Click "Process Payment" to complete

### 6. Toggle Dark Mode
- Click the sun/moon icon in the header
- Theme preference is saved automatically

## 🔧 Configuration Options

### Use In-Memory Database (No MongoDB Required)
Edit `.env`:
```env
USE_MOCK_DB=true
```

### Connect to MongoDB
Edit `.env`:
```env
MONGO_URI=mongodb://localhost:27017/
MONGO_DB_NAME=threadvibe_db
USE_MOCK_DB=false
```

### Change Secret Key
Edit `.env`:
```env
SECRET_KEY=your-new-secret-key-here
```

## 📱 Features to Explore

- ✅ **Dark/Light Mode** - Toggle in header
- ✅ **Product Search** - Search bar in products page
- ✅ **Category Filtering** - Filter by clothing type
- ✅ **Shopping Cart** - Add, update, remove items
- ✅ **Wishlist** - Save favorite products (requires login)
- ✅ **User Profile** - View orders and wishlist
- ✅ **Demo Payment** - Simulated payment process
- ✅ **Responsive Design** - Works on mobile, tablet, desktop

## 🎨 Customization

### Change Site Name
Edit `config.py`:
```python
SITE_NAME: str = "YourStoreName"
SITE_MARK: str = "YS"
SITE_TAGLINE: str = "Your tagline here"
```

### Change Colors
Edit `static/css/style.css`:
```css
:root {
--primary: #2563eb;  /* Change this */
}
```

### Add More Products
Edit `config.py` and add to `SAMPLE_PRODUCTS` list.

## 🐛 Troubleshooting

### Port Already in Use
Change port in `app.py`:
```python
app.run(debug=False, host='0.0.0.0', port=5001)
```

### MongoDB Connection Error
Set `USE_MOCK_DB=true` in `.env` to use in-memory database.

### Images Not Showing
- Check images are in `static/assets/` folder
- Check filenames match: `img1.jpg`, `img2.jpg`, etc.
- Add `placeholder.jpg` for fallback

### CSRF Token Error
- Clear browser cookies
- Restart the application

## � Next Steps

- Add your own product images
- Customize colors and branding
- Connect to real MongoDB database
- Deploy to production (see README.md)

## 💡 Pro Tips

1. **Test with Mock DB First** - Set `USE_MOCK_DB=true` to test without MongoDB
2. **Use Dark Mode** - Toggle theme to see both designs
3. **Create Test Account** - Register to test all features
4. **Check Profile** - View order history and wishlist
5. **Try Demo Payment** - Complete checkout to see payment flow

---

**Need Help?** Check README.md for detailed documentation.

**Happy Shopping! 🛍️**
