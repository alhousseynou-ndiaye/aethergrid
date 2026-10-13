create table buildings (
   building_id         text primary key,
   site_id             text not null,
   primary_space_usage text,
   sqm                 numeric(12,2),
   timezone            text,
   constraint positive_area check ( sqm > 0 )
);

create table electricity_readings (
   building_id     text not null,
   timestamp_local timestamp not null,
   consumption_kwh numeric(15,5) not null,
   constraint electricity_readings_pk primary key ( building_id,
                                                    timestamp_local ),
   constraint electricity_building_fk foreign key ( building_id )
      references buildings ( building_id ),
   constraint non_negative_consumption check ( consumption_kwh >= 0 )
);