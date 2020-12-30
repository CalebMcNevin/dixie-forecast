DECLARE @startDate datetime = '2014-01-01';
DECLARE @endDate datetime = '2020-11-30';

WITH
    SLS
    AS
    (
        SELECT CASE WHEN P.FunctionalCategory IN ('Starters','Alternators') THEN P.FunctionalCategory
					WHEN P.FinishedGood=1 THEN 'Other Finished Goods'
					ELSE 'Components' END FunctionalCategory
          , CASE WHEN AI.account_number IN ('DIXMN','DIXM2','DIXC1','DIXA1','DIXP1') THEN 'Intercompany' ELSE 'Sales' END OrderType
		  , proc_date
		  , SUM(qty) NetQty
        FROM Sales.AllInvoicesSuper AI
            LEFT JOIN Production.Parts P ON AI.part_number = P.PartNumber
        WHERE proc_date BETWEEN @startDate AND @endDate
            AND transaction_type != 'C'
        GROUP BY P.FinishedGood, P.FunctionalCategory, proc_date, CASE WHEN AI.account_number IN ('DIXMN','DIXM2','DIXC1','DIXA1','DIXP1') THEN 'Intercompany' ELSE 'Sales' END
    )
SELECT SLS.FunctionalCategory
	  , SLS.OrderType
	  , SLS.proc_date
	  , COALESCE(SLS.NetQty, 0) NetQty
FROM SLS
ORDER BY SLS.proc_date;