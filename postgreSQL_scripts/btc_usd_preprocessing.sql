-- create a timestamp column date_ from the epoch data
SELECT to_timestamp( timestamp_value ) AS date_, *
FROM btc_usd;

ALTER TABLE btc_usd DROP IF EXISTS date_;

ALTER TABLE btc_usd ADD COLUMN date_ TIMESTAMP;

UPDATE btc_usd
SET date_ = to_timestamp( timestamp_value );

-- create an index in date column
CREATE INDEX btc_usd_date__idx ON
public.btc_usd ( date_ );

----------------------- resample data by hour ------------------------
DROP TABLE IF EXISTS btc_usd_by_hour CASCADE;

CREATE TABLE btc_usd_by_hour
  AS (
	SELECT t1.*, t2."open", t3."close"
	FROM ( SELECT date_trunc( 'hour', date_ ) AS date_, 
		MAX( high ) AS high, MIN( low ) AS low, 
		SUM( volume_btc ) AS volume_btc, SUM( volume_currency ) AS volume_currency, 
		AVG( weighted_price ) AS weighted_price
		FROM btc_usd
		GROUP BY 1 ) AS t1
	JOIN ( SELECT DISTINCT ON
		( date_trunc( 'hour', date_ )) "open", date_trunc( 'hour', date_ )
		FROM btc_usd
		ORDER BY date_trunc( 'hour', date_ ), date_ ) AS t2 
	ON t1.date_ = t2.date_trunc
	JOIN (SELECT DISTINCT ON
		( date_trunc( 'hour', date_ )) "close", date_trunc( 'hour', date_ )
		FROM btc_usd
		ORDER BY date_trunc( 'hour', date_ ) DESC, date_ DESC) AS t3
	ON t1.date_ = t3.date_trunc
	);

-- create an index in date column
CREATE INDEX btc_usd_by_hour_date__idx ON
public.btc_usd_by_hour ( date_ );

-- check where the data is incomplete
DROP VIEW IF EXISTS btc_usd_by_hour_date_dif;

CREATE VIEW btc_usd_by_hour_date_dif AS (
	SELECT DATE_PART('day', date_ - lag(date_) OVER (ORDER BY date_)) *  24 + DATE_PART('hour', date_ - lag(date_) OVER (ORDER BY date_)) AS date_dif, 
	date_ 
	FROM btc_usd_by_hour);

SELECT * FROM btc_usd_by_hour_date_dif
WHERE date_dif > 1;

----------------------- resample data by day ------------------------
DROP TABLE IF EXISTS btc_usd_by_day CASCADE;

CREATE TABLE btc_usd_by_day
  AS (
	SELECT t1.*, t2."open", t3."close"
	FROM ( SELECT date_trunc( 'day', date_ ) AS date_, 
		MAX( high ) AS high, MIN( low ) AS low, 
		SUM( volume_btc ) AS volume_btc, SUM( volume_currency ) AS volume_currency, 
		AVG( weighted_price ) AS weighted_price,
		STDDEV_POP( weighted_price) AS std_weighted_price
		FROM btc_usd
		GROUP BY 1 ) AS t1
	JOIN ( SELECT DISTINCT ON
		( date_trunc( 'day', date_ )) "open", date_trunc( 'day', date_ )
		FROM btc_usd
		ORDER BY date_trunc( 'day', date_ ), date_ ) AS t2 
	ON t1.date_ = t2.date_trunc
	JOIN (SELECT DISTINCT ON
		( date_trunc( 'day', date_ )) "close", date_trunc( 'day', date_ )
		FROM btc_usd
		ORDER BY date_trunc( 'day', date_ ) DESC, date_ DESC) AS t3
	ON t1.date_ = t3.date_trunc
	);

-- create an index in date column
CREATE INDEX btc_usd_by_day_date__idx ON
public.btc_usd_by_day ( date_ );

-- check where the data is incomplete
DROP VIEW IF EXISTS btc_usd_by_day_date_dif;

CREATE VIEW btc_usd_by_day_date_dif AS (
	SELECT DATE_PART('day', date_ - lag(date_) OVER (ORDER BY date_)) AS date_dif, 
	date_ 
	FROM btc_usd_by_day);

SELECT * FROM btc_usd_by_day_date_dif
WHERE date_dif > 1;