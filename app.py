

import streamlit as st
import pandas as pd
import mysql.connector
from mysql.connector import Error
import hashlib



# Login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Sales Intelligence Hub Login")
    login_username = st.text_input("Username")
    login_password = st.text_input("Password", type="password")
    db_password = st.text_input(
        "MySQL root password", type="password"
    )

    if st.button("Login"):
        try:
            conn = mysql.connector.connect(
                host="127.0.0.1",
                port=3306,
                user="root",
                password=db_password,
                database="sales_intelligence_hub"
            )

            cursor = conn.cursor(dictionary=True)
            password_hash = hashlib.sha256(
                login_password.encode("utf-8")
            ).hexdigest()

            cursor.execute(
                """SELECT user_id, username, branch_id, role
                   FROM users
                   WHERE username = %s AND password = %s""",
                (login_username, password_hash)
            )
            account = cursor.fetchone()
            cursor.close()
            conn.close()

            if account:
                st.session_state.logged_in = True
                st.session_state.username = account["username"]
                st.session_state.role = account["role"]
                st.session_state.branch_id = account["branch_id"]
                st.session_state.db_password = db_password
                st.rerun()
            else:
                st.error("Invalid username or password.")

        except Error as e:
            st.error(f"Database connection failed: {e}")

    st.stop()


st.set_page_config(
    page_title="Sales Intelligence Hub",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Sales Intelligence Hub")
st.caption("Sales Analytics & Financial Tracking System")


# Database settings
host = "127.0.0.1"
port = 3306
user = "root"
password = st.session_state.get("db_password", "")

def get_connection():
    return mysql.connector.connect(
        host=host,
        port=int(port),
        user=user,
        password=password,
        database="sales_intelligence_hub"
    )

def read_data(query, params=None):
    conn = get_connection()
    try:
        return pd.read_sql(query, conn, params=params)
    finally:
        conn.close()

def execute_query(query, params=None):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        conn.commit()
        cursor.close()
    finally:
        conn.close()

if not password:
    st.info("Enter your MySQL root password in the sidebar to connect.")
    st.stop()

try:
    conn = get_connection()
    conn.close()
    st.sidebar.success("MySQL connected")
except Error as e:
    st.error(f"Database connection failed: {e}")
    st.stop()


# Sidebar navigation based on user role
if st.session_state.role == "Super Admin":
    menu_options = [
        "Dashboard",
        "Sales Records",
        "Add Sale",
        "Record Payment",
        "Pending Payments",
        "SQL Reports"
    ]
else:
    menu_options = [
        "Dashboard",
        "Sales Records",
        "Add Sale",
        "Record Payment",
        "Pending Payments"
    ]

page = st.sidebar.radio("Navigation", menu_options)

st.sidebar.write(f"Logged in as: {st.session_state.username}")
st.sidebar.write(f"Role: {st.session_state.role}")

if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()


# Dashboard
if page == "Dashboard":
    st.subheader("Business Overview")

    totals = read_data("""
        SELECT
            COALESCE(SUM(gross_sales), 0) AS gross,
            COALESCE(SUM(received_amount), 0) AS received,
            COALESCE(SUM(pending_amount), 0) AS pending,
            COUNT(*) AS sales_count
        FROM customer_sales
    """)

    a, b, c, d = st.columns(4)
    a.metric("Total Sales", f"₹{totals.iloc[0]['gross']:,.2f}")
    b.metric("Amount Received", f"₹{totals.iloc[0]['received']:,.2f}")
    c.metric("Amount Pending", f"₹{totals.iloc[0]['pending']:,.2f}")
    d.metric("Total Sales Records", int(totals.iloc[0]["sales_count"]))

    st.divider()

    left, right = st.columns(2)

    with left:
        st.subheader("Branch-wise Sales")
        branch_data = read_data("""
            SELECT b.branch_name,
                   COALESCE(SUM(s.gross_sales), 0) AS gross_sales
            FROM branches b
            LEFT JOIN customer_sales s
                ON b.branch_id = s.branch_id
            GROUP BY b.branch_id, b.branch_name
            ORDER BY gross_sales DESC
        """)
        st.bar_chart(
            branch_data.set_index("branch_name")["gross_sales"]
        )
        st.dataframe(branch_data, width="stretch")

    with right:
        st.subheader("Monthly Sales Trend")
        monthly = read_data("""
            SELECT DATE_FORMAT(date, '%Y-%m') AS month,
                   SUM(gross_sales) AS gross_sales
            FROM customer_sales
            GROUP BY DATE_FORMAT(date, '%Y-%m')
            ORDER BY month
        """)
        if not monthly.empty:
            st.line_chart(monthly.set_index("month")["gross_sales"])
        else:
            st.info("No monthly sales data available.")

    st.subheader("Payment Method Summary")
    methods = read_data("""
        SELECT payment_method, SUM(amount_paid) AS total_collection
        FROM payment_splits
        GROUP BY payment_method
        ORDER BY total_collection DESC
    """)
    st.dataframe(methods, width="stretch")


# Sales records - restrict Admin to assigned branch
elif page == "Sales Records":
    st.subheader("Sales Records")

    if st.session_state.role == "Super Admin":
        sales = read_data("""
            SELECT s.sale_id, s.date, s.name, s.mobile_number,
                   s.product_name, b.branch_name, s.gross_sales,
                   s.received_amount, s.pending_amount, s.status
            FROM customer_sales s
            JOIN branches b ON s.branch_id = b.branch_id
            ORDER BY s.date DESC
        """)
    else:
        sales = read_data("""
            SELECT s.sale_id, s.date, s.name, s.mobile_number,
                   s.product_name, b.branch_name, s.gross_sales,
                   s.received_amount, s.pending_amount, s.status
            FROM customer_sales s
            JOIN branches b ON s.branch_id = b.branch_id
            WHERE s.branch_id = %s
            ORDER BY s.date DESC
        """, (st.session_state.branch_id,))

    st.dataframe(sales, width="stretch", hide_index=True)


# Add sale
elif page == "Add Sale":
    st.subheader("Add a New Sale")

    branches = read_data("""
        SELECT branch_id, branch_name FROM branches ORDER BY branch_name
    """)

    with st.form("sale_form"):
        branch_options = {
            row["branch_name"]: int(row["branch_id"])
            for _, row in branches.iterrows()
        }

        branch_name = st.selectbox(
            "Branch", list(branch_options.keys())
        )
        sale_date = st.date_input("Sale Date")
        customer_name = st.text_input("Customer Name")
        mobile = st.text_input("Mobile Number")
        product = st.selectbox("Product", ["DS", "DA", "BA", "FSD"])
        gross = st.number_input(
            "Gross Sales Amount (₹)", min_value=0.01, step=500.0
        )
        status = st.selectbox("Status", ["Open", "Close"])

        submitted = st.form_submit_button("Save Sale")

        if submitted:
            if not customer_name.strip() or not mobile.strip():
                st.warning("Enter the customer name and mobile number.")
            else:
                try:
                    execute_query("""
                        INSERT INTO customer_sales
                        (branch_id, date, name, mobile_number,
                         product_name, gross_sales, status)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (
                        branch_options[branch_name],
                        sale_date,
                        customer_name.strip(),
                        mobile.strip(),
                        product,
                        gross,
                        status
                    ))
                    st.success("Sale added successfully!")
                except Error as e:
                    st.error(f"Could not save sale: {e}")

# Record payment
elif page == "Record Payment":
    st.subheader("Record an Installment Payment")

    sales = read_data("""
        SELECT sale_id, name, gross_sales, received_amount, pending_amount
        FROM customer_sales
        WHERE pending_amount > 0
        ORDER BY sale_id
    """)

    if sales.empty:
        st.info("There are no sales with pending balances.")
    else:
        with st.form("payment_form"):
            options = {
                f"Sale {int(row.sale_id)} - {row['name']} "
                f"(Pending ₹{row.pending_amount:,.2f})":
                int(row.sale_id)
                for _, row in sales.iterrows()
            }

            selected_sale = st.selectbox(
                "Select Sale", list(options.keys())
            )
            payment_date = st.date_input("Payment Date")
            amount = st.number_input(
                "Amount Paid (₹)", min_value=0.01, step=500.0
            )
            method = st.selectbox(
                "Payment Method", ["Cash", "UPI", "Card"]
            )

            submitted = st.form_submit_button("Record Payment")

            if submitted:
                sale_id = options[selected_sale]
                pending = float(
                    sales.loc[
                        sales["sale_id"] == sale_id, "pending_amount"
                    ].iloc[0]
                )

                if amount > pending:
                    st.error(
                        f"Payment exceeds the pending balance of "
                        f"₹{pending:,.2f}."
                    )
                else:
                    try:
                        execute_query("""
                            INSERT INTO payment_splits
                            (sale_id, payment_date, amount_paid, payment_method)
                            VALUES (%s, %s, %s, %s)
                        """, (sale_id, payment_date, amount, method))
                        st.success(
                            "Payment recorded! The MySQL trigger "
                            "updates the received amount automatically."
                        )
                    except Error as e:
                        st.error(f"Could not record payment: {e}")

# Pending payments
elif page == "Pending Payments":
    st.subheader("Pending Collection Report")

    pending = read_data("""
        SELECT s.sale_id, s.name, b.branch_name,
               s.gross_sales, s.received_amount, s.pending_amount
        FROM customer_sales s
        JOIN branches b ON s.branch_id = b.branch_id
        WHERE s.pending_amount > 0
        ORDER BY s.pending_amount DESC
    """)

    st.dataframe(pending, width="stretch", hide_index=True)

    if not pending.empty:
        st.metric(
            "Total Pending Collection",
            f"₹{pending['pending_amount'].sum():,.2f}"
        )

# SQL reports
elif page == "SQL Reports":
    st.subheader("Analytical SQL Reports")

    reports = {
        "Branch-wise Sales": """
            SELECT b.branch_name, SUM(s.gross_sales) AS gross_sales
            FROM branches b
            JOIN customer_sales s ON b.branch_id = s.branch_id
            GROUP BY b.branch_id, b.branch_name
        """,
        "Top 3 Sales": """
            SELECT sale_id, name, gross_sales
            FROM customer_sales
            ORDER BY gross_sales DESC LIMIT 3
        """,
        "Payment Method Collections": """
            SELECT payment_method, SUM(amount_paid) AS collection
            FROM payment_splits
            GROUP BY payment_method
        """,
        "Open Sales": """
            SELECT * FROM customer_sales WHERE status = 'Open'
        """,
        "Monthly Summary": """
            SELECT YEAR(date) AS year, MONTH(date) AS month,
                   SUM(gross_sales) AS gross_sales,
                   SUM(received_amount) AS received,
                   SUM(pending_amount) AS pending
            FROM customer_sales
            GROUP BY YEAR(date), MONTH(date)
            ORDER BY year, month
        """
    }

    selected_report = st.selectbox("Choose a Report", list(reports.keys()))
    result = read_data(reports[selected_report])
    st.dataframe(result, width="stretch", hide_index=True)

st.sidebar.caption("Sales Intelligence Hub | Project Dashboard")
