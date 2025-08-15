-- create the databases
CREATE DATABASE IF NOT EXISTS users;
USE users;


-- create the users for each database
CREATE USER 'alex'@'%' IDENTIFIED BY 'password';
GRANT CREATE, ALTER, INDEX, LOCK TABLES, REFERENCES, UPDATE, DELETE, DROP, SELECT, INSERT ON `users`.* TO 'alex'@'%';

CREATE TABLE IF NOT EXISTS Tg_users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    first_name VARCHAR(25),
    last_name VARCHAR(25),
    username VARCHAR(25),
    phone_number VARCHAR(25)
);

CREATE TABLE IF NOT EXISTS Orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL, 
    quantity INT,
    date VARCHAR(255),
    options VARCHAR(255),
    FOREIGN KEY (customer_id) REFERENCES Tg_users (id)
);
