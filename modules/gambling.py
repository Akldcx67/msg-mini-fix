from flask import Flask, request, jsonify

app = Flask(__name__)

# Data storage (in-memory for simplicity)
users = {}
items = {}
cases = {}

class User:
    _next_user_id = 1

    def __init__(self, username):
        self.user_id = User._next_user_id
        User._next_user_id += 1
        self.username = username
        self._inventory = []

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, username):
        if not isinstance(username, str):
            raise ValueError("Username must be a string.")
        self._username = username

    def add_item(self, item):
        if not isinstance(item, Item):
            raise ValueError("Only Item objects can be added to the inventory.")
        if item.owner_id is not None:
            raise ValueError("Item already belongs to another user.")
        item.owner_id = self.user_id
        self._inventory.append(item)

    def remove_item(self, item):
        if item in self._inventory:
            item.owner_id = None
            self._inventory.remove(item)
        else:
            raise ValueError("Item not found in the user's inventory.")

    def get_inventory(self):
        return self._inventory

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "username": self.username,
            "inventory": [item.to_dict() for item in self._inventory],
        }


class Item:
    _next_item_id = 1

    def __init__(self, name, value):
        self.item_id = Item._next_item_id
        Item._next_item_id += 1
        self.name = name
        self.value = value
        self._effects = []
        self.owner_id = None

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        if not isinstance(name, str):
            raise ValueError("Name must be a string.")
        self._name = name

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if not isinstance(value, (int, float)) or value < 0:
            raise ValueError("Value must be a non-negative number.")
        self._value = value

    def add_effect(self, effect):
        if not isinstance(effect, str):
            raise ValueError("Effect must be a string.")
        self._effects.append(effect)

    def remove_effect(self, effect):
        if effect in self._effects:
            self._effects.remove(effect)
        else:
            raise ValueError(f"Effect '{effect}' not found in the item.")

    def get_effects(self):
        return self._effects

    def to_dict(self):
        return {
            "item_id": self.item_id,
            "name": self.name,
            "value": self.value,
            "effects": self._effects,
            "owner_id": self.owner_id,
        }


class Case:
    _next_case_id = 1

    def __init__(self, description):
        self.case_id = Case._next_case_id
        Case._next_case_id += 1
        self.description = description
        self._items = []
        self.owner_id = None

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, description):
        if not isinstance(description, str):
            raise ValueError("Description must be a string.")
        self._description = description

    def add_item(self, item):
        if not isinstance(item, Item):
            raise ValueError("Only Item objects can be added to the case.")
        if item.owner_id != self.owner_id:
            raise ValueError("Item does not belong to the case owner.")
        self._items.append(item)

    def remove_item(self, item_id):
        for item in self._items:
            if item.item_id == item_id:
                self._items.remove(item)
                return
        raise ValueError(f"Item with ID {item_id} not found in the case.")

    def get_items(self):
        return self._items

    def total_value(self):
        return sum(item.value for item in self._items)

    def to_dict(self):
        return {
            "case_id": self.case_id,
            "description": self.description,
            "owner_id": self.owner_id,
            "items": [item.to_dict() for item in self._items],
        }


# Flask Routes

@app.route("/users", methods=["POST"])
def create_user():
    data = request.json
    username = data.get("username")
    if not username:
        return jsonify({"error": "Username is required"}), 400
    user = User(username)
    users[user.user_id] = user
    return jsonify(user.to_dict()), 201


@app.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = users.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user.to_dict())


@app.route("/items", methods=["POST"])
def create_item():
    data = request.json
    name = data.get("name")
    value = data.get("value")
    if not name or not value:
        return jsonify({"error": "Name and value are required"}), 400
    item = Item(name, value)
    items[item.item_id] = item
    return jsonify(item.to_dict()), 201


@app.route("/items/<int:item_id>", methods=["GET"])
def get_item(item_id):
    item = items.get(item_id)
    if not item:
        return jsonify({"error": "Item not found"}), 404
    return jsonify(item.to_dict())


@app.route("/trade", methods=["POST"])
def trade_item():
    data = request.json
    sender_id = data.get("sender_id")
    receiver_id = data.get("receiver_id")
    item_id = data.get("item_id")
    if not sender_id or not receiver_id or not item_id:
        return jsonify({"error": "Sender ID, receiver ID, and item ID are required"}), 400

    sender = users.get(sender_id)
    receiver = users.get(receiver_id)
    item = items.get(item_id)

    if not sender or not receiver or not item:
        return jsonify({"error": "Invalid sender, receiver, or item"}), 404

    if item.owner_id != sender.user_id:
        return jsonify({"error": "Sender does not own the item"}), 400

    sender.remove_item(item)
    receiver.add_item(item)
    return jsonify({"message": f"Item '{item.name}' traded from {sender.username} to {receiver.username}."})


@app.route("/cases", methods=["POST"])
def create_case():
    data = request.json
    description = data.get("description")
    if not description:
        return jsonify({"error": "Description is required"}), 400
    case = Case(description)
    cases[case.case_id] = case
    return jsonify(case.to_dict()), 201


@app.route("/cases/<int:case_id>", methods=["GET"])
def get_case(case_id):
    case = cases.get(case_id)
    if not case:
        return jsonify({"error": "Case not found"}), 404
    return jsonify(case.to_dict())


if __name__ == "__main__":
    app.run(debug=True)