DECLARE @startDate datetime = '2014-01-01';
DECLARE @endDate datetime = '2020-11-30';

WITH
    SLS
    AS
    (
        SELECT CASE WHEN P.FinishedGood=1 THEN P.FunctionalCategory ELSE 'Components' END FunctionalCategory
		  , proc_date
		  , part_number
		  , SUM(qty) NetQty
        FROM Sales.AllInvoicesSuper AI
            LEFT JOIN DIXIE_CENTRAL.Production.Parts P ON AI.part_number = P.PartNumber
        WHERE proc_date BETWEEN @startDate AND @endDate
            AND transaction_type != 'C'
        GROUP BY P.FinishedGood, P.FunctionalCategory, proc_date, part_number
    )
SELECT SLS.FunctionalCategory
	  , SLS.proc_date
	  , SLS.part_number
	  , COALESCE(SLS.NetQty, 0) NetQty
FROM SLS
    LEFT JOIN DIXIE_CENTRAL.Production.Parts P ON SLS.part_number = P.PartNumber
ORDER BY SLS.proc_date;