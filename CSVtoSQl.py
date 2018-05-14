import csv, sqlite3

con = sqlite3.connect(":memory:")
cur = con.cursor()
con.text_factory = str

#Export nodes.csv to sql table
cur.execute("CREATE TABLE nodes (id, lat,lon,version);")
with open('nodes.csv','rb') as fin:
    dr = csv.DictReader(fin)
    to_db = [(i['id'], i['lat'],i['lon'],i['version']) for i in dr]

cur.executemany("INSERT INTO nodes (id, lat,lon,version) VALUES (?, ?,?,?);", to_db)

con.commit()

#Export nodes_tags.csv to sql table
cur.execute("CREATE TABLE nodes_tags (id, key,value,type);")

with open('nodes_tags.csv','rb') as fin:
    dr = csv.DictReader(fin)
    to_db = [(i['id'], i['key'],i['value'],i['type']) for i in dr]

cur.executemany("INSERT INTO nodes_tags (id, key,value,type) VALUES (?, ?,?,?);",to_db)

con.commit()

#Export ways.csv to sql table
cur.execute("CREATE TABLE ways (id, version);")

with open('ways.csv','rb') as fin:
    dr = csv.DictReader(fin)
    to_db = [(i['id'], i['version']) for i in dr]

cur.executemany("INSERT INTO ways (id, version) VALUES (?, ?);", to_db)

con.commit()

#Export ways_nodes.csv to sql table
cur.execute("CREATE TABLE ways_nodes (id, node_id,position);")

with open('ways_nodes.csv','rb') as fin:
    dr = csv.DictReader(fin)
    to_db = [(i['id'], i['node_id'],i['position']) for i in dr]

cur.executemany("INSERT INTO ways_nodes (id, node_id,position) VALUES (?, ?,?);", to_db)

con.commit()

#Export ways_tags.csv to sql table
cur.execute("CREATE TABLE ways_tags (id, key,value,type);")

with open('ways_tags.csv','rb') as fin:
    dr = csv.DictReader(fin)
    to_db = [(i['id'], i['key'],i['value'],i['type']) for i in dr]

cur.executemany("INSERT INTO ways_tags (id, key,value,type) VALUES (?, ?,?,?);", to_db)

con.commit()


#SQL Queries
cur.execute('SELECT count(*) FROM nodes ')
print cur.fetchone()

cur.execute('SELECT count(*) FROM ways ')
print cur.fetchone()

cur.execute('select value from (select value, count(1)  from nodes_tags where key="postcode" group by value order by count(1) desc) ')
print cur.fetchone()


cur.execute('SELECT distinct(value) FROM nodes_tags where key="cuisine" ')
cuisine=cur.fetchall()
len(cuisine)

cur.execute('SELECT value, count(id) as count_cuisine FROM nodes_tags where key="cuisine"  group by value order by count_cuisine DESC Limit 10 ')
top_ten_cuisine=cur.fetchall()
top_ten_cuisine

cur.execute('SELECT distinct(value) FROM nodes_tags where key="name"  and value LIKE "%pizza%"  and value NOT LIKE "%www.%" and value NOT LIKE "%.c%" or value LIKE "%PIZZA%"  and value NOT LIKE "%www.%" and value NOT LIKE "%.c%" or value LIKE "%Pizza%" and value NOT LIKE "%www.%" and value NOT LIKE "%.c%"')
pizza=cur.fetchall()
pizza

cur.execute('SELECT value FROM nodes_tags where key="name"  and value LIKE "%pizza%"  and value NOT LIKE "%www.%" and value NOT LIKE "%.c%" or value LIKE "%PIZZA%"  and value NOT LIKE "%www.%" and value NOT LIKE "%.c%" or value LIKE "%Pizza%" and value NOT LIKE "%www.%" and value NOT LIKE "%.c%"')
pizza_resturant_list=cur.fetchall()
heapq.nlargest(1, zip(pizza_resturant_list))
