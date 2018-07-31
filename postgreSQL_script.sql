-- create a timestamp column date_ from the epoch data
/* SELECT to_timestamp(timestamp_value) AS date_, *
FROM btc_usd;

 ALTER TABLE btc_usd ADD COLUMN date_ TIMESTAMP;*/

 UPDATE btc_usd
SET date_ = to_timestamp(timestamp_value);

-- CREATE INDEX btc_usd_date__idx ON
--public.btc_usd (date_) ;

-- test query by day
SELECT * FROM btc_usd;-- WHERE date_::date = '2018-01-02';
