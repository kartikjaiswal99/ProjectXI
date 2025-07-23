# 🖤 ANOIR Backend 

**ANOIR Backend** is the server-side engine powering the e-commerce platform for **ANOIR**, a modern clothing brand. Built with Django and the Django REST Framework, it provides a comprehensive and secure API for product management, user authentication, shopping cart operations, and payment processing.

Designed with performance, security, and scalability in mind, this backend serves as the foundational backbone for ANOIR's frontend applications (web) and admin dashboards.

---

##  Features

* **Product Management**

  * CRUD operations for sellers via Django Admin
  * Support for categories, sizes, images, and filtering


* **Cart Functionality**

  * Add items to cart without login
  * Persistent cart after login
  * Quantity and variation handling (e.g., size)

* **JWT Authentication**

  * Token-based login/signup via Djoser
  * Custom user model (core.User)

* **Razorpay Payment Integration**

  * Seamless and secure payment processing
  * Order placement with real-time payment status updates

* **Order Management**

  * Store and retrieve order history

* **Optimized ORM Queries**

  * Efficient database access via Django ORM

* **Admin Dashboard**

  * Manage products, orders, customers, and payments via Django Admin
  
* **Cloudinary Storage (Production)**

  * Media (images) stored in Cloudinary

  * Static assets handled via WhiteNoise

* **Environment-Based Switching**

  * development: Uses SQLite, local media storage

  * production: Uses PostgreSQL, Cloudinary for media

---

## Tech Stack

| Component         | Technology                                        |
| ----------------- | ------------------------------------------------- |
| Backend Framework | Django, Django REST Framework                     |
| Authentication    | JWT (via Djoser + SimpleJWT)                      |
| Payment Gateway   | Razorpay API                                      |
| Database (Dev)    | SQLite (default)                                  |
| Database (Prod)	  | PostgreSQL                                        |
| Media Storage	    | Cloudinary (prod) / Local FS (dev)                |
| Static Files	    | WhiteNoise                                        |
| Admin Dashboard	  | Django Admin                                      |
| API Testing Tool  | Postman (for local development & testing)         |

---
