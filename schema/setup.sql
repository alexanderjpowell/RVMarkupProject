-- Create HtmlScores table in RedVentures database
-- command: mysql -uroot -ppassword < setup.sql

USE RedVentures;

CREATE TABLE IF NOT EXISTS HtmlScores 
(
	ID INT NOT NULL PRIMARY KEY AUTO_INCREMENT, 
	Score INT(10),
	Keyname CHAR(50),
	Filename CHAR(50),
	Last_modified DATE
);