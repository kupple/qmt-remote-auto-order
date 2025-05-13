people = [
    {"name": "Alice", "age": 30},
    {"name": "Bob", "age": 25},
    {"name": "Charlie", "age": 30}
]

print(next((item for item in people if item.get("name") == "Alice"), None))