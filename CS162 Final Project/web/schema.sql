-- CREATE DATABASE allergies_food_preferences;
USE allergies_food_preferences;

DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS diets;
DROP TABLE IF EXISTS allergies;
DROP TABLE IF EXISTS restaurants;
DROP TABLE IF EXISTS food;

-- Will be referenced as a one to one db where users are associated with one diet
CREATE TABLE IF NOT EXISTS diets (
  dietid INTEGER PRIMARY KEY AUTO_INCREMENT,
  dietname VARCHAR(20) UNIQUE NOT NULL
);

-- will be referenced as a many to many db where users can be associated with 0 to many allergies.
CREATE TABLE IF NOT EXISTS allergies (
  allergyid INTEGER PRIMARY KEY AUTO_INCREMENT,
  allergyname VARCHAR(20) UNIQUE NOT NULL
);


CREATE TABLE IF NOT EXISTS user (
  userid INTEGER PRIMARY KEY AUTO_INCREMENT,
  username VARCHAR(20) UNIQUE NOT NULL,
  field_password VARCHAR(20) UNIQUE NOT NULL -- PASSWORD is key on MySQL so name was changed
);

-- will be referanced as a many to many db where different diets can be associated with different restaurants
CREATE TABLE IF NOT EXISTS restaurants (
  restaurantid INTEGER PRIMARY KEY AUTO_INCREMENT,
  restaurantname VARCHAR(20) UNIQUE NOT NULL,
  streetnumber INTEGER,
  street VARCHAR(20),
  district VARCHAR(20),
  city VARCHAR(20),
  openhours TIME,
  closehours TIME,
  veganoptions BOOLEAN,
  vegetarianoptions BOOLEAN
)

-- will be referenced as a many to many db where different diets can be associated with different food (dishes)
CREATE TABLE IF NOT EXISTS food (
  foodid INTEGER PRIMARY KEY AUTO_INCREMENT,
  foodname VARCHAR(50),
  price INTEGER,
  calories INTEGER
)

-- relational tables
CREATE TABLE IF NOT EXISTS userdiets (
  userid INTEGER,
  dietid INTEGER,
  FOREIGN KEY (userid) REFERENCES users(userid), -- USER is keyword on MySQL
  FOREIGN KEY (dietid) REFERENCES diets(dietid),
  PRIMARY KEY (userid, dietid)
);

CREATE TABLE IF NOT EXISTS userallergies (
  userid INTEGER,
  allergyid INTEGER,
  FOREIGN KEY (userid) REFERENCES users (userid),
  FOREIGN KEY (allergyid) REFERENCES allergies(allergyid),
  PRIMARY KEY (userid, allergyid)
);
-- a restaurants can have many food and a food can be found in many restaurants
CREATE TABLE IF NOT EXISTS restaurantfood (
  restaurantid INTEGER,
  foodid INTEGER,
  FOREIGN KEY (restaurantid) REFERENCES restaurants(restaurantid),
  FOREIGN KEY (foodid) REFERENCES food(foodid),
  PRIMARY KEY (restaurantid, foodid)
)

-- many - to - many relationship between food and diet
CREATE TABLE IF NOT EXISTS dietfood (
  foodid INTEGER,
  dietid INTEGER,
  FOREIGN KEY (foodid) REFERENCES food(foodid),
  FOREIGN KEY (dietid) REFERENCES diet(dietid),
  PRIMARY KEY (foodid, dietid)
)

-- many-to-many relationship between food and allergies
CREATE TABLE IF NOT EXISTS foodallergies (
  foodid INTEGER,
  allergyid INTEGER,
  FOREIGN KEY (foodid) REFERENCES food(foodid),
  FOREIGN KEY (allergyid) REFERENCES allergies(allergyid),
  PRIMARY KEY (foodid, allergyid)
)