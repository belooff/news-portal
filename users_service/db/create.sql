CREATE DATABASE users_prod;
CREATE DATABASE users_dev;
CREATE DATABASE users_test;

CREATE TABLE users (
	id			serial PRIMARY KEY,
	name		text NOT NULL,
	email		text NOT NULL,
	password	text NOT NULL
);