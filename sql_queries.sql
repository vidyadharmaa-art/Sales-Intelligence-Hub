
USE sales_intelligence_hub;

-- 1. Display all customer sales
SELECT * FROM customer_sales;

-- 2. Display all branches
SELECT * FROM branches;

-- 3. Display all payment records
SELECT * FROM payment_splits;

-- 4. Find all open sales
SELECT * FROM customer_sales
WHERE status = 'Open';

-- 5. Calculate total gross sales
SELECT SUM(gross_sales) AS total_gross_sales
FROM customer_sales;

-- 6. Calculate total amount received
SELECT SUM(received_amount) AS total_received
FROM customer_sales;

-- 7. Calculate total pending amount
SELECT SUM(pending_amount) AS total_pending
FROM customer_sales;

-- 8. Count sales per branch
SELECT b.branch_name, COUNT(cs.sale_id) AS total_sales
FROM branches b
LEFT JOIN customer_sales cs ON b.branch_id = cs.branch_id
GROUP BY b.branch_id, b.branch_name;

-- 9. Show sales details with branch names
SELECT cs.*, b.branch_name
FROM customer_sales cs
JOIN branches b ON cs.branch_id = b.branch_id;

-- 10. Show total payments received for each sale
SELECT cs.sale_id, cs.name, cs.gross_sales,
       COALESCE(SUM(ps.amount_paid), 0) AS total_paid
FROM customer_sales cs
LEFT JOIN payment_splits ps ON cs.sale_id = ps.sale_id
GROUP BY cs.sale_id, cs.name, cs.gross_sales;

-- 11. Calculate branch-wise gross sales
SELECT b.branch_name, SUM(cs.gross_sales) AS branch_gross_sales
FROM branches b
LEFT JOIN customer_sales cs ON b.branch_id = cs.branch_id
GROUP BY b.branch_id, b.branch_name;

-- 12. Show sales with their payment methods
SELECT cs.sale_id, cs.name, ps.payment_method, ps.amount_paid
FROM customer_sales cs
JOIN payment_splits ps ON cs.sale_id = ps.sale_id;

-- 13. Show sales with branch administrator names
SELECT cs.sale_id, cs.name, b.branch_name, b.branch_admin_name
FROM customer_sales cs
JOIN branches b ON cs.branch_id = b.branch_id;

-- 14. Find sales with pending payments above 5000
SELECT sale_id, name, gross_sales, received_amount, pending_amount
FROM customer_sales
WHERE pending_amount > 5000
ORDER BY pending_amount DESC;

-- 15. Show monthly sales summary
SELECT YEAR(date) AS sales_year,
       MONTH(date) AS sales_month,
       COUNT(*) AS number_of_sales,
       SUM(gross_sales) AS monthly_gross_sales,
       SUM(received_amount) AS monthly_received,
       SUM(pending_amount) AS monthly_pending
FROM customer_sales
GROUP BY YEAR(date), MONTH(date)
ORDER BY sales_year, sales_month;
