import json
import datetime
import matplotlib.pyplot as plt
import pytz

with open('/Users/decarlo/Downloads/nest_last.jsonl', 'r') as json_file:
    json_list = list(json_file)

h_list = []
t_list = []

for json_str in json_list:
    
    result = json.loads(json_str)
    h0 = result['value']['samples'][0]['humidity']
    date = datetime.datetime.fromtimestamp(float(result['timestamp']), pytz.timezone("America/Denver"))
    print(date, float(result['timestamp']), (h0))
    t_list.append(date)
    h_list.append((h0))

n = 1
plt.plot(t_list[::n], h_list[::n])
plt.ylabel('% Relative Humidity')
plt.show()
