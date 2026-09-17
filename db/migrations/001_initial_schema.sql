-- Migration: 001_initial_schema (PostgreSQL)
-- Description: Initial database schema for Pantry Pal
-- Created: 2026-09-17
-- Notes: ERD design artifact lives at docs/erd/pantry-pal-diagram.json
--        This file is immutable once applied; future changes go in 002_*.sql, 003_*.sql, ...

CREATE TABLE Cook (
    cook_id            INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    username           VARCHAR(50)  NOT NULL UNIQUE,
    email              VARCHAR(255) NOT NULL UNIQUE,
    password_hash      VARCHAR(255) NOT NULL,
    display_name       VARCHAR(100),
    created_at         TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Pantry (
    pantry_id          INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    cook_id            INT NOT NULL UNIQUE REFERENCES Cook(cook_id),
    created_at         TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Ingredient (
    ingredient_id      INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name               VARCHAR(120) NOT NULL UNIQUE,
    category           VARCHAR(50),
    default_unit       VARCHAR(20)
);

CREATE TABLE Recipe (
    recipe_id          INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    title              VARCHAR(200) NOT NULL,
    description        TEXT,
    instructions       TEXT,
    created_by_cook_id INT NOT NULL REFERENCES Cook(cook_id),
    prep_time_minutes  INT,
    cook_time_minutes  INT,
    servings           INT,
    cuisine            VARCHAR(50),
    published_at       TIMESTAMP
);

CREATE TABLE RecipeIngredient (
    recipe_ingredient_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    recipe_id            INT NOT NULL REFERENCES Recipe(recipe_id),
    ingredient_id        INT NOT NULL REFERENCES Ingredient(ingredient_id),
    quantity             NUMERIC(10,2) NOT NULL,
    unit                 VARCHAR(20) NOT NULL,
    is_optional          BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE PantryIngredient (
    pantry_ingredient_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    pantry_id            INT NOT NULL REFERENCES Pantry(pantry_id),
    ingredient_id        INT NOT NULL REFERENCES Ingredient(ingredient_id),
    quantity             NUMERIC(10,2) NOT NULL,
    unit                 VARCHAR(20) NOT NULL,
    expiry_date          TIMESTAMP,
    added_at             TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE SavedRecipe (
    saved_recipe_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    cook_id         INT NOT NULL REFERENCES Cook(cook_id),
    recipe_id       INT NOT NULL REFERENCES Recipe(recipe_id),
    saved_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    notes           TEXT,
    UNIQUE (cook_id, recipe_id)
);