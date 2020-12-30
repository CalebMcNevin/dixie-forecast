SELECT CustomerCode account_number
      , TwelveMonthSales
FROM Sales.Accounts A
    JOIN (SELECT account_number, SUM(CASE AC.Currency WHEN 'USD' THEN 1.3 ELSE 1.0 END * exchange_total) TwelveMonthSales
    FROM Sales.AllInvoicesSuper S
        JOIN Sales.Accounts AC ON S.account_number = AC.CustomerCode
    WHERE proc_date >= DATEADD(MONTH,-12,GETDATE())
        AND transaction_type != 'C'
    GROUP BY account_number) S ON A.CustomerCode = S.account_number
WHERE AreaCode != '99';