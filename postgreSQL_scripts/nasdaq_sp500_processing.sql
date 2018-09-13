-- create table that has ratio measures from prices and volumes
DROP TABLE IF EXISTS nasdaq_agg, sp500_agg;

CREATE TABLE nasdaq_agg
	AS ( 
	-- define an intermediate selection to create lag columns
	SELECT 
		-- measures
		"open",
		(high - low) / high AS perc_high_low, high, low,
		perc_price, price,
		volume_currency,
		-- possible aggregations
		EXTRACT(dow FROM date_) AS weekday,
		EXTRACT(DAY FROM date_) AS day_of_month,
		EXTRACT(MONTH FROM date_) AS month_,
		CASE WHEN EXTRACT(dow FROM date_) IN (0, 6) THEN 1
			ELSE 0
		END AS weekend,
		EXTRACT(YEAR FROM date_) AS year_,
		-- date as reference
		date_
	FROM nasdaq_clean_interpolate
	ORDER BY date_ DESC
);

CREATE TABLE sp500_agg
	AS ( 
	-- define an intermediate selection to create lag columns
	SELECT 
		-- measures
		"open",
		(high - low) / high AS perc_high_low, high, low,
		perc_price, price,
		-- possible aggregations
		EXTRACT(dow FROM date_) AS weekday,
		EXTRACT(DAY FROM date_) AS day_of_month,
		EXTRACT(MONTH FROM date_) AS month_,
		CASE WHEN EXTRACT(dow FROM date_) IN (0, 6) THEN 1
			ELSE 0
		END AS weekend,
		EXTRACT(YEAR FROM date_) AS year_,
		-- date as reference
		date_
	FROM sp500_clean_interpolate
	ORDER BY date_ DESC
);