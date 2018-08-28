SELECT ("close" - "open") / "close" AS per_close_open, 
(lag(weighted_price) OVER (ORDER BY date_) - weighted_price) / weighted_price AS per_weighted_price,
weighted_price,
"open",
"close",
date_
FROM btc_usd
ORDER BY date_ DESC