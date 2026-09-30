import sqlite3
from pathlib import Path
from datetime import datetime,timedelta
DB=Path(__file__).parent/'data/campusbite.db'; DB.parent.mkdir(exist_ok=True)
CANTEENS=[('snackers','Snackers','Student Activity Centre','10:00 AM – 10:00 PM',80,34,'Snacks, rolls, shakes'),('nestle','Nestle','Academic Block','8:00 AM – 8:00 PM',60,24,'Coffee, Maggi, quick bites'),('dominos','Dominos','Food Court','11:00 AM – 11:30 PM',120,71,'Pizza, sides, beverages'),('yadav-canteen','Yadav Canteen','Boys Hostel Lane','7:30 AM – 11:00 PM',95,52,'North Indian meals, thali'),('night-canteen','Night Canteen','Central Lawn','8:00 PM – 3:00 AM',70,18,'Late-night comfort food'),('campus-cafe','Campus Cafe','Library Road','9:00 AM – 9:00 PM',90,42,'Sandwiches, coffee, desserts')]
MENUS={
'snackers':[('Aloo Tikki Burger',55,'Popular'),('Paneer Roll',70,'Veg'),('Cold Coffee',65,'Beverage')],
'nestle':[('Masala Maggi',45,'Quick bite'),('Cappuccino',80,'Beverage'),('Veg Sandwich',60,'Light meal')],
'dominos':[('Farmhouse Medium',399,'Popular'),('Garlic Bread',149,'Side'),('Pepsi',60,'Beverage')],
'yadav-canteen':[('Rajma Rice',80,'Meal'),('Paneer Thali',120,'Meal'),('Lassi',45,'Beverage')],
'night-canteen':[('Egg Maggi',70,'Late-night'),('Chai',25,'Beverage'),('Bread Omelette',65,'Popular')],
'campus-cafe':[('Grilled Sandwich',110,'Popular'),('Iced Latte',120,'Beverage'),('Brownie',90,'Dessert')]}
def con():
 c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; return c
def seed():
 c=con(); c.executescript('''CREATE TABLE IF NOT EXISTS canteens(id INTEGER PRIMARY KEY,slug TEXT UNIQUE,name TEXT,location TEXT,hours TEXT,capacity INTEGER,occupied INTEGER,specialty TEXT,is_open INTEGER DEFAULT 1,updated_at TEXT);CREATE TABLE IF NOT EXISTS menu_items(id INTEGER PRIMARY KEY,canteen_id INTEGER,name TEXT,price INTEGER,tag TEXT);CREATE TABLE IF NOT EXISTS occupancy_history(id INTEGER PRIMARY KEY,canteen_id INTEGER,observed_at TEXT,occupied INTEGER,capacity INTEGER,active_bookings INTEGER);CREATE TABLE IF NOT EXISTS bookings(id INTEGER PRIMARY KEY,canteen_id INTEGER,student_name TEXT,student_id TEXT,booking_date TEXT,booking_time TEXT,seats INTEGER,status TEXT,created_at TEXT);''')
 if c.execute('SELECT COUNT(*) n FROM canteens').fetchone()['n']==0:
  for slug,name,loc,hours,cap,occ,specialty in CANTEENS:
   cid=c.execute('INSERT INTO canteens(slug,name,location,hours,capacity,occupied,specialty,updated_at) VALUES(?,?,?,?,?,?,?,?)',(slug,name,loc,hours,cap,occ,specialty,datetime.now().isoformat(timespec='minutes'))).lastrowid
   for m in MENUS[slug]: c.execute('INSERT INTO menu_items(canteen_id,name,price,tag) VALUES(?,?,?,?)',(cid,*m))
   for ago in range(14):
    for hour,base in [(9,.32),(11,.57),(13,.86),(15,.42),(18,.72),(20,.63)]:
     day=datetime.now()-timedelta(days=ago); value=max(0,min(cap,int(cap*(base+(((ago*7+hour+cid*3)%13-6)/100)))))
     c.execute('INSERT INTO occupancy_history(canteen_id,observed_at,occupied,capacity,active_bookings) VALUES(?,?,?,?,?)',(cid,day.replace(hour=hour,minute=0,second=0,microsecond=0).isoformat(),value,cap,int(value*(.12 if hour in [11,13,18,20] else .05))))
  c.commit()
 c.close()
def canteens():
 c=con(); out=[]
 for r in c.execute('SELECT * FROM canteens ORDER BY id'):
  x=dict(r); x['is_open']=bool(x['is_open']); x['available']=max(0,x['capacity']-x['occupied']); x['crowd_pct']=round(x['occupied']/x['capacity']*100); x['menu']=[dict(m) for m in c.execute('SELECT name,price,tag FROM menu_items WHERE canteen_id=?',(r['id'],))]; out.append(x)
 c.close(); return out
def one(slug): return next((x for x in canteens() if x['slug']==slug),None)
def history(slug):
 c=con(); rows=[dict(r) for r in c.execute('SELECT h.* FROM occupancy_history h JOIN canteens c ON c.id=h.canteen_id WHERE c.slug=? ORDER BY observed_at',(slug,))]; c.close(); return rows
def bookings():
 c=con(); rows=[dict(r) for r in c.execute("SELECT b.*,c.name canteen_name,c.slug FROM bookings b JOIN canteens c ON c.id=b.canteen_id WHERE b.student_id='NITJ-DEMO' ORDER BY b.booking_date,b.booking_time")]; c.close(); return rows
def create(p):
 if not all(k in p for k in ['slug','booking_date','booking_time','seats']): raise ValueError('Please complete all booking fields.')
 seats=int(p['seats']); x=one(p['slug'])
 if not x: raise ValueError('Canteen not found.')
 if not x['is_open']: raise ValueError('This canteen is currently closed.')
 if seats<1 or seats>8: raise ValueError('Choose between 1 and 8 seats.')
 if seats>x['available']: raise ValueError(f"Only {x['available']} seats are available right now.")
 c=con(); cur=c.execute("INSERT INTO bookings(canteen_id,student_name,student_id,booking_date,booking_time,seats,status,created_at) VALUES(?,?,?,?,?,?,?,?)",(x['id'],'Demo Student','NITJ-DEMO',p['booking_date'],p['booking_time'],seats,'confirmed',datetime.now().isoformat(timespec='minutes'))); c.execute('UPDATE canteens SET occupied=occupied+? WHERE id=?',(seats,x['id'])); c.commit(); row=dict(c.execute('SELECT b.*,c.name canteen_name,c.slug FROM bookings b JOIN canteens c ON c.id=b.canteen_id WHERE b.id=?',(cur.lastrowid,)).fetchone()); c.close(); return row
def cancel(i):
 c=con(); r=c.execute("SELECT * FROM bookings WHERE id=? AND student_id='NITJ-DEMO' AND status='confirmed'",(i,)).fetchone()
 if not r: c.close(); raise ValueError('Booking cannot be cancelled.')
 c.execute("UPDATE bookings SET status='cancelled' WHERE id=?",(i,)); c.execute('UPDATE canteens SET occupied=MAX(0,occupied-?) WHERE id=?',(r['seats'],r['canteen_id'])); c.commit(); c.close()
def update(slug,p):
 x=one(slug)
 if not x: raise ValueError('Canteen not found.')
 c=con(); cap=int(p.get('capacity',x['capacity'])); occ=max(0,min(cap,int(p.get('occupied',x['occupied'])))); c.execute('UPDATE canteens SET is_open=?,occupied=?,capacity=?,updated_at=? WHERE slug=?',(int(bool(p.get('is_open',x['is_open']))),occ,cap,datetime.now().isoformat(timespec='minutes'),slug)); c.commit(); c.close(); return one(slug)
