CREATE TABLE everythingdatabalanced_tmp(
    id serial PRIMARY KEY,
    reviewerid varchar(255),
    asin varchar(255),
    reviewername varchar(255),
    helpful varchar(255),
    reviewtext varchar(50000),
    overall numeric,
    summary varchar(5000),
    reviewtime date,
    category varchar(255),
    class numeric
);

INSERT INTO everythingdatabalanced_tmp (id, reviewerid, asin, reviewername, helpful, reviewtext, overall, summary, reviewtime, category, class)
SELECT * FROM everythingdatabalanced ORDER BY RANDOM();


DROP TABLE TABLE everythingdatabalanced;

ALTER TABLE everythingdatabalanced_tmp RENAME TO everythingdatabalanced;

-- Get size of a table

SELECT pg_total_relation_size('everythingdata')/1024/1024 AS size_mb;






CREATE TABLE Everythingdata(
    id serial PRIMARY KEY,
    asin VARCHAR(255),
    reviewerName VARCHAR(255),
    helpful VARCHAR(255),
    reviewText VARCHAR(50000),
    overall numeric,
    summary VARCHAR(5000),
    reviewTime date,
    category varchar(255),
    class numeric
);

CREATE TABLE EverythingdataSpam(
    id serial PRIMARY KEY,
    everythingid serial,
    asin VARCHAR(255),
    reviewerName VARCHAR(255),
    helpful VARCHAR(255),
    reviewText VARCHAR(50000),
    overall numeric,
    summary VARCHAR(5000),
    reviewTime date,
    category varchar(255),
    class numeric
);
CREATE TABLE EverythingdataHam(
    id serial PRIMARY KEY,
    everythingid serial,
    asin VARCHAR(255),
    reviewerName VARCHAR(255),
    helpful VARCHAR(255),
    reviewText VARCHAR(50000),
    overall numeric,
    summary VARCHAR(5000),
    reviewTime date,
    category varchar(255),
    class numeric
);

INSERT INTO everythingdata(asin, reviewername, helpful, reviewtext, overall, summary, reviewtime, category, class)
SELECT asin, reviewername, helpful, reviewtext, overall, summary, reviewtime, category, class from cellphonesandaccessoriesdata;

INSERT INTO everythingdata(asin, reviewername, helpful, reviewtext, overall, summary, reviewtime, category, class)
SELECT asin, reviewername, helpful, reviewtext, overall, summary, reviewtime, category, class from electronicsdata;

INSERT INTO everythingdata(asin, reviewername, helpful, reviewtext, overall, summary, reviewtime, category, class)
SELECT asin, reviewername, helpful, reviewtext, overall, summary, reviewtime, category, class from homeandkitchendata;

INSERT INTO everythingdata(asin, reviewername, helpful, reviewtext, overall, summary, reviewtime, category, class)
SELECT asin, reviewername, helpful, reviewtext, overall, summary, reviewtime, category, class from clothingshoesandjewelrydata;

INSERT INTO everythingdata(asin, reviewername, helpful, reviewtext, overall, summary, reviewtime, category, class)
SELECT asin, reviewername, helpful, reviewtext, overall, summary, reviewtime, category, class from homeandkitchendata;

INSERT INTO everythingdata(asin, reviewername, helpful, reviewtext, overall, summary, reviewtime, category, class)
SELECT asin, reviewername, helpful, reviewtext, overall, summary, reviewtime, category, class from sportsandoutdoorsdata;

INSERT INTO everythingdata(asin, reviewername, helpful, reviewtext, overall, summary, reviewtime, category, class)
SELECT asin, reviewername, helpful, reviewtext, overall, summary, reviewtime, category, class from toysandgamesdata;


INSERT INTO EverythingdataSpam(everythingid, asin, reviewername, helpful, reviewtext, overall, summary, reviewtime, category, class)
SELECT * FROM EverythingData
WHERE class = 1
ORDER BY everythingdata.id
LIMIT 5000000;


INSERT INTO EverythingdataHam(everythingid, asin, reviewername, helpful, reviewtext, overall, summary, reviewtime, category, class)
SELECT * FROM EverythingData
WHERE class = 0
ORDER BY everythingdata.id
LIMIT 5000000;

-- Create Table for verification after training

CREATE TABLE VerificationData(
    id serial PRIMARY KEY,
    everythingid serial,
    asin VARCHAR(255),
    reviewerName VARCHAR(255),
    helpful VARCHAR(255),
    reviewText VARCHAR(50000),
    overall numeric,
    summary VARCHAR(5000),
    reviewTime date,
    category varchar(255),
    class numeric
);

INSERT INTO VerificationData(everythingid, asin, reviewername, helpful, reviewtext, overall, summary, reviewtime, category, class)
SELECT * FROM EverythingData
WHERE class = 1
ORDER BY everythingdata.id
OFFSET 5000000;

INSERT INTO VerificationData(everythingid, asin, reviewername, helpful, reviewtext, overall, summary, reviewtime, category, class)
SELECT * FROM EverythingData
WHERE class = 0
ORDER BY everythingdata.id
OFFSET 5000000;


CREATE TABLE VerificationDataResults(
    id serial PRIMARY KEY,
    verificationid integer,
    bnb_class decimal,
    sgd_class decimal,
    nb_class decimal,
    lr_class decimal,
    ann_class decimal,
    class numeric
);


-- Create the training tables

DROP TABLE training_nlp;



-- Balanced Tables

CREATE TABLE everythingdatabalanced(
    id serial PRIMARY KEY,
    reviewerid varchar(255),
    asin varchar(255),
    reviewername varchar(255),
    helpful varchar(255),
    reviewtext varchar(50000),
    overall numeric,
    summary varchar(5000),
    reviewtime date,
    category varchar(255),
    class numeric
);

INSERT INTO everythingdatabalanced (reviewerid, asin, reviewername, helpful, reviewtext, overall, summary, reviewtime, category, class)
SELECT * FROM everythingdata
WHERE class = 0
LIMIT 5000000;

INSERT INTO everythingdatabalanced (reviewerid, asin, reviewername, helpful, reviewtext, overall, summary, reviewtime, category, class)
SELECT * FROM everythingdata
WHERE class = 1
LIMIT 5000000;


CREATE TABLE everythingdatabalanced_tmp(
    id serial PRIMARY KEY,
    reviewerid varchar(255),
    asin varchar(255),
    reviewername varchar(255),
    helpful varchar(255),
    reviewtext varchar(50000),
    overall numeric,
    summary varchar(5000),
    reviewtime date,
    category varchar(255),
    class numeric
);

INSERT INTO everythingdatabalanced_tmp (id, reviewerid, asin, reviewername, helpful, reviewtext, overall, summary, reviewtime, category, class)
SELECT * FROM everythingdatabalanced ORDER BY RANDOM();


DROP TABLE TABLE everythingdatabalanced;

ALTER TABLE everythingdatabalanced_tmp RENAME TO everythingdatabalanced;



-- This is for merging the NLP Results into trainingdatab

UPDATE trainingdatabig
SET bnb_class = training_nlp.bnb_class, nb_class = training_nlp.nb_class,
sgd_class = training_nlp.sgd_class, lr_class = training_nlp.lr_class
FROM training_nlp
WHERE trainingdatabig.everything_id = training_nlp.everything_id AND
trainingdatabig.overall = training_nlp.overall AND
trainingdatabig.class = training_nlp.class;


CREATE TABLE TrainingDataBig(
    id serial PRIMARY KEY,
    everythingid integer,
    review_text_length integer,
    helpful integer,
    not_helpful integer,
    bnb_class decimal,
    sgd_class decimal,
    nb_class decimal,
    lr_class decimal,
    class numeric
);
