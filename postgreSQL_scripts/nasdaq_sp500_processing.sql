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
		-- date as reference
		date_
	FROM nasdaq_clean_regression
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
		-- date as reference
		date_
	FROM sp500_clean_regression
	ORDER BY date_ DESC
);