from datetime import datetime
try:
    from sklearn.linear_model import LinearRegression
except Exception:
    LinearRegression = None

class TrafficPredictor:
    def __init__(self, rows): self.rows = rows
    def features(self, row):
        dt = datetime.fromisoformat(row['observed_at']); cap=max(1,row['capacity'])
        return [dt.hour, int(dt.weekday() >= 5), int(dt.hour in [11,13,18,20]), row['occupied']/cap*100, row['active_bookings']/cap*100]
    def predict(self, hour, current_pct, booking_load, capacity):
        hour=int(hour); current_pct=float(current_pct); booking_load=float(booking_load)
        X=[self.features(r) for r in self.rows]; y=[r['occupied']/max(1,r['capacity'])*100 for r in self.rows]
        meal=int(hour in [11,13,18,20]); f=[hour,0,meal,current_pct,booking_load/max(1,capacity)*100]
        if LinearRegression and len(X)>4:
            model=LinearRegression().fit(X,y); predicted=float(model.predict([f])[0]); model_name='LinearRegression'
        else:
            predicted=current_pct*.55+(12 if meal else 0)+f[4]*.7; model_name='weighted fallback'
        predicted=max(4,min(98,round(predicted)))
        label='Low traffic' if predicted<40 else 'Moderate traffic' if predicted<70 else 'High traffic' if predicted<88 else 'Very busy'
        reasons=[]
        if meal: reasons.append('meal-time demand lifts occupancy')
        if current_pct>65: reasons.append('current crowd is already elevated')
        if f[4]>8: reasons.append('active bookings add pressure')
        if not reasons: reasons.append('outside the main meal windows')
        return {'predicted_pct':predicted,'label':label,'band':f'{max(0,predicted-8)}–{min(100,predicted+8)}%','reasons':reasons,'features':{'hour':hour,'meal_period':bool(meal),'current_pct':round(current_pct),'booking_load':round(booking_load)},'model':model_name}
