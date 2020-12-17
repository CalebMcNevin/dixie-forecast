SELECT CustomerCode account_number
      , ExchangeTotal
FROM Sales.Accounts A
    JOIN (SELECT account_number, SUM(exchange_total) ExchangeTotal
    FROM Sales.AllInvoicesSuper
    WHERE proc_date >= DATEADD(MONTH,-12,GETDATE())
        AND transaction_type != 'C'
    GROUP BY account_number) S ON A.CustomerCode = S.account_number
WHERE AreaCode != '99'
ORDER BY S.ExchangeTotal DESC;