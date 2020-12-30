DECLARE @startDate datetime = '2014-01-01';
DECLARE @endDate datetime = '2020-11-30';

WITH
    SLS
    AS
    (
        SELECT account_number
		  , proc_date
		  , part_number
		  , SUM(qty) Qty
		  , SUM(CASE A.Currency WHEN 'USD' THEN 1.3 * exchange_total ELSE exchange_total END) ExchangeTotal
        FROM Sales.AllInvoicesSuper AI
            LEFT JOIN Sales.Accounts A ON AI.account_number = A.CustomerCode
        WHERE proc_date BETWEEN @startDate AND @endDate
            AND transaction_type != 'C'
        GROUP BY account_number, proc_date, part_number
    )
SELECT SLS.account_number
	  , SLS.proc_date
	  , SLS.part_number
	  , COALESCE(SLS.Qty, 0) NetQty
	  , COALESCE(SLS.ExchangeTotal, 0) NetExchange
FROM SLS
    LEFT JOIN DIXIE_CENTRAL.Production.Parts P ON SLS.part_number = P.PartNumber
ORDER BY SLS.proc_date;