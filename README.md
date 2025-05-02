# Barcode Inventory Management System

A comprehensive inventory management system with barcode scanning capabilities, designed to track products across multiple warehouses.

## Overview

This system allows users to manage product inventory using barcode scanning technology (compatible with BCST-23 and other keyboard-emulating barcode scanners). It features a user-friendly menu interface that makes inventory operations intuitive and efficient.

## Features

- **Barcode Scanning Integration**
  - Scan products using standard barcode scanners
  - Interactive scanning mode for adding new products
  - Batch scanning for check-in operations

- **Complete Inventory Management**
  - Track products across multiple warehouses
  - Check in/out operations with transaction logging
  - Transfer products between warehouses
  - Set minimum stock levels for restock alerts

- **Reporting**
  - Generate inventory reports by warehouse
  - View transaction history with filtering options
  - Get low stock alerts based on minimum levels

- **User Management**
  - Role-based access control (Admin, Manager, Staff)
  - Secure authentication system

## Database Structure

- **Products**: Store information about products including barcodes
- **Categories**: Group products by category
- **Warehouses**: Define storage locations
- **Inventory**: Track product quantities in warehouses (many-to-many)
- **Transactions**: Record all inventory movements
- **Users**: Manage system access with role-based permissions
- **Suppliers**: Store supplier details
- **Product_Suppliers**: Link products to suppliers (many-to-many)

## Installation

### Prerequisites

- Python 3.7 or higher
- SQLite (built-in) or PostgreSQL (optional for larger deployments)
- Barcode scanner that functions as a keyboard input device (like BCST-23)

### Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/barcode-inventory.git
   cd barcode-inventory
   ```

2. Set up a virtual environment:
   ```
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Make the application executable:
   ```
   chmod +x inventory_app.py
   ```

5. Run the application:
   ```
   ./inventory_app.py
   ```

6. Log in with the default admin credentials:
   - Username: `admin`
   - Password: `admin`
   - **Important**: Change the default password immediately

## Usage

### Basic Navigation

The application features a menu-driven interface:

1. **Main Menu**
   - Products
   - Inventory
   - Reports
   - Scan Mode
   - User Management

2. **Barcode Scanning**
   - Select "Scan Mode" from the main menu
   - Choose "Scan and Add Products" or "Scan and Check In Products"
   - Follow the prompts to scan barcodes and enter details

3. **Inventory Management**
   - Add new products with category and supplier details
   - Check in products to specific warehouses
   - Set minimum stock levels for restock warnings
   - Transfer products between warehouses

### Sample Workflow

1. Add categories and warehouses
2. Add products with barcodes
3. Check in products to warehouses
4. Set minimum stock levels
5. Generate inventory reports
6. Check for low stock alerts

## Database Schema

The system uses a normalized relational database with:
- Primary and foreign keys for data integrity
- Indexed fields for performance optimization
- Transaction management for data consistency

## Development

### Project Structure

```
barcode-inventory/
│
├── inventory_app.py            # Main application entry point
├── generate_sample_data.py     # Script to populate test data
│
└── inventory/
    ├── models/                 # Database models (SQLAlchemy)
    ├── repositories/           # Data access layer
    ├── services/               # Business logic
    ├── cli/                    # Command handlers
    └── utils/                  # Utility functions (barcode handling)
```

### Technologies Used

- **SQLAlchemy ORM**: Object-Relational Mapping
- **SQLite/PostgreSQL**: Database storage
- **Python**: Core application logic

## Acknowledgments

- Developed as a project for CODE University's Relational Databases course