from flask import Flask, jsonify, request
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route('/api', methods = ['GET'])
def api():
    name = request.args.get('name')
    if not name:
        return jsonify(error = "name parameter is missing"), 400
    current_day = datetime.utcnow().strftime('%A')
    
    current_utc_time = datetime.utcnow() + timedelta(hours=2)
    
    track = request.args.get('backend')
    if not track:
        return jsonify(error = "track parameter is missing"), 400
    
    if(request.method == 'GET'):
        data = {
            "name" : name,
            "current_day" : current_day,
            "current_utc_time" : current_utc_time.strftime('%Y-%m-%d %H:%M:%S'),
            "track" : track,
            "github_url_file": "https://github.com/your_username/your_repository/blob/main/app.py",
            "github_url_source": "https://github.com/your_username/your_repository"
            
        }
  
        return jsonify(data),  200
    if __name__=='__main__':
        app.run(debug=True)