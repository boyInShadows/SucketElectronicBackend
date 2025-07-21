# Sucket Electronic - Backend API

A Django REST API backend for the Sucket Electronic e-commerce platform. This backend provides a comprehensive API for managing products, users, orders, and content management.

## 🚀 Features

- **User Management**: Custom user model with authentication and authorization
- **Product Management**: Categories, products with Persian slug support
- **Shopping Cart**: Full cart functionality with items management
- **Order Management**: Complete order processing with status tracking
- **Content Management**: Articles and contact messages
- **RESTful API**: Comprehensive API endpoints using Django REST Framework
- **CORS Support**: Cross-origin resource sharing enabled
- **Media Management**: File uploads for products and articles

## 🛠️ Tech Stack

- **Django 5.2**: Web framework
- **Django REST Framework**: API development
- **SQLite**: Database (development)
- **CORS Headers**: Cross-origin support
- **Pillow**: Image processing

## 📋 Prerequisites

- Python 3.8+
- pip (Python package installer)
- Virtual environment (recommended)

## 🔧 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd SucketElectronic/backend
   ```

2. **Create and activate virtual environment**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install django
   pip install djangorestframework
   pip install django-cors-headers
   pip install Pillow
   ```

4. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```

The API will be available at `http://localhost:8000/`

## 📚 API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout

### Users
- `GET /api/users/` - List users (admin only)
- `GET /api/users/{id}/` - Get user details
- `PUT /api/users/{id}/` - Update user
- `DELETE /api/users/{id}/` - Delete user

### Categories
- `GET /api/categories/` - List categories
- `POST /api/categories/` - Create category (admin only)
- `GET /api/categories/{id}/` - Get category details
- `PUT /api/categories/{id}/` - Update category
- `DELETE /api/categories/{id}/` - Delete category

### Products
- `GET /api/products/` - List products
- `POST /api/products/` - Create product (admin only)
- `GET /api/products/{id}/` - Get product details
- `PUT /api/products/{id}/` - Update product
- `DELETE /api/products/{id}/` - Delete product

### Cart
- `GET /api/cart/` - Get user's cart
- `POST /api/cart/` - Create cart
- `GET /api/cart/items/` - List cart items
- `POST /api/cart/items/` - Add item to cart
- `PUT /api/cart/items/{id}/` - Update cart item
- `DELETE /api/cart/items/{id}/` - Remove item from cart

### Orders
- `GET /api/orders/` - List user's orders
- `POST /api/orders/` - Create order
- `GET /api/orders/{id}/` - Get order details
- `PUT /api/orders/{id}/` - Update order status

### Articles
- `GET /api/articles/` - List articles
- `POST /api/articles/` - Create article (admin only)
- `GET /api/articles/{id}/` - Get article details
- `PUT /api/articles/{id}/` - Update article
- `DELETE /api/articles/{id}/` - Delete article

### Messages
- `GET /api/messages/` - List contact messages (admin only)
- `POST /api/messages/` - Send contact message
- `GET /api/messages/{id}/` - Get message details

## 🗄️ Database Models

### User
- Custom user model extending AbstractUser
- Phone number field
- Admin role management

### Category
- Name, description, and slug
- Persian slug support for SEO

### Product
- Name, description, price, category
- Image URL support
- Timestamps

### Cart & CartItem
- User-specific shopping cart
- Product quantity management

### Order & OrderItem
- Order status tracking
- Total price calculation
- Shipping address

### Article
- Content management for blog/articles
- Image upload support

### Message
- Contact form submissions
- Email and message content

## 🔐 Authentication

The API uses Django's built-in authentication system with custom user model. JWT tokens or session-based authentication can be implemented as needed.

## 🌐 CORS Configuration

CORS is configured to allow cross-origin requests from the frontend application. Update `ALLOWED_HOSTS` and `CORS_ALLOWED_ORIGINS` in settings.py for production.

## 📁 Project Structure

```
backend/
├── config/                 # Django settings and configuration
│   ├── settings.py        # Main settings file
│   ├── urls.py           # Root URL configuration
│   └── wsgi.py           # WSGI configuration
├── ecommerce/            # Main app
│   ├── models.py         # Database models
│   ├── views.py          # API views
│   ├── serializers.py    # DRF serializers
│   └── urls.py           # App URL patterns
├── products/             # Products app
├── media/               # Uploaded files
├── manage.py            # Django management script
└── db.sqlite3           # SQLite database
```

## 🚀 Deployment

For production deployment:

1. Set `DEBUG = False` in settings.py
2. Configure a production database (PostgreSQL recommended)
3. Set up static file serving
4. Configure environment variables for sensitive data
5. Set up proper CORS origins
6. Use a production WSGI server (Gunicorn)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is part of the Sucket Electronic e-commerce platform.

## 🔗 Frontend Integration

This backend is designed to work with the Next.js frontend application. The frontend repository contains the complete user interface and connects to these API endpoints. 