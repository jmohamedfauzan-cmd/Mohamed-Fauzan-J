
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import hashlib

DB = "food_ordering.db"

# ---------------- DATABASE ----------------
def connect():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def setup_database():
    con = connect()
    cur = con.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            address TEXT NOT NULL,
            password TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS restaurants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            cuisine TEXT NOT NULL,
            rating REAL NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS foods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            restaurant_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            category TEXT NOT NULL,
            available INTEGER DEFAULT 1,
            FOREIGN KEY (restaurant_id) REFERENCES restaurants(id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            restaurant_id INTEGER NOT NULL,
            total REAL NOT NULL,
            address TEXT NOT NULL,
            payment TEXT NOT NULL,
            status TEXT NOT NULL,
            order_time TEXT NOT NULL,
            FOREIGN KEY (customer_id) REFERENCES customers(id),
            FOREIGN KEY (restaurant_id) REFERENCES restaurants(id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            food_id INTEGER NOT NULL,
            food_name TEXT NOT NULL,
            price REAL NOT NULL,
            quantity INTEGER NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(id)
        )
    """)

    if cur.execute("SELECT COUNT(*) FROM restaurants").fetchone()[0] == 0:
        restaurants = [
            ("Spice Garden", "Indian", 4.6),
            ("Burger House", "Fast Food", 4.4),
            ("Pizza Corner", "Italian", 4.5),
            ("Chennai Biryani", "South Indian", 4.7)
        ]
        cur.executemany(
            "INSERT INTO restaurants(name,cuisine,rating) VALUES(?,?,?)",
            restaurants
        )

        foods = [
            (1, "Chicken Biryani", 180, "Biryani"),
            (1, "Paneer Butter Masala", 160, "Main Course"),
            (1, "Masala Dosa", 90, "South Indian"),
            (2, "Chicken Burger", 150, "Burger"),
            (2, "Veg Burger", 120, "Burger"),
            (2, "French Fries", 80, "Sides"),
            (3, "Margherita Pizza", 220, "Pizza"),
            (3, "Farmhouse Pizza", 280, "Pizza"),
            (3, "Chicken Pizza", 320, "Pizza"),
            (4, "Chicken Biryani", 190, "Biryani"),
            (4, "Mutton Biryani", 260, "Biryani"),
            (4, "Parotta", 50, "Bread")
        ]
        cur.executemany(
            "INSERT INTO foods(restaurant_id,name,price,category) VALUES(?,?,?,?)",
            foods
        )

    con.commit()
    con.close()


# ---------------- APPLICATION ----------------
class FoodOrderingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FoodHub - Online Food Ordering")
        self.root.geometry("1100x700")
        self.root.minsize(900, 600)

        self.customer_id = None
        self.customer_name = None
        self.cart = {}
        self.selected_restaurant = None

        self.setup_style()
        self.show_home()

    def setup_style(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except:
            pass

        style.configure("Title.TLabel", font=("Arial", 26, "bold"))
        style.configure("Heading.TLabel", font=("Arial", 18, "bold"))
        style.configure("Food.TButton", font=("Arial", 11, "bold"), padding=8)
        style.configure("Action.TButton", font=("Arial", 11, "bold"), padding=10)

    def clear(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def header(self):
        bar = tk.Frame(self.root, bg="#ff5a36", height=65)
        bar.pack(fill="x")
        bar.pack_propagate(False)

        tk.Label(
            bar, text="🍔 FoodHub",
            bg="#ff5a36", fg="white",
            font=("Arial", 22, "bold")
        ).pack(side="left", padx=25)

        tk.Button(
            bar, text="Home", command=self.show_home,
            bg="#ff5a36", fg="white", relief="flat",
            font=("Arial", 10, "bold")
        ).pack(side="left", padx=8)

        tk.Button(
            bar, text="Restaurants", command=self.show_restaurants,
            bg="#ff5a36", fg="white", relief="flat",
            font=("Arial", 10, "bold")
        ).pack(side="left", padx=8)

        tk.Button(
            bar, text=f"Cart ({sum(self.cart.values())})",
            command=self.show_cart,
            bg="#ff5a36", fg="white", relief="flat",
            font=("Arial", 10, "bold")
        ).pack(side="left", padx=8)

        if self.customer_id:
            tk.Button(
                bar, text="My Orders", command=self.show_orders,
                bg="#ff5a36", fg="white", relief="flat",
                font=("Arial", 10, "bold")
            ).pack(side="left", padx=8)

            tk.Button(
                bar, text="Logout", command=self.logout,
                bg="#ff5a36", fg="white", relief="flat",
                font=("Arial", 10, "bold")
            ).pack(side="right", padx=20)

            tk.Label(
                bar, text=f"Hi, {self.customer_name}",
                bg="#ff5a36", fg="white",
                font=("Arial", 10)
            ).pack(side="right", padx=10)
        else:
            tk.Button(
                bar, text="Login", command=self.show_login,
                bg="#ff5a36", fg="white", relief="flat",
                font=("Arial", 10, "bold")
            ).pack(side="right", padx=10)

            tk.Button(
                bar, text="Register", command=self.show_register,
                bg="#ff5a36", fg="white", relief="flat",
                font=("Arial", 10, "bold")
            ).pack(side="right", padx=10)

            tk.Button(
                bar, text="Admin", command=self.show_admin_login,
                bg="#ff5a36", fg="white", relief="flat",
                font=("Arial", 10, "bold")
            ).pack(side="right", padx=10)

    # ---------------- HOME ----------------
    def show_home(self):
        self.clear()
        self.header()

        frame = tk.Frame(self.root, bg="#fff0eb")
        frame.pack(fill="x", padx=35, pady=30)

        tk.Label(
            frame, text="Hungry? Let's fix that. 🍕",
            bg="#fff0eb", fg="#222",
            font=("Arial", 30, "bold")
        ).pack(pady=(30, 5))

        tk.Label(
            frame,
            text="Order delicious food from your favourite restaurants.",
            bg="#fff0eb", fg="#555",
            font=("Arial", 13)
        ).pack(pady=5)

        tk.Button(
            frame, text="Explore Restaurants",
            command=self.show_restaurants,
            bg="#ff5a36", fg="white",
            font=("Arial", 12, "bold"),
            padx=20, pady=10, relief="flat"
        ).pack(pady=25)

        tk.Label(
            self.root, text="Popular Restaurants",
            font=("Arial", 20, "bold")
        ).pack(pady=10)

        con = connect()
        restaurants = con.execute(
            "SELECT * FROM restaurants LIMIT 4"
        ).fetchall()
        con.close()

        grid = tk.Frame(self.root)
        grid.pack(fill="x", padx=35)

        for i, r in enumerate(restaurants):
            card = tk.Frame(
                grid, bg="white",
                highlightbackground="#ddd",
                highlightthickness=1,
                padx=15, pady=15
            )
            card.grid(row=0, column=i, padx=8, sticky="nsew")
            grid.columnconfigure(i, weight=1)

            tk.Label(
                card, text="🍽️",
                font=("Arial", 28),
                bg="white"
            ).pack()

            tk.Label(
                card, text=r["name"],
                font=("Arial", 13, "bold"),
                bg="white"
            ).pack()

            tk.Label(
                card, text=f'{r["cuisine"]}  ⭐ {r["rating"]}',
                bg="white", fg="#666"
            ).pack(pady=5)

            tk.Button(
                card, text="View Menu",
                command=lambda rid=r["id"]: self.show_menu(rid),
                bg="#ff5a36", fg="white",
                relief="flat"
            ).pack(pady=5)

    # ---------------- RESTAURANTS ----------------
    def show_restaurants(self):
        self.clear()
        self.header()

        tk.Label(
            self.root, text="Restaurants",
            font=("Arial", 25, "bold")
        ).pack(pady=20)

        search_frame = tk.Frame(self.root)
        search_frame.pack(fill="x", padx=35)

        search = tk.Entry(search_frame, font=("Arial", 12))
        search.pack(side="left", fill="x", expand=True, ipady=8)

        def search_restaurants():
            self.display_restaurants(search.get())

        tk.Button(
            search_frame, text="Search",
            command=search_restaurants,
            bg="#ff5a36", fg="white",
            font=("Arial", 11, "bold"),
            relief="flat", padx=18
        ).pack(side="left", padx=8)

        self.restaurant_area = tk.Frame(self.root)
        self.restaurant_area.pack(fill="both", expand=True, padx=35, pady=20)

        self.display_restaurants("")

    def display_restaurants(self, query):
        for w in self.restaurant_area.winfo_children():
            w.destroy()

        con = connect()
        restaurants = con.execute(
            """SELECT * FROM restaurants
               WHERE name LIKE ? OR cuisine LIKE ?""",
            (f"%{query}%", f"%{query}%")
        ).fetchall()
        con.close()

        for i, r in enumerate(restaurants):
            card = tk.Frame(
                self.restaurant_area,
                bg="white",
                highlightbackground="#ddd",
                highlightthickness=1,
                padx=20, pady=15
            )
            card.grid(row=i // 3, column=i % 3, padx=10, pady=10, sticky="nsew")

            self.restaurant_area.columnconfigure(i % 3, weight=1)

            tk.Label(
                card, text="🍴",
                font=("Arial", 32), bg="white"
            ).pack()

            tk.Label(
                card, text=r["name"],
                font=("Arial", 15, "bold"), bg="white"
            ).pack()

            tk.Label(
                card, text=f'{r["cuisine"]} | ⭐ {r["rating"]}',
                bg="white", fg="#666"
            ).pack(pady=5)

            tk.Button(
                card, text="View Menu",
                command=lambda rid=r["id"]: self.show_menu(rid),
                bg="#ff5a36", fg="white",
                relief="flat", padx=15, pady=7
            ).pack()

    # ---------------- MENU ----------------
    def show_menu(self, restaurant_id):
        self.clear()
        self.header()
        self.selected_restaurant = restaurant_id

        con = connect()
        restaurant = con.execute(
            "SELECT * FROM restaurants WHERE id=?",
            (restaurant_id,)
        ).fetchone()
        foods = con.execute(
            "SELECT * FROM foods WHERE restaurant_id=? AND available=1",
            (restaurant_id,)
        ).fetchall()
        con.close()

        tk.Label(
            self.root, text=restaurant["name"],
            font=("Arial", 26, "bold")
        ).pack(pady=(20, 3))

        tk.Label(
            self.root,
            text=f'{restaurant["cuisine"]}   ⭐ {restaurant["rating"]}',
            font=("Arial", 12), fg="#666"
        ).pack()

        area = tk.Frame(self.root)
        area.pack(fill="both", expand=True, padx=35, pady=20)

        for i, food in enumerate(foods):
            card = tk.Frame(
                area, bg="white",
                highlightbackground="#ddd",
                highlightthickness=1,
                padx=18, pady=15
            )
            card.grid(row=i // 3, column=i % 3, padx=10, pady=10, sticky="nsew")
            area.columnconfigure(i % 3, weight=1)

            tk.Label(
                card, text="🍽️",
                font=("Arial", 30), bg="white"
            ).pack()

            tk.Label(
                card, text=food["name"],
                font=("Arial", 14, "bold"), bg="white"
            ).pack()

            tk.Label(
                card, text=food["category"],
                bg="white", fg="#777"
            ).pack()

            tk.Label(
                card, text=f'₹{food["price"]:.2f}',
                font=("Arial", 15, "bold"),
                fg="#ff5a36", bg="white"
            ).pack(pady=5)

            tk.Button(
                card, text="Add to Cart",
                command=lambda f=food: self.add_to_cart(f),
                bg="#ff5a36", fg="white",
                relief="flat", padx=12, pady=7
            ).pack()

    # ---------------- CART ----------------
    def add_to_cart(self, food):
        if self.cart:
            first_id = next(iter(self.cart))
            con = connect()
            first = con.execute(
                "SELECT restaurant_id FROM foods WHERE id=?",
                (first_id,)
            ).fetchone()
            con.close()

            if first and first["restaurant_id"] != food["restaurant_id"]:
                messagebox.showwarning(
                    "Different Restaurant",
                    "Your cart can contain food from only one restaurant.\n"
                    "Clear your cart before ordering from another restaurant."
                )
                return

        self.cart[food["id"]] = self.cart.get(food["id"], 0) + 1
        messagebox.showinfo("Added", f'{food["name"]} added to cart.')
        self.show_menu(food["restaurant_id"])

    def show_cart(self):
        self.clear()
        self.header()

        tk.Label(
            self.root, text="Your Cart",
            font=("Arial", 25, "bold")
        ).pack(pady=20)

        if not self.cart:
            tk.Label(
                self.root, text="Your cart is empty 🛒",
                font=("Arial", 16), fg="#777"
            ).pack(pady=50)

            tk.Button(
                self.root, text="Browse Restaurants",
                command=self.show_restaurants,
                bg="#ff5a36", fg="white",
                relief="flat", padx=20, pady=10
            ).pack()
            return

        con = connect()
        subtotal = 0
        items = []

        for food_id, quantity in self.cart.items():
            food = con.execute(
                "SELECT * FROM foods WHERE id=?",
                (food_id,)
            ).fetchone()
            if food:
                total = food["price"] * quantity
                subtotal += total
                items.append((food, quantity, total))

        con.close()

        table = tk.Frame(self.root)
        table.pack(fill="x", padx=40)

        headers = ["Food", "Quantity", "Price", "Total", "Action"]
        for c, h in enumerate(headers):
            tk.Label(
                table, text=h,
                font=("Arial", 11, "bold")
            ).grid(row=0, column=c, padx=20, pady=10)

        for row, (food, quantity, total) in enumerate(items, 1):
            tk.Label(table, text=food["name"]).grid(
                row=row, column=0, padx=20, pady=8
            )

            qty_frame = tk.Frame(table)
            qty_frame.grid(row=row, column=1)

            tk.Button(
                qty_frame, text="-",
                command=lambda fid=food["id"]: self.change_quantity(fid, -1)
            ).pack(side="left")

            tk.Label(
                qty_frame, text=str(quantity),
                width=4
            ).pack(side="left")

            tk.Button(
                qty_frame, text="+",
                command=lambda fid=food["id"]: self.change_quantity(fid, 1)
            ).pack(side="left")

            tk.Label(
                table, text=f"₹{food['price']:.2f}"
            ).grid(row=row, column=2)

            tk.Label(
                table, text=f"₹{total:.2f}"
            ).grid(row=row, column=3)

            tk.Button(
                table, text="Remove",
                command=lambda fid=food["id"]: self.remove_from_cart(fid),
                bg="#d93025", fg="white", relief="flat"
            ).grid(row=row, column=4, padx=10)

        delivery = 40
        tax = subtotal * 0.05
        grand_total = subtotal + delivery + tax

        summary = tk.Frame(self.root, bg="white", padx=25, pady=20)
        summary.pack(anchor="e", padx=50, pady=20)

        tk.Label(summary, text=f"Subtotal: ₹{subtotal:.2f}").pack(anchor="e")
        tk.Label(summary, text=f"Delivery: ₹{delivery:.2f}").pack(anchor="e")
        tk.Label(summary, text=f"Tax (5%): ₹{tax:.2f}").pack(anchor="e")
        tk.Label(
            summary, text=f"Grand Total: ₹{grand_total:.2f}",
            font=("Arial", 16, "bold")
        ).pack(anchor="e", pady=5)

        buttons = tk.Frame(self.root)
        buttons.pack()

        tk.Button(
            buttons, text="Clear Cart",
            command=self.clear_cart,
            bg="#d93025", fg="white",
            relief="flat", padx=15, pady=8
        ).pack(side="left", padx=8)

        tk.Button(
            buttons, text="Checkout",
            command=self.checkout,
            bg="#ff5a36", fg="white",
            relief="flat", padx=15, pady=8
        ).pack(side="left", padx=8)

    def change_quantity(self, food_id, amount):
        self.cart[food_id] = self.cart.get(food_id, 0) + amount
        if self.cart[food_id] <= 0:
            del self.cart[food_id]
        self.show_cart()

    def remove_from_cart(self, food_id):
        self.cart.pop(food_id, None)
        self.show_cart()

    def clear_cart(self):
        self.cart.clear()
        self.show_cart()

    # ---------------- REGISTER ----------------
    def show_register(self):
        self.clear()
        self.header()

        tk.Label(
            self.root, text="Create Customer Account",
            font=("Arial", 24, "bold")
        ).pack(pady=25)

        form = tk.Frame(self.root, padx=40)
        form.pack()

        fields = {}
        labels = ["Name", "Phone", "Address", "Password"]

        for i, label in enumerate(labels):
            tk.Label(
                form, text=label,
                font=("Arial", 11, "bold")
            ).grid(row=i, column=0, sticky="w", pady=7)

            entry = tk.Entry(
                form, width=40,
                show="*" if label == "Password" else ""
            )
            entry.grid(row=i, column=1, pady=7)
            fields[label] = entry

        def register():
            name = fields["Name"].get().strip()
            phone = fields["Phone"].get().strip()
            address = fields["Address"].get().strip()
            password = fields["Password"].get()

            if not all([name, phone, address, password]):
                messagebox.showwarning(
                    "Missing Details",
                    "Please fill all fields."
                )
                return

            con = connect()
            con.execute(
                "INSERT INTO customers(name,phone,address,password) VALUES(?,?,?,?)",
                (name, phone, address, hash_password(password))
            )
            con.commit()
            con.close()

            messagebox.showinfo(
                "Success",
                "Registration successful. You can now login."
            )
            self.show_login()

        tk.Button(
            self.root, text="Register",
            command=register,
            bg="#ff5a36", fg="white",
            font=("Arial", 12, "bold"),
            relief="flat", padx=25, pady=10
        ).pack(pady=20)

    # ---------------- LOGIN ----------------
    def show_login(self):
        self.clear()
        self.header()

        tk.Label(
            self.root, text="Customer Login",
            font=("Arial", 24, "bold")
        ).pack(pady=30)

        form = tk.Frame(self.root)
        form.pack()

        tk.Label(form, text="Phone", font=("Arial", 11, "bold")).grid(
            row=0, column=0, pady=10, sticky="w"
        )
        phone = tk.Entry(form, width=35)
        phone.grid(row=0, column=1, pady=10)

        tk.Label(form, text="Password", font=("Arial", 11, "bold")).grid(
            row=1, column=0, pady=10, sticky="w"
        )
        password = tk.Entry(form, width=35, show="*")
        password.grid(row=1, column=1, pady=10)

        def login():
            con = connect()
            customer = con.execute(
                "SELECT * FROM customers WHERE phone=?",
                (phone.get().strip(),)
            ).fetchone()
            con.close()

            if customer and check_password_hash(
                customer["password"], password.get()
            ):
                self.customer_id = customer["id"]
                self.customer_name = customer["name"]
                messagebox.showinfo(
                    "Login Successful",
                    f"Welcome, {customer['name']}!"
                )
                self.show_home()
            else:
                messagebox.showerror(
                    "Login Failed",
                    "Invalid phone number or password."
                )

        tk.Button(
            self.root, text="Login",
            command=login,
            bg="#ff5a36", fg="white",
            font=("Arial", 12, "bold"),
            relief="flat", padx=30, pady=10
        ).pack(pady=20)

    def logout(self):
        self.customer_id = None
        self.customer_name = None
        self.cart.clear()
        self.show_home()

    # ---------------- CHECKOUT ----------------
    def checkout(self):
        if not self.customer_id:
            messagebox.showwarning(
                "Login Required",
                "Please login before checkout."
            )
            self.show_login()
            return

        if not self.cart:
            return

        con = connect()
        customer = con.execute(
            "SELECT * FROM customers WHERE id=?",
            (self.customer_id,)
        ).fetchone()

        subtotal = 0
        restaurant_id = None

        for food_id, quantity in self.cart.items():
            food = con.execute(
                "SELECT * FROM foods WHERE id=?",
                (food_id,)
            ).fetchone()
            if food:
                restaurant_id = food["restaurant_id"]
                subtotal += food["price"] * quantity

        con.close()

        delivery = 40
        tax = subtotal * 0.05
        total = subtotal + delivery + tax

        self.clear()
        self.header()

        tk.Label(
            self.root, text="Checkout",
            font=("Arial", 25, "bold")
        ).pack(pady=20)

        form = tk.Frame(self.root)
        form.pack()

        tk.Label(
            form, text="Delivery Address",
            font=("Arial", 11, "bold")
        ).pack(anchor="w")

        address = tk.Text(form, width=55, height=4)
        address.pack(pady=5)
        address.insert("1.0", customer["address"])

        tk.Label(
            form, text="Payment Method",
            font=("Arial", 11, "bold")
        ).pack(anchor="w", pady=(15, 3))

        payment = ttk.Combobox(
            form,
            values=["Cash on Delivery", "Demo Online Payment"],
            state="readonly", width=35
        )
        payment.current(0)
        payment.pack()

        tk.Label(
            form,
            text=f"\nSubtotal: ₹{subtotal:.2f}\n"
                 f"Delivery: ₹{delivery:.2f}\n"
                 f"Tax: ₹{tax:.2f}\n"
                 f"TOTAL: ₹{total:.2f}",
            font=("Arial", 13, "bold"),
            justify="left"
        ).pack(anchor="w", pady=20)

        def place_order():
            delivery_address = address.get("1.0", "end").strip()

            if not delivery_address:
                messagebox.showwarning(
                    "Address Required",
                    "Please enter a delivery address."
                )
                return

            con = connect()

            cur = con.execute(
                """INSERT INTO orders
                   (customer_id,restaurant_id,total,address,payment,status,order_time)
                   VALUES(?,?,?,?,?,?,?)""",
                (
                    self.customer_id,
                    restaurant_id,
                    total,
                    delivery_address,
                    payment.get(),
                    "Placed",
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                )
            )

            order_id = cur.lastrowid

            for food_id, quantity in self.cart.items():
                food = con.execute(
                    "SELECT * FROM foods WHERE id=?",
                    (food_id,)
                ).fetchone()

                con.execute(
                    """INSERT INTO order_items
                       (order_id,food_id,food_name,price,quantity)
                       VALUES(?,?,?,?,?)""",
                    (
                        order_id,
                        food["id"],
                        food["name"],
                        food["price"],
                        quantity
                    )
                )

            con.commit()
            con.close()

            self.cart.clear()

            messagebox.showinfo(
                "Order Placed!",
                f"Order #{order_id} placed successfully!"
            )

            self.show_order_details(order_id)

        tk.Button(
            self.root, text="Place Order",
            command=place_order,
            bg="#ff5a36", fg="white",
            font=("Arial", 13, "bold"),
            relief="flat", padx=30, pady=12
        ).pack()

    # ---------------- ORDERS ----------------
    def show_orders(self):
        self.clear()
        self.header()

        tk.Label(
            self.root, text="My Orders",
            font=("Arial", 25, "bold")
        ).pack(pady=20)

        con = connect()
        orders = con.execute(
            """SELECT o.*, r.name restaurant
               FROM orders o
               JOIN restaurants r ON r.id=o.restaurant_id
               WHERE o.customer_id=?
               ORDER BY o.id DESC""",
            (self.customer_id,)
        ).fetchall()
        con.close()

        if not orders:
            tk.Label(
                self.root, text="No orders yet.",
                font=("Arial", 15), fg="#777"
            ).pack(pady=40)
            return

        area = tk.Frame(self.root)
        area.pack(fill="both", expand=True, padx=40)

        for i, order in enumerate(orders):
            card = tk.Frame(
                area, bg="white",
                highlightbackground="#ddd",
                highlightthickness=1,
                padx=20, pady=15
            )
            card.pack(fill="x", pady=8)

            tk.Label(
                card,
                text=f"Order #{order['id']}  |  {order['restaurant']}",
                font=("Arial", 14, "bold"),
                bg="white"
            ).pack(anchor="w")

            tk.Label(
                card,
                text=f"₹{order['total']:.2f}   |   Status: {order['status']}",
                bg="white"
            ).pack(anchor="w", pady=5)

            tk.Button(
                card, text="View Details",
                command=lambda oid=order["id"]: self.show_order_details(oid),
                bg="#ff5a36", fg="white",
                relief="flat"
            ).pack(anchor="e")

    def show_order_details(self, order_id):
        self.clear()
        self.header()

        con = connect()
        order = con.execute(
            """SELECT o.*,r.name restaurant
               FROM orders o JOIN restaurants r ON r.id=o.restaurant_id
               WHERE o.id=?""",
            (order_id,)
        ).fetchone()

        items = con.execute(
            "SELECT * FROM order_items WHERE order_id=?",
            (order_id,)
        ).fetchall()
        con.close()

        tk.Label(
            self.root,
            text=f"Order #{order_id}",
            font=("Arial", 25, "bold")
        ).pack(pady=20)

        info = tk.Frame(self.root, bg="white", padx=25, pady=20)
        info.pack(fill="x", padx=40)

        tk.Label(
            info, text=f"Restaurant: {order['restaurant']}",
            font=("Arial", 13, "bold"), bg="white"
        ).pack(anchor="w")

        tk.Label(
            info, text=f"Status: {order['status']}",
            font=("Arial", 13, "bold"),
            fg="#ff5a36", bg="white"
        ).pack(anchor="w", pady=5)

        tk.Label(
            info, text=f"Payment: {order['payment']}",
            bg="white"
        ).pack(anchor="w")

        tk.Label(
            info, text=f"Address: {order['address']}",
            bg="white", wraplength=900
        ).pack(anchor="w", pady=5)

        tk.Label(
            self.root, text="Items",
            font=("Arial", 18, "bold")
        ).pack(anchor="w", padx=40, pady=(20, 5))

        for item in items:
            tk.Label(
                self.root,
                text=f"{item['food_name']} × {item['quantity']}   "
                     f"₹{item['price'] * item['quantity']:.2f}",
                font=("Arial", 11)
            ).pack(anchor="w", padx=55, pady=3)

        tk.Label(
            self.root,
            text=f"TOTAL: ₹{order['total']:.2f}",
            font=("Arial", 16, "bold")
        ).pack(anchor="e", padx=60, pady=20)

    # ---------------- ADMIN ----------------
    def show_admin_login(self):
        self.clear()
        self.header()

        tk.Label(
            self.root, text="Admin Login",
            font=("Arial", 25, "bold")
        ).pack(pady=30)

        form = tk.Frame(self.root)
        form.pack()

        tk.Label(form, text="Username").grid(row=0, column=0, pady=10)
        username = tk.Entry(form, width=30)
        username.grid(row=0, column=1, pady=10)

        tk.Label(form, text="Password").grid(row=1, column=0, pady=10)
        password = tk.Entry(form, width=30, show="*")
        password.grid(row=1, column=1, pady=10)

        def login():
            if username.get() == "admin" and password.get() == "admin123":
                self.show_admin()
            else:
                messagebox.showerror(
                    "Invalid Login",
                    "Username or password is incorrect."
                )

        tk.Button(
            self.root, text="Admin Login",
            command=login,
            bg="#333", fg="white",
            font=("Arial", 12, "bold"),
            relief="flat", padx=25, pady=10
        ).pack(pady=20)

        tk.Label(
            self.root,
            text="Demo: admin / admin123",
            fg="#777"
        ).pack()

    def show_admin(self):
        self.clear()

        top = tk.Frame(self.root, bg="#222", height=65)
        top.pack(fill="x")
        top.pack_propagate(False)

        tk.Label(
            top, text="FoodHub Admin Dashboard",
            bg="#222", fg="white",
            font=("Arial", 20, "bold")
        ).pack(side="left", padx=25)

        tk.Button(
            top, text="Logout",
            command=self.show_home,
            bg="#222", fg="white",
            relief="flat"
        ).pack(side="right", padx=25)

        con = connect()

        customers = con.execute(
            "SELECT COUNT(*) FROM customers"
        ).fetchone()[0]

        restaurants = con.execute(
            "SELECT COUNT(*) FROM restaurants"
        ).fetchone()[0]

        foods = con.execute(
            "SELECT COUNT(*) FROM foods"
        ).fetchone()[0]

        orders = con.execute(
            "SELECT COUNT(*) FROM orders"
        ).fetchone()[0]

        revenue = con.execute(
            "SELECT COALESCE(SUM(total),0) FROM orders WHERE status!='Cancelled'"
        ).fetchone()[0]

        all_orders = con.execute(
            """SELECT o.*,c.name customer,r.name restaurant
               FROM orders o
               JOIN customers c ON c.id=o.customer_id
               JOIN restaurants r ON r.id=o.restaurant_id
               ORDER BY o.id DESC"""
        ).fetchall()

        con.close()

        stats = tk.Frame(self.root)
        stats.pack(fill="x", padx=30, pady=25)

        values = [
            ("Customers", customers),
            ("Restaurants", restaurants),
            ("Food Items", foods),
            ("Orders", orders),
            ("Revenue", f"₹{revenue:.2f}")
        ]

        for i, (name, value) in enumerate(values):
            card = tk.Frame(
                stats, bg="white",
                highlightbackground="#ddd",
                highlightthickness=1,
                padx=25, pady=15
            )
            card.grid(row=0, column=i, padx=6, sticky="nsew")
            stats.columnconfigure(i, weight=1)

            tk.Label(
                card, text=str(value),
                font=("Arial", 18, "bold"),
                bg="white"
            ).pack()

            tk.Label(
                card, text=name,
                bg="white", fg="#666"
            ).pack()

        tk.Label(
            self.root, text="Manage Orders",
            font=("Arial", 20, "bold")
        ).pack(anchor="w", padx=30)

        area = tk.Frame(self.root)
        area.pack(fill="both", expand=True, padx=30, pady=10)

        canvas = tk.Canvas(area)
        scrollbar = ttk.Scrollbar(
            area, orient="vertical", command=canvas.yview
        )
        inner = tk.Frame(canvas)

        inner.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        statuses = [
            "Placed", "Confirmed", "Preparing",
            "Ready for Pickup", "Out for Delivery",
            "Delivered", "Cancelled"
        ]

        for order in all_orders:
            row = tk.Frame(
                inner, bg="white",
                highlightbackground="#ddd",
                highlightthickness=1,
                padx=15, pady=10
            )
            row.pack(fill="x", pady=5)

            tk.Label(
                row,
                text=f"#{order['id']} | {order['customer']} | "
                     f"{order['restaurant']} | ₹{order['total']:.2f}",
                bg="white",
                font=("Arial", 10, "bold")
            ).pack(side="left")

            combo = ttk.Combobox(
                row, values=statuses,
                state="readonly", width=20
            )
            combo.set(order["status"])
            combo.pack(side="left", padx=10)

            tk.Button(
                row, text="Update",
                command=lambda oid=order["id"], cb=combo:
                    self.update_order_status(oid, cb.get()),
                bg="#ff5a36", fg="white",
                relief="flat"
            ).pack(side="left")

    def update_order_status(self, order_id, status):
        con = connect()
        con.execute(
            "UPDATE orders SET status=? WHERE id=?",
            (status, order_id)
        )
        con.commit()
        con.close()

        messagebox.showinfo(
            "Updated",
            f"Order #{order_id} status changed to {status}."
        )
        self.show_admin()


def check_password_hash(stored_hash, password):
    return stored_hash == hash_password(password)


if __name__ == "__main__":
    setup_database()

    root = tk.Tk()
    app = FoodOrderingApp(root)
    root.mainloop()
