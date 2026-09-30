import os
from datetime import datetime
from flask import Flask,render_template,jsonify,request
from db import seed,canteens,one,history,bookings,create,cancel,update
from ml.traffic_model import TrafficPredictor
seed(); app=Flask(__name__)
def pred(c,h=None): return TrafficPredictor(history(c['slug'])).predict(h if h is not None else datetime.now().hour,c['crowd_pct'],0,c['capacity'])
@app.get('/')
def home(): return render_template('index.html')
@app.get('/admin')
def admin(): return render_template('index.html')
@app.get('/health')
def health(): return jsonify(status='ok',service='campusbite',database='sqlite')
@app.get('/manus-routes.json')
def routes(): return app.send_static_file('manus-routes.json')
@app.get('/api/summary')
def summary():
 cs=canteens(); return jsonify(student={'name':'Demo Student','student_id':'NITJ-DEMO'},canteens=[dict(c,prediction=pred(c)) for c in cs],bookings=bookings(),insight='Lunch peaks are usually strongest around 1:00 PM; try Nestle or Campus Cafe for a calmer midday stop.')
@app.get('/api/canteens/<slug>')
def detail(slug):
 c=one(slug)
 if not c:return jsonify(error='Canteen not found'),404
 return jsonify(dict(c,prediction=pred(c,request.args.get('hour',datetime.now().hour))))
@app.post('/api/bookings')
def book():
 try:
  b=create(request.get_json() or {}); return jsonify(booking=b,prediction=pred(one(b['slug']),int(b['booking_time'][:2]))),201
 except Exception as e:return jsonify(error=str(e)),400
@app.post('/api/bookings/<int:i>/cancel')
def cancel_api(i):
 try: cancel(i); return jsonify(ok=True,bookings=bookings())
 except Exception as e:return jsonify(error=str(e)),400
@app.patch('/api/admin/canteens/<slug>')
def update_api(slug):
 try:return jsonify(update(slug,request.get_json() or {}))
 except Exception as e:return jsonify(error=str(e)),400
if __name__=='__main__': app.run(host='0.0.0.0',port=int(os.getenv('PORT','5000')),debug=True)
