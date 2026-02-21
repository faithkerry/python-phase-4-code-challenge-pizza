#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, jsonify
import os

# ----------------- Config -----------------
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

db.init_app(app)
migrate = Migrate(app, db)

# ----------------- Routes -----------------

# Home
@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

# ----------------- RESTAURANTS -----------------
@app.route("/restaurants", methods=["GET"])
def get_restaurants():
    restaurants = Restaurant.query.all()
    return jsonify([r.to_dict(only=("id","name","address")) for r in restaurants])

@app.route("/restaurants/<int:id>", methods=["GET"])
def get_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if restaurant:
        return jsonify(restaurant.to_dict())  # includes restaurant_pizzas automatically
    return jsonify({"error": "Restaurant not found"}), 404

@app.route("/restaurants/<int:id>", methods=["DELETE"])
def delete_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if restaurant:
        db.session.delete(restaurant)
        db.session.commit()
        return '', 204
    return jsonify({"error": "Restaurant not found"}), 404

# ----------------- PIZZAS -----------------
@app.route("/pizzas", methods=["GET"])
def get_pizzas():
    pizzas = Pizza.query.all()
    # Only include id, name, ingredients (exclude restaurant_pizzas)
    return jsonify([p.to_dict(only=("id", "name", "ingredients")) for p in pizzas])

# ----------------- RESTAURANT_PIZZAS -----------------
@app.route("/restaurant_pizzas", methods=["POST"])
def create_restaurant_pizza():
    data = request.get_json()
    price = data.get("price")
    pizza_id = data.get("pizza_id")
    restaurant_id = data.get("restaurant_id")

    # Validate price
    if not 1 <= price <= 30:
        return jsonify({"errors": ["validation errors"]}), 400

    # Check pizza and restaurant exist
    pizza = Pizza.query.get(pizza_id)
    restaurant = Restaurant.query.get(restaurant_id)
    if not pizza or not restaurant:
        return jsonify({"errors": ["Pizza or Restaurant not found"]}), 404

    # Create RestaurantPizza
    restaurant_pizza = RestaurantPizza(
        price=price,
        pizza_id=pizza_id,
        restaurant_id=restaurant_id
    )
    db.session.add(restaurant_pizza)
    db.session.commit()

    return jsonify(restaurant_pizza.to_dict()), 201

# ----------------- RUN SERVER -----------------
if __name__ == "__main__":
    app.run(port=5555, debug=True)