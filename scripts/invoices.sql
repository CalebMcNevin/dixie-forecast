DECLARE @startDate datetime = '2014-01-01';
DECLARE @endDate datetime = '2020-11-30';

WITH SLS AS (
	SELECT account_number
		  ,proc_date
		  ,part_number
		  ,SUM(qty) Qty
		  ,SUM(exchange_total) ExchangeTotal
	FROM Sales.AllInvoicesSuper
	WHERE proc_date BETWEEN @startDate AND @endDate
	AND transaction_type != 'C'
	GROUP BY account_number, proc_date, part_number
)
SELECT SLS.account_number
	  ,SLS.proc_date
	  ,SLS.part_number
	  ,COALESCE(SLS.Qty, 0) NetQty
	  ,COALESCE(SLS.ExchangeTotal, 0) NetExchange
FROM SLS
LEFT JOIN Production.Parts P ON SLS.part_number = P.PartNumber
WHERE P.FinishedGood = 1
ORDER BY SLS.proc_date;