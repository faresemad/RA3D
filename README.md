# RA3D - Digital Services Marketplace

RA3D is a comprehensive platform for buying and selling digital services including social media services, accounts, SSH, RDP, cPanel, SMTP, webmails, and more. The platform provides a secure and efficient marketplace for both buyers and sellers of digital services.

## 🚀 Features

- **User Authentication**: Secure JWT-based authentication system
- **Multiple Service Types**:
  - Social Media Accounts
  - SSH/Shell Access
  - RDP (Remote Desktop Protocol)
  - cPanel Hosting
  - SMTP Services
  - Webmail Accounts
  - And more...
- **Order Management**: Complete order lifecycle management
- **Wallet System**: Integrated payment and wallet functionality
- **Seller Dashboard**: Tools for sellers to manage their services
- **Ticket System**: Customer support ticket management
- **Real-time Notifications**: Using Django Channels and WebSockets
- **Admin Dashboard**: Comprehensive admin controls
- **API Documentation**: Swagger/OpenAPI documentation

## 🛠️ Technology Stack

- **Backend**: Django 4+ with Django REST Framework
- **Database**: PostgreSQL
- **Caching & Message Broker**: Redis
- **Task Queue**: Celery
- **WebSockets**: Django Channels
- **Authentication**: JWT (JSON Web Tokens)
- **API Documentation**: drf-spectacular (Swagger/OpenAPI)
- **Containerization**: Docker & Docker Compose

## 📋 Prerequisites

- Docker and Docker Compose
- Python 3.11+
- PostgreSQL
- Redis

## 🔧 Installation & Setup

### Using Docker (Recommended)

1. Clone the repository:
   ```bash
   git clone https://github.com/faresemad/RA3D.git
   cd RA3D
   ```

2. Set up environment variables:
   - Copy the example env files in the `.envs` directory
   - Update with your specific configuration

3. Build and start the containers:
   ```bash
   docker-compose up --build
   ```

4. Access the application at http://localhost:8000

### Manual Setup

1. Clone the repository

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements/local.txt
   ```

4. Set up environment variables

5. Run migrations:
   ```bash
   python manage.py migrate
   ```

6. Start the development server:
   ```bash
   python manage.py runserver
   ```

## 📚 API Documentation

After starting the server, access the API documentation at:
- Swagger UI: http://localhost:8000/api/docs/
- Schema: http://localhost:8000/api/schema/

## 📦 Project Structure

- `apps/`: Django applications
  - `accounts/`: Social media accounts management
  - `cpanel/`: cPanel hosting services
  - `dashboard/`: User dashboard functionality
  - `notifications/`: Real-time notification system
  - `orders/`: Order processing and management
  - `rdp/`: Remote Desktop Protocol services
  - `sellers/`: Seller profiles and management
  - `shells/`: SSH/Shell services
  - `smtp/`: SMTP services
  - `tickets/`: Support ticket system
  - `users/`: User authentication and profiles
  - `wallet/`: Payment and wallet system
  - `webmails/`: Webmail services
- `config/`: Project configuration
- `compose/`: Docker configuration files
- `templates/`: HTML templates
- `static/`: Static files (CSS, JS, images)

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the terms of the license included in the repository.

## 📞 Contact

For questions or support, please open an issue in the GitHub repository or contact the project maintainers.
