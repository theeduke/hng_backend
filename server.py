from flask import Flask, jsonify, request
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route('/api', methods = ['GET'])
def api():
    slack_name = request.args.get('slack name',type=str)
    
    current_day = datetime.utcnow().strftime('%A')
    
    current_utc_time = datetime.utcnow() + timedelta(hours=1 )
    
    track = request.args.get('track', type=str)
    
    #JSON object to be returned
    
    if(request.method == 'GET'):
        data = {
            "slack_name" : slack_name,
            "current_day" : current_day,
            "current_utc_time" : current_utc_time.strftime('%Y-%m-%d %H:%M:%S'),
            "track" : track,
            "github_url_file": "https://github.com/theeduke/hng_backend/blob/main/server.py",
            "github_url_source": "https://github.com/theeduke/hng_backend",
            "status code" : 200
        }
  
        return jsonify(data),  200
    if __name__=='__main__':
        app.run(debug=True)