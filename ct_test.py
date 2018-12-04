import pickle
import sys

def judge(value):
  result = model.predict([[value]])
  low = model.labels_[0]
  high = model.labels_[-1]

  if result[0] == low:
    return "LOW"
  else:
    return "HIGH"


model = pickle.load(open("ct_model.sav","rb"))

print(judge(sys.argv[1]))