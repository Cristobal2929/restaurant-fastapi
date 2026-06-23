# -*- coding: utf-8 -*-
import os
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# ----------------------------------------------------------------------
# Database setup
# ----------------------------------------------------------------------
DATABASE_URL = "sqlite:///restaurant.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String, nullable=False)
    item = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)


# ----------------------------------------------------------------------
# FastAPI app
# ----------------------------------------------------------------------
app = FastAPI()


@app.on_event("startup")
def startup():
    # Create tables if they do not exist
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ----------------------------------------------------------------------
# Routes
# ----------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
def read_root():
    # Retrieve all orders and compute total revenue
    db = next(get_db())
    orders = db.query(Order).order_by(Order.id.desc()).all()
    total_revenue = sum(o.quantity * o.price for o in orders)

    # Build HTML page
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Restaurant Orders</title>
        <style>
            body {{
                font-family: Arial, Helvetica, sans-serif;
                margin: 20px;
                padding: 0;
                background-color: #f9f9f9;
            }}
            .container {{
                max-width: 800px;
                margin: auto;
                background: #fff;
                padding: 20px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                border-radius: 8px;
            }}
            h1 {{
                text-align: center;
                color: #333;
            }}
            form {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 10px;
                margin-bottom: 20px;
            }}
            form input[type="text"],
            form input[type="number"] {{
                width: 100%;
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
            }}
            form button {{
                grid-column: span 2;
                padding: 10px;
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
            }}
            form button:hover {{
                background-color: #218838;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
            }}
            th, td {{
                padding: 8px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }}
            th {{
                background-color: #f2f2f2;
            }}
            .total {{
                text-align: right;
                font-weight: bold;
                margin-top: 10px;
            }}
            @media (max-width: 600px) {{
                form {{
                    grid-template-columns: 1fr;
                }}
                form button {{
                    grid-column: span 1;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Restaurant Orders</h1>
            <form action="/add" method="post">
                <input type="text" name="customer_name" placeholder="Customer Name" required>
                <input type="text" name="item" placeholder="Item" required>
                <input type="number" name="quantity" placeholder="Quantity" min="1" required>
                <input type="number" name="price" placeholder="Price per Item" step="0.01" min="0" required>
                <button type="submit">Add Order</button>
            </form>

            <h2>Current Orders</h2>
            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Customer</th>
                        <th>Item</th>
                        <th>Qty</th>
                        <th>Price</th>
                        <th>Total</th>
                    </tr>
                </thead>
                <tbody>
    """
    for order in orders:
        line_total = order.quantity * order.price
        html_content += f"""
                    <tr>
                        <td>{order.id}</td>
                        <td>{order.customer_name}</td>
                        <td>{order.item}</td>
                        <td>{order.quantity}</td>
                        <td>${order.price:.2f}</td>
                        <td>${line_total:.2f}</td>
                    </tr>
        """
    html_content += f"""
                </tbody>
            </table>
            <div class="total">Total Revenue: ${total_revenue:.2f}</div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.post("/add")
def add_order(
    customer_name: str = Form(...),
    item: str = Form(...),
    quantity: int = Form(...),
    price: float = Form(...),
):
    db = next(get_db())
    new_order = Order(
        customer_name=customer_name,
        item=item,
        quantity=quantity,
        price=price,
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    return RedirectResponse(url="/", status_code=303)


if __name__ == "__main__":
    import os, uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))