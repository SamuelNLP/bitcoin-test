-- create table that has ratio measures from prices and volumes
CREATE TABLE btc_usd_perc_by_aggregations 
	AS ( 
	-- define an intermediate selection to create lag columns
	WITH lags AS (
		SELECT 
			lag(weighted_price) OVER (ORDER BY date_) AS lag_weighted_price,
			lag(volume_currency) OVER (ORDER BY date_) AS lag_volume_currency,
			lag(volume_btc) OVER (ORDER BY date_) AS lag_volume_btc,
			date_
		FROM btc_usd
	)
	SELECT 
		-- measures
		("close" - "open") / "close" AS perc_close_open,
		(high - low) / high AS perc_high_low,
		(weighted_price - lag_weighted_price) / lag_weighted_price AS perc_weighted_price,
		(volume_currency - lag_volume_currency) / lag_volume_currency AS perc_volume_currency,
		(volume_btc - lag_volume_btc) / lag_volume_btc AS perc_volume_btc,
		-- possible aggregations
		EXTRACT(dow FROM date_) AS weekday,
		EXTRACT(DAY FROM date_) AS day_of_month,
		EXTRACT(HOUR FROM date_) AS hour_,
		CASE WHEN EXTRACT(dow FROM date_) IN (0, 6) THEN 1
			ELSE 0
		END AS weekend,
		CASE WHEN EXTRACT(HOUR FROM date_) < 12 THEN 'am'
			ELSE 'pm'
		END AS am_vs_pm,
		EXTRACT(YEAR FROM date_) AS year_,
		EXTRACT(MINUTE FROM date_) AS minute_,
		-- date as reference
		date_
	FROM btc_usd
	INNER JOIN lags USING(date_)
	ORDER BY date_ DESC
)