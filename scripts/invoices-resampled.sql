DECLARE @startDate datetime = DATEADD(MONTH,-24,GETDATE());

WITH ACNT AS (
	SELECT DISTINCT account_number
	FROM Sales.AllInvoicesSuper
	WHERE proc_date >= @startDate
	AND transaction_type != 'C'
), PRT AS (
	SELECT DISTINCT part_number
	FROM Sales.AllInvoicesSuper
	WHERE proc_date >= @startDate
	AND transaction_type != 'C'
), CRS AS (
	SELECT DD.Date
		  ,ACNT.account_number
		  ,PRT.part_number
	FROM dbo.DateDimension DD
	CROSS JOIN ACNT
	CROSS JOIN PRT
	WHERE DD.Date BETWEEN @startDate AND GETDATE()
), SLS AS (
	SELECT account_number
		  ,proc_date
		  ,part_number
		  ,SUM(qty) Qty
		  ,SUM(exchange_total) ExchangeTotal
	FROM Sales.AllInvoicesSuper
	WHERE proc_date >= @startDate
	AND transaction_type != 'C'
	GROUP BY account_number, proc_date, part_number
)
SELECT TOP 100 CRS.account_number
	  ,CRS.Date
	  ,CRS.part_number
	  ,COALESCE(SLS.Qty, 0) NetQty
	  ,COALESCE(SLS.ExchangeTotal, 0) NetExchange
FROM CRS
LEFT JOIN SLS ON CRS.Date = SLS.proc_date
				 AND CRS.account_number = SLS.account_number
				 AND CRS.part_number = SLS.part_number; 