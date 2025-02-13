# PRIDRIAN Luxe

## Overview
PRIDRIAN Luxe is a feature-rich e-commerce web application built using Django. It is designed for managing and selling luxury products, providing a seamless experience for both customers and administrators. The platform includes functionalities such as user authentication, product management, cart and wishlist handling, secure checkout, and integrated payment options.

---

## Features

### User Features
- **Registration and Login**: Secure registration and login using email as the primary identifier.
- **Profile Management**: Users can update their personal details, including full name, phone number, address, and profile picture.
- **Cart and Wishlist**:
  - Add, update, and remove items from the cart.
  - Save favorite items to a wishlist for future reference.
- **Checkout and Payments**:
  - Mobile payments integrated with M-Pesa.
  - Order history to track past purchases.
- **Address Management**:
  - Add, edit, delete, and set default shipping addresses.
- **Product Reviews**:
  - Rate and review products to help other customers.

### Admin Features
- **Admin Dashboard**:
  - Overview of total sales, orders, customers, and inventory.
  - Manage products, orders, and customers efficiently.
- **Product Management**:
  - Add, edit, and delete products with details such as price, stock, colors, and images.
- **Order Management**:
  - View, track, and update order statuses.
- **Settings Management**:
  - Configure site settings, including logos, contact details, payment methods, and shipping options.

---

## Installation

### Prerequisites
Ensure you have the following installed:
- Python 3.11+
- Django 4.2
- Virtual environment (optional but recommended)
- A database (SQLite is default; MySQL or PostgreSQL can be configured)

### Setup
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-repo/pridrian.git
   cd pridrian
   ```

2. **Create a Virtual Environment**:
   ```bash
   python -m venv myenv
   source myenv/bin/activate  # On Windows: myenv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the Database**:
   - Edit `settings.py` to configure your database credentials if not using SQLite.

5. **Run Migrations**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create a Superuser**:
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the Development Server**:
   ```bash
   python manage.py runserver
   ```
   Visit `http://127.0.0.1:8000` to access the application.

---

## Project Structure

```
PRIDRIAN/
├── myapp/
│   ├── migrations/          # Database migrations
│   ├── templates/          # HTML templates
│   ├── static/             # CSS, JS, and images
│   ├── admin.py            # Admin configurations
│   ├── models.py           # Database models
│   ├── views.py            # Application views
│   ├── forms.py            # Django forms
│   ├── urls.py             # URL routing
│   ├── signals.py          # Signal handlers
├── manage.py                 # Django's CLI utility
├── requirements.txt          # Dependencies
├── README.md                # Project documentation
```

---

## Key Modules

### Models
- **User**: Custom user model with email as the primary field.
- **Profile**: User profiles with personal and contact details.
- **Product**: Information about products, including price, stock, and images.
- **Order**: Tracks customer orders and their statuses.
- **CartItem**: Items in a user's cart.
- **Wishlist**: Products saved by the user for later purchase.
- **Review**: Customer reviews and ratings for products.
- **Settings**: Configurable settings for the site.

### Forms
- User registration, address management, product reviews, and admin settings are handled through Django forms.

### Views
- Includes views for public pages (e.g., home, shop, contact), user dashboards, admin management, and cart operations.

---

## Payment Integration

The project integrates M-Pesa for mobile money payments. Key components:
- **Authentication**: Uses `MpesaC2bCredential` and `MpesaAccessToken` classes for API authentication.
- **STK Push**: Sends payment requests directly to users' mobile devices.

---

## Contributing

We welcome contributions! Follow these steps:
1. Fork the repository.
2. Create a new branch for your feature/bugfix.
3. Commit your changes with clear messages.
4. Submit a pull request.

---

## License
This project is licensed under the MIT License. See the `LICENSE` file for more details.

---

## Contact
For inquiries or support, contact:
- Email: support@pridrianluxe.com
- Phone: +254-700-000-000
- Website: [Pridrian Luxe](http://www.pridrianluxe.com)

---

## Acknowledgements
Special thanks to the contributors and the Django community for their support and resources.


