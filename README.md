# Sales Intelligence Hub

## 1. Project Overview
Sales Intelligence Hub is a sales analytics and financial tracking system that helps monitor customer sales, installment payments, pending balances, and branch performance.

## 2. Technologies Used
- Python
- Streamlit
- MySQL
- SQL
- Pandas
- MySQL Connector for Python

## 3. Features
- User login with role-based access
- Add and view sales records
- Record installment payments
- Track received and pending amounts
- View pending collection reports
- Analyse branch-wise sales
- View monthly sales trends
- Generate analytical SQL reports

## 4. Database Structure
- **branches:** Stores branch details.
- **customer_sales:** Stores customer and sales information.
- **users:** Stores login accounts, roles, and branch assignments.
- **payment_splits:** Stores installment payment details.

## 5. Financial Tracking
The system records installment payments and uses a MySQL trigger to update the received amount. The pending amount is calculated from gross sales minus the received amount.

## 6. How to Run
1. Start MySQL Server.
2. Open this folder in Visual Studio Code.
3. Install dependencies by running `python -m pip install -r requirements.txt`.
4. Start the dashboard using `python -m streamlit run app.py`.
5. Open the local URL displayed in the terminal.

## 7. Project Files
- `app.py` — Streamlit application.
- `sql_queries.sql` — SQL queries and analysis.
- `requirements.txt` — Python dependencies.
- `README.md` — Project documentation.

## 8. Testing
The dashboard, sales records, installment payments, pending balances, branch-wise sales, and analytical reports were tested using sample data.
