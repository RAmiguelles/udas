# DATE: 12/22/2021
# RUN THIS QUERY IN MYSQL DATABASE

TRUNCATE TABLE time_zone;
TRUNCATE TABLE time_zone_name;
TRUNCATE TABLE time_zone_transition;
TRUNCATE TABLE time_zone_transition_type;

INSERT INTO time_zone (Use_leap_seconds) VALUES ('N');
SET @time_zone_id= LAST_INSERT_ID();
INSERT INTO time_zone_name (NAME, Time_zone_id) VALUES ('Asia/Manila', @time_zone_id);
INSERT INTO time_zone_transition (Time_zone_id, Transition_time, Transition_type_id) VALUES
(@time_zone_id, -2147483648, 2)
,(@time_zone_id, -1046678400, 1)
,(@time_zone_id, -1038733200, 2)
,(@time_zone_id, -873273600, 3)
,(@time_zone_id, -794221200, 2)
,(@time_zone_id, -496224000, 1)
,(@time_zone_id, -489315600, 2)
,(@time_zone_id, 259344000, 1)
,(@time_zone_id, 275151600, 2)
;
INSERT INTO time_zone_transition_type (Time_zone_id, Transition_type_id, OFFSET, Is_DST, Abbreviation) VALUES
(@time_zone_id, 0, -57360, 0, 'LMT')
,(@time_zone_id, 1, 32400, 1, 'PDT')
,(@time_zone_id, 2, 28800, 0, 'PST')
,(@time_zone_id, 3, 32400, 0, 'JST')
,(@time_zone_id, 4, 28800, 0, 'PST')
;

INSERT INTO time_zone (Use_leap_seconds) VALUES ('N');
SET @time_zone_id= LAST_INSERT_ID();
INSERT INTO time_zone_name (NAME, Time_zone_id) VALUES ('UTC', @time_zone_id);
INSERT INTO time_zone_transition_type (Time_zone_id, Transition_type_id, OFFSET, Is_DST, Abbreviation) VALUES
    (@time_zone_id, 0, 0, 0, 'UTC')
;
INSERT INTO time_zone (Use_leap_seconds) VALUES ('N');
SET @time_zone_id= LAST_INSERT_ID();
INSERT INTO time_zone_name (NAME, Time_zone_id) VALUES ('Universal', @time_zone_id);
INSERT INTO time_zone_transition_type (Time_zone_id, Transition_type_id, OFFSET, Is_DST, Abbreviation) VALUES
    (@time_zone_id, 0, 0, 0, 'UTC')
;

ALTER TABLE time_zone_transition ORDER BY Time_zone_id, Transition_time;
ALTER TABLE time_zone_transition_type ORDER BY Time_zone_id, Transition_type_id;