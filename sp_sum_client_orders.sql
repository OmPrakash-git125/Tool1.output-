CREATE PROCEDURE sp_sum_client_orders (
  @client_id INT,
  @from_date DATE,
  @to_date DATE
)
AS
BEGIN
  SELECT SUM(order_amount)
  FROM client_orders
  WHERE order_date BETWEEN @from_date AND @to_date
    AND client_id = @client_id
END
