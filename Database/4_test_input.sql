# # # СДЕЛАТЬ ПРОВЕРКУ ЧТОБЫ НЕ ПЕРЕДАВАЛИСЬ ПУСТЫЕ СТРОКИ В ПОЛЯ где тип данных varchar(), например: name, address, phone, email и т.д.

insert into suppliers(name, address, phone, email, note) values("Lipton",   "Great Britain","0 (000)-000-00-00", "Lipton@gmail.com",    "");
insert into suppliers(name, address, phone, email, note) values("Завод А",  "Тула",         "0 (000)-000-00-01", "Zavod_A@yandex.ru",   "Это привет");
insert into suppliers(name, address, phone, email, note) values("Завод Б",  "Липецк",       "0 (000)-000-00-02", "Zavod_B@yandex.ru",   "Это я вивет");
insert into suppliers(name, address, phone, email, note) values("Завод В",  "Москва",       "0 (000)-000-00-03", "Zavod_V@mail.ru",     "Это я всем привет");
insert into suppliers(name, address, phone, email, note) values("Crafter",  "South Korea",  "0 (000)-000-00-04", "Crafter@gmail.com",   "Это я вивет");
insert into suppliers(name, address, phone, email, note) values("Apple",    "California",   "0 (000)-000-00-05", "Appple@gmail.com",    "");
# строка в provider может быть равна строке в customers, мешать этому не будем (но в БД будем их воспринимать за разных людей)

insert into supplies(suppliers_id, delivery_note, date, note) values(1, "0000000001", '2020-09-20', "это Lipton");
insert into supplies(suppliers_id, delivery_note, date, note) values(2, "0000000002", '2020-09-21', "это Завод А");
insert into supplies(suppliers_id, delivery_note, date, note) values(3, "0000000003", '2020-09-22', "это Завод Б");
insert into supplies(suppliers_id, delivery_note, date, note) values(4, "0000000004", '2020-09-25', "это Завод В");
insert into supplies(suppliers_id, delivery_note, date, note) values(5, "0000000005", '2020-09-24', "это Crafter");
insert into supplies(suppliers_id, delivery_note, date, note) values(6, "0000000006", '2020-09-25', "это Apple");
insert into supplies(suppliers_id, delivery_note, date, note) values(1, "0000000007", '2020-09-20', "Прибыла с задержкой");

insert into catalog(product_name, price, shelf_life, description) values("Чай Lipton Стандартный",  149.99,     365,    "чяй");
insert into catalog(product_name, price, shelf_life, description) values("Чай Lipton Фруктовый",    149.99,     364,    "чаааай");
insert into catalog(product_name, price, shelf_life, description) values("Деталь А",                150,        NULL,   "Деталь автомобиля");
insert into catalog(product_name, price, shelf_life, description) values("Деталь Б",                3500.58,    NULL,   "Деталь бензопилы");
insert into catalog(product_name, price, shelf_life, description) values("Деталь В",                2000,       NULL,   "Деталь велосипеда");
insert into catalog(product_name, price, shelf_life, description) values("Crafter DE-7/N",          42000,      NULL,   "Гитара фирмы Crafter");
insert into catalog(product_name, price, shelf_life, description) values("iPhone X",                100000,     NULL,   "Дорогой телефон");
insert into catalog(product_name, price, shelf_life, description) values("iPad 2",                  20000,      NULL,   "Дорогой Планшет");
insert into catalog(product_name, price, shelf_life, description) values("iPad 3",                  30000,      NULL,   "Дорогой Планшет");
insert into catalog(product_name, price, shelf_life, description) values("10",                      10,         10,     "10");

# shelf_life может принимать значение NULL - это означает, что срок годности товара не ограничен
# product_name не уникальный потому что цена товара может зависеть от времени, поэтому создаётся этот же товар с таким же именем, но с другой ценой
    # когда-нибудь из-за этого потребуется создать таблицу product_names к которой будет подключаться каталог, чтобы не дублировать имена


insert into goods(id, catalog_id, state_id, production_date, note) values(1, 1, 1, '2001-01-01', "Чай");
insert into goods(id, catalog_id, state_id, production_date, note) values(2, 1, 1, '2001-01-02', "");
insert into goods(id, catalog_id, state_id, production_date, note) values(3, 1, 1, '2001-01-03', "");
insert into goods(id, catalog_id, state_id, production_date, note) values(4, 2, 1, '2020-12-22', "");
insert into goods(id, catalog_id, state_id, production_date, note) values(5, 2, 1, '2001-01-05', "");
insert into goods(id, catalog_id, state_id, production_date, note) values(6, 2, 1, '2001-01-05', "Была вскрыта упаковка");
insert into goods(id, catalog_id, state_id, production_date, note) values(7, 3, 1, '2001-01-06', "");
insert into goods(id, catalog_id, state_id, production_date, note) values(8, 3, 1, '2001-01-07', "");
insert into goods(id, catalog_id, state_id, production_date, note) values(9, 3, 1, '2001-01-08', "");
insert into goods(id, catalog_id, state_id, production_date, note) values(10, 4, 1, '2001-01-09', "");
insert into goods(id, catalog_id, state_id, production_date, note) values(11, 4, 1, '2020-12-22', "");
insert into goods(id, catalog_id, state_id, production_date, note) values(12, 4, 1, '2001-01-10', "");
insert into goods(id, catalog_id, state_id, production_date, note) values(13, 5, 1, '2001-01-01', "");
insert into goods(id, catalog_id, state_id, production_date, note) values(14, 5, 1, '2001-01-02', "");
insert into goods(id, catalog_id, state_id, production_date, note) values(15, 5, 1, '2001-01-03', "");
insert into goods(id, catalog_id, state_id, production_date, note) values(16, 6, 1, '2001-01-05', "");
insert into goods(id, catalog_id, state_id, production_date, note) values(17, 6, 1, '2001-01-05', "");
insert into goods(id, catalog_id, state_id, production_date, note) values(18, 6, 1, '2001-01-06', "");
insert into goods(id, catalog_id, state_id, production_date, note) values(19, 7, 1, '2001-01-07', "");
insert into goods(id, catalog_id, state_id, production_date, note) values(20, 7, 1, '2001-01-08', "");
insert into goods(id, catalog_id, state_id, production_date, note) values(21, 7, 1, '2001-01-09', "");
insert into goods(id, catalog_id, state_id, production_date, note) values(22, 8, 1, '2020-12-22', "");
insert into goods(id, catalog_id, state_id, production_date, note) values(23, 8, 1, '2001-01-10', "");
insert into goods(id, catalog_id, state_id, production_date, note) values(24, 8, 1, '2001-01-07', "Уценка (поцарапан)");
insert into goods(id, catalog_id, state_id, production_date, note) values(25, 9, 1, '2001-01-08', "");
insert into goods(id, catalog_id, state_id, production_date, note) values(26, 9, 1, '2001-01-09', "");
insert into goods(id, catalog_id, state_id, production_date, note) values(27, 9, 1, '2020-12-22', "");
insert into goods(id, catalog_id, state_id, production_date, note) values(28, 9, 1, '2001-01-10', "Уценка (поцарапан)");

insert into goods_supplies(supplies_id, goods_id) values(7, 1);
insert into goods_supplies(supplies_id, goods_id) values(7, 2);
insert into goods_supplies(supplies_id, goods_id) values(7, 3);
insert into goods_supplies(supplies_id, goods_id) values(1, 4);
insert into goods_supplies(supplies_id, goods_id) values(1, 5);
insert into goods_supplies(supplies_id, goods_id) values(1, 6);
insert into goods_supplies(supplies_id, goods_id) values(2, 7);
insert into goods_supplies(supplies_id, goods_id) values(2, 8);
insert into goods_supplies(supplies_id, goods_id) values(2, 9);
insert into goods_supplies(supplies_id, goods_id) values(3, 10);
insert into goods_supplies(supplies_id, goods_id) values(3, 11);
insert into goods_supplies(supplies_id, goods_id) values(3, 12);
insert into goods_supplies(supplies_id, goods_id) values(4, 13);
insert into goods_supplies(supplies_id, goods_id) values(4, 14);
insert into goods_supplies(supplies_id, goods_id) values(4, 15);
insert into goods_supplies(supplies_id, goods_id) values(5, 16);
insert into goods_supplies(supplies_id, goods_id) values(5, 17);
insert into goods_supplies(supplies_id, goods_id) values(5, 18);
insert into goods_supplies(supplies_id, goods_id) values(6, 19);
insert into goods_supplies(supplies_id, goods_id) values(6, 20);
insert into goods_supplies(supplies_id, goods_id) values(6, 21);
insert into goods_supplies(supplies_id, goods_id) values(6, 22);
insert into goods_supplies(supplies_id, goods_id) values(6, 23);
insert into goods_supplies(supplies_id, goods_id) values(6, 24);
insert into goods_supplies(supplies_id, goods_id) values(6, 25);
insert into goods_supplies(supplies_id, goods_id) values(6, 26);
insert into goods_supplies(supplies_id, goods_id) values(6, 27);
insert into goods_supplies(supplies_id, goods_id) values(6, 28);

insert into storage(goods_id, shelf) values(11, "AA11AA11");
insert into storage(goods_id, shelf) values(10, "AA11AA11");
insert into storage(goods_id, shelf) values(9, "AA11AA11");
insert into storage(goods_id, shelf) values(8, "AA11AA12");
insert into storage(goods_id, shelf) values(7, "AA11AA12");
insert into storage(goods_id, shelf) values(6, "AA11AA12");
# несколько товаров может лежать на одной полке (ограничение по количеству не нужно)
# товары для которых ещё не определили полку хранения не добаляются (можно было бы добавлять со значением shelf = NULL, но это лишнее)

insert into customers(name, address, phone, email, note) values("Савеля", "скрыт", "8", "*@gmail.ru", "");
insert into customers(name, address, phone, email, note) values("Кирилл", "м. Молодёжная", "8(916)-???-??-?5", "fg@yandex.ru", "Это привет");
insert into customers(name, address, phone, email, note) values("ЛДВ", "м. Южная", "8(916)-???-??-??", "*@mail.ru", "ы");
insert into customers(name, address, phone, email, note) values("Частная фирма С.А", "м. Тульская", "8(916)-???-??-7?", "ggg@yandex.ru", "Это я вивет");
insert into customers(name, address, phone, email, note) values("Яндекс", "м. Арбатская", "8(916)-???-??-12", "fkjg@yandex.ru", "Яндыкс, круть");
insert into customers(name, address, phone, email, note) values("Перекрёсток", "84", "+??????????", "Perekrestok@gmail.com", "");
insert into customers(name, address, phone, email, note) values("Кирилл З.", "м. Южная", "8(916)-???-?5-?1", "8*@mail.ru", "Это я всем привет");
insert into customers(name, address, phone, email, note) values("Гена", "4", "786", "*465@gmail.ru", "");
insert into customers(name, address, phone, email, note) values("Глеб", "м. Молодёжная", "8(916)-???-?5-?2", "f565@yandex.ru", "Это привет");
insert into customers(name, address, phone, email, note) values("Саша", "м. Тульская", "8(916)-???-?5-3?", "gg78g@yandex.ru", "Это я вивет");
insert into customers(name, address, phone, email, note) values("Паша", "м. Арбатская", "8(916)-?6?-??-14", "fk645jg@yandex.ru", "Это я вивет");
# адрес может повторяться (раличные покупатели из одного и того же места)
# email и телефон не могут повторяться, они строго привязаны друг к другу

insert into shipments(customers_id, date, delivery_note, note) values(1, '2020-09-20', "0000000001", "Ок");
insert into shipments(customers_id, date, delivery_note, note) values(2, '2020-09-21', "0000000002", "отправили с задержкой");
insert into shipments(customers_id, date, delivery_note, note) values(5, '2020-09-22', "0000000003", "Товар не доставили");
insert into shipments(customers_id, date, delivery_note, note) values(4, '2020-09-23', "0000000004", "");

# insert into goods_shipments(shipments_id, goods_id) values(1, 1);
# insert into goods_shipments(shipments_id, goods_id) values(1, 2);
# insert into goods_shipments(shipments_id, goods_id) values(2, 3);
# insert into goods_shipments(shipments_id, goods_id) values(2, 4);
# insert into goods_shipments(shipments_id, goods_id) values(3, 10);
# insert into goods_shipments(shipments_id, goods_id) values(3, 11);
# insert into goods_shipments(shipments_id, goods_id) values(4, 12);
# если товар находится в shipments goods, то надо выставить goods.state = 1




insert into goods(catalog_id, state_id, production_date, note) values(1, 1, '2001-01-01', "Чай");
insert into goods(catalog_id, state_id, production_date, note) values(1, 1, '2001-01-02', "");
insert into goods(catalog_id, state_id, production_date, note) values(1, 1, '2001-01-03', "");
insert into goods(catalog_id, state_id, production_date, note) values(2, 1, '2020-12-22', "");
insert into goods(catalog_id, state_id, production_date, note) values(2, 1, '2001-01-05', "");
insert into goods(catalog_id, state_id, production_date, note) values(2, 1, '2001-01-05', "Была вскрыта упаковка");
insert into goods(catalog_id, state_id, production_date, note) values(3, 1, '2001-01-06', "");
insert into goods(catalog_id, state_id, production_date, note) values(3, 1, '2001-01-07', "");
insert into goods(catalog_id, state_id, production_date, note) values(3, 1, '2001-01-08', "");
insert into goods(catalog_id, state_id, production_date, note) values(4, 1, '2001-01-09', "");
insert into goods(catalog_id, state_id, production_date, note) values(4, 1, '2020-12-22', "");
insert into goods(catalog_id, state_id, production_date, note) values(4, 1, '2001-01-10', "");
insert into goods(catalog_id, state_id, production_date, note) values(5, 1, '2001-01-01', "");
insert into goods(catalog_id, state_id, production_date, note) values(5, 1, '2001-01-02', "");
insert into goods(catalog_id, state_id, production_date, note) values(5, 1, '2001-01-03', "");
insert into goods(catalog_id, state_id, production_date, note) values(6, 1, '2001-01-05', "");
insert into goods(catalog_id, state_id, production_date, note) values(6, 1, '2001-01-05', "");
insert into goods(catalog_id, state_id, production_date, note) values(6, 1, '2001-01-06', "");
insert into goods(catalog_id, state_id, production_date, note) values(7, 1, '2001-01-07', "");
insert into goods(catalog_id, state_id, production_date, note) values(7, 1, '2001-01-08', "");
insert into goods(catalog_id, state_id, production_date, note) values(7, 1, '2001-01-09', "");
insert into goods(catalog_id, state_id, production_date, note) values(8, 1, '2020-12-22', "");
insert into goods(catalog_id, state_id, production_date, note) values(8, 1, '2001-01-10', "");
insert into goods(catalog_id, state_id, production_date, note) values(8, 1, '2001-01-07', "Уценка (поцарапан)");
insert into goods(catalog_id, state_id, production_date, note) values(9, 1, '2001-01-08', "");
insert into goods(catalog_id, state_id, production_date, note) values(9, 1, '2001-01-09', "");
insert into goods(catalog_id, state_id, production_date, note) values(9, 1, '2020-12-22', "");
insert into goods(catalog_id, state_id, production_date, note) values(9, 1, '2001-01-10', "Уценка (поцарапан)");



# delete from goods
# LIMIT 18446744073709551615;  # unsigned long long


call add_goods(1000, 10,'1000-10-10', '1000');
select count(id) FROM goods;
# CREATE PROCEDURE sell_package(IN in_goods_id INT, in_shipments_id int)
call sell_package(10, 1);
call sell_package(11, 1);
call sell_package(12, 1);
call sell_package(13, 1);
call sell_package(14, 1);
call sell_package(15, 2);
call sell_package(16, 2);
call sell_package(17, 2);
call sell_package(18, 2);
call sell_package(19, 2);
call sell_package(20, 3);
call sell_package(21, 4);
