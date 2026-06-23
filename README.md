---
title: Restaurant Order Manager
emoji: 🍽️
colorFrom: teal
colorTo: teal
sdk: streamlit
app_file: app.py
---

# Restaurant Order Manager

A simple Gradio web app that lets a restaurant staff:

- **Add new orders** (customer name, item, quantity, price)
- **View all current orders** in a table
- **See total revenue** automatically updated
- **Delete an order** by selecting its ID

The data is stored locally in a SQLite database (`restaurant.db`) using SQLAlchemy, so the information persists between sessions.

## How to run locally