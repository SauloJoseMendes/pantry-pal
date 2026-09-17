-- Migration: 001_initial_schema
-- Description: Initial database schema for Pantry Pal
-- Created: 2026-09-17
CREATE TABLE Cook (
    cook_id            INT AUTO_INCREMENT PRIMARY KEY,
    username           VARCHAR(50)  NOT NULL UNIQUE,
    email              VARCHAR(255) NOT NULL UNIQUE,
    password_hash      VARCHAR(255) NOT NULL,
    display_name       VARCHAR(100),
    created_at         DATETIME     NOT NULL
);

CREATE TABLE Pantry (
    pantry_id          INT AUTO_INCREMENT PRIMARY KEY,
    cook_id            INT NOT NULL UNIQUE,            
    created_at         DATETIME NOT NULL,
    FOREIGN KEY (cook_id) REFERENCES Cook(cook_id)
);

CREATE TABLE Ingredient (
    ingredient_id      INT AUTO_INCREMENT PRIMARY KEY,
    name               VARCHAR(120) NOT NULL UNIQUE,
    category           VARCHAR(50),
    default_unit       VARCHAR(20)
);

CREATE TABLE Recipe (
    recipe_id          INT AUTO_INCREMENT PRIMARY KEY,
    title              VARCHAR(200) NOT NULL,
    description        TEXT,
    instructions       TEXT,
    created_by_cook_id INT,                            
    source             VARCHAR(50) NOT NULL DEFAULT 'user',
    source_url         VARCHAR(2048),                  
    prep_time_minutes  INT,
    cook_time_minutes  INT,
    servings           INT,
    cuisine            VARCHAR(50),
    published_at       DATETIME,
    FOREIGN KEY (created_by_cook_id) REFERENCES Cook(cook_id),
    CHECK (created_by_cook_id IS NOT NULL OR source <> 'user')  
);

CREATE TABLE RecipeIngredient (
    recipe_ingredient_id INT AUTO_INCREMENT PRIMARY KEY,
    recipe_id            INT NOT NULL,
    ingredient_id        INT NOT NULL,
    quantity             DECIMAL(10,2) NOT NULL,
    unit                 VARCHAR(20) NOT NULL,
    is_optional          BOOLEAN NOT NULL DEFAULT FALSE,
    FOREIGN KEY (recipe_id)     REFERENCES Recipe(recipe_id),
    FOREIGN KEY (ingredient_id) REFERENCES Ingredient(ingredient_id)
);

CREATE TABLE PantryIngredient (
    pantry_ingredient_id INT AUTO_INCREMENT PRIMARY KEY,
    pantry_id            INT NOT NULL,
    ingredient_id        INT NOT NULL,
    quantity             DECIMAL(10,2) NOT NULL,
    unit                 VARCHAR(20) NOT NULL,
    expiry_date          DATETIME,
    added_at             DATETIME NOT NULL,
    FOREIGN KEY (pantry_id)     REFERENCES Pantry(pantry_id),
    FOREIGN KEY (ingredient_id) REFERENCES Ingredient(ingredient_id)
);

CREATE TABLE SavedRecipe (
    saved_recipe_id INT AUTO_INCREMENT PRIMARY KEY,
    cook_id         INT NOT NULL,
    recipe_id       INT NOT NULL,
    saved_at        DATETIME NOT NULL,
    notes           TEXT,
    FOREIGN KEY (cook_id)   REFERENCES Cook(cook_id),
    FOREIGN KEY (recipe_id) REFERENCES Recipe(recipe_id),
    UNIQUE (cook_id, recipe_id)
);