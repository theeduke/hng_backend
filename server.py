from flask import Flask, jsonify, request
from datetime import datetime

app = Flask(__name__)

@app.route('/api', methods = ['GET'])
def api():
    slack_name = request.args.get('slack_name',type=str)
    
    current_day = datetime.utcnow().strftime('%A')
    
    current_utc_time = datetime.utcnow()
    
    track = request.args.get('track', type=str)
    
    #JSON object to be returned
    
    if(request.method == 'GET'):
        data = {
            "slack_name" : slack_name,
            "current_day" : current_day,
            "utc_time" : current_utc_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "track" : track,
            "github_file_url": "https://github.com/theeduke/hng_backend/blob/main/server.py",
            "github_repo_url": "https://github.com/theeduke/hng_backend",
            "status code" : 200
        }
  
        return jsonify(data),  200
    if __name__=='__main__':
        app.run(debug=True)