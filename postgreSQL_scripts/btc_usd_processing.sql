-- create table that has ratio measures from prices and volumes
DROP TABLE IF EXISTS btc_usd_by_hour_agg, btc_usd_by_day_agg;

-- create by hour for a more expressive eda analysis
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
		EXTRACT(MONTH FROM date_) AS month_,
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
	ORDER BY date_ DESC
);

-- create byu day for ML analysis
CREATE TABLE btc_usd_by_day_agg
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
		std_weighted_price,
		volume_btc, volume_currency,
		-- date as reference
		date_
	FROM btc_usd_by_day
	INNER JOIN lags USING(date_)
	ORDER BY date_ DESC
);