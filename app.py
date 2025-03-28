# app.py
from flask import Flask, render_template, request, send_file
import os
from scrapers.laptopsdirect import scrape_laptopsdirect
from scrapers.scan import scrape_scan
from scrapers.overclockers import scrape_overclockers
from scrapers.currys import scrape_currys

app = Flask(__name__)
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

SCRAPERS = {
    'LaptopsDirect': scrape_laptopsdirect,
    'SCAN': scrape_scan,
    'Overclockers': scrape_overclockers,
    'Currys': scrape_currys,
}

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        company = request.form.get('company')
        if company in SCRAPERS:
            csv_path = os.path.join(DATA_DIR, f'{company.lower()}.csv')
            SCRAPERS[company](csv_path)
            return send_file(csv_path, as_attachment=True)
        return "Invalid company selected", 400
    return render_template('index.html', companies=SCRAPERS.keys())

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)