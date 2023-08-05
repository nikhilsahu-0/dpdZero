## Overview
This guide will help you setup and use our API to manage user data, generate tokens, and perform CRUD 
 (Create, Retrieve, Update, Delete) operations on data. Our API is built using FastAPI framework for routing,
SQLAlchemy as the ORM (Object-Relational Mapping), PostgreSQL as the database, and JWT for token generation.

## Table of Contents
1. [Frameworks](#frameworks)
1. [Database Schema](#database-schema)
1. [Instructions to Run](#instructions-to-run)
1. [Setup Instructions](#setup-instructions)


## Frameworks
### Backend Framework: FastAPI (Python)
FastAPI is a modern, fast, and highly performant web framework for building APIs with Python 3.7+ based on standard Python type hints.

**Why fastAPI:** Due to its exceptional performance, developer-friendly API, and comprehensive documentation. It allows developers to
quickly build robust and scalable APIs with minimal boilerplate code, making it an excellent choice for modern web applications. 

### Other Frameworks/Libraries
- Database ORM: SQLAlchemy
- Authentication Library: JWT

Feel free to explore the [FastAPI documentation](https://fastapi.tiangolo.com/) for more details on how to leverage the features of this powerful backend framework.

## Database Schema
### PostgreSQL Database: fastapi

#### Table 1: user
This table stores information about registered users.

| Column    | Type    | Description                            |
|-----------|---------|----------------------------------------|
| user_id   | int     | Primary key                            |
| username  | varchar | User's username                        |
| email     | varchar | User's email                           |
| password  | varchar | User's password                        |
| full_name | varchar | User's full name                       |
| age       | int     | User's age                             |
| gender    | varchar | User's gender                          |

#### Table 2: data
This table stores key-value pairs of data.

| Column   | Type    | Description                            |
|----------|---------|----------------------------------------|
| data_id  | int     | Primary key                            |
| key      | varchar | Data key                               |
| value    | varchar | Data value                             |

The PostgreSQL database named `fastapi` consists of two tables: `user` and `data`. The `user` table contains user-related information, including user IDs, usernames, emails, passwords, full names, ages, and genders. The `data` table stores key-value pairs, where each entry consists of a data ID, a key, and a corresponding value.

## Instructions to Run
Clone the repository:
```
git clone https://github.com/nikhilsahu-0/nikhil_dpdZero.git
```
Navigate to the project directory:
```
cd nikhil_dpdZero
```
Before running the application, create a Docker network to facilitate communication between containers:
```
docker network create my_network
```
Once the network is created, you can use Docker Compose to set up and run the required services. The provided docker-compose.yml file will handle the deployment of your application components. Make sure you have Docker Compose installed on your system.
```
docker compose up -d
```
The -d flag runs the containers in the background.

The application should now be up and running, with the required services connected over the my_network Docker network. You can access api endpoints by visiting the appropriate URL `http://localhost:8000`

**PG-Admin :** `http://localhost:5050` **Email/Username :** *admin@email.com* **Password :** *password*

**Postgres Credentials( if required ) :** **User :** *user* **Password :** *password*

## Setup Instructions

No further setup is required as Docker handles the environment and dependencies. The provided Docker Compose configuration takes care of setting up all the necessary components.

If you encounter any issues during the setup or while running the containers, please refer to the Docker Compose documentation or the provided `docker-compose.yml` file for troubleshooting.
