# Covid-19 Real-Time Data Tracker for USA

This is a pure Python dashboard built with Ploly's Dash - a framework for browser based data visualization. It is connected to API data source (www.covidtracking.com) and updated each time the API updates.

Running online currently on Heroku (testing puropeses): https://covidtrackboard.herokuapp.com/

## Instalation

Installation via requirements.txt:

```
git clone https://github.com/ExperimentalHypothesis/dash-covidtrackboard
cd dash-covidtrackboard
python -m venv myenv (or possibly python3 -m venv myenv)
source myenv/bin/activate (on Windows myenv\Scripts\activate.bat)
pip install -r requirements.txt (or possibly pip3 install -r requirements.txt)
```

## Run

```
python app.py (or possibly python3 app.py)
```


