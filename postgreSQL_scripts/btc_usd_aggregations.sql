SELECT hour_,
avg(perc_close_open) AS close_open,
avg(perc_high_low) AS high_low
FROM btc_usd_perc_by_aggregations
GROUP BY hour_;

SELECT * FROM btc_usd_perc_by_aggregations
--WHERE date_ BETWEEN '2015-10-06 04:40' AND '2015-10-06 04:50'
ORDER BY perc_volume_btc asc