# delimiter //
# drop trigger if exists goods_shipments_insert //
# CREATE TRIGGER goods_shipments_insert AFTER INSERT  # changes goods.state to '1' (sold)
# ON goods_shipments FOR EACH ROW BEGIN
#     UPDATE warehouse.goods
#         Set goods.state = 1
#     where goods.id = goods_shipments.goods_id;
# END //
#
# delimiter ;



# create view true_schedule(id, station_from, station_to, departure_time, arrival_time, type, model) as
#     select s.id, st1.station as station_from, st2.station as station_to, s.depature_time, s.arrival_time, types.type, tr.model from train_schedule.schedule s
#         left join train_schedule.stations st1 on (st1.id = s.from_id)
#         left join train_schedule.stations st2 on (st2.id = s.to_id)
#         left join train_schedule.types types on (types.id = s.type_id)
#         left join train_schedule.trains tr on (tr.id = s.train_id)
#         order by s.depature_time;


# select * from goods_view;


select NOT exists(select * from goods where goods.id=2);
DELETE FROM catalog WHERE catalog.id = 4;