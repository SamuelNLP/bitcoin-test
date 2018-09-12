-- create table that has ratio measures from prices and volumes
CREATE TABLE btc_usd_by_hour_agg
	AS ( 
	-- define an intermediate selection to create lag columns
	WITH lags AS (
		SELECT 
			lag(weighted_price) OVER (ORDER BY date_) AS lag_weighted_price,
			date_
		FROM btc_usd
	)
	SELECT 
		-- measures
		("close" - "open") / "close" AS perc_close_open, "open", "close",
		(high - low) / high AS perc_high_low, high, low,
		(weighted_price - lag_weighted_price) / lag_weighted_price AS perc_weighted_price, weighted_price,
		volume_btc, volume_currency,
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
		-- date as reference
		date_
	FROM btc_usd_by_hour
	INNER JOIN lags USING(date_)
	WHERE date_ > '2015-03-29 02:00:00'
	ORDER BY date_ DESC
)