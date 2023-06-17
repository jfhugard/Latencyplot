#!/usr/bin/env python3

import sys
import json
import matplotlib.pyplot as plt
import matplotlib.ticker

def maxlat(x, y):
  maximum = 0
  for lat in x:
    if lat == max(x):
      break
    if y[lat] > 0:
      maximum = lat
  return maximum

def plot(infilename, outfilename):
  with open(infilename, 'r') as f:
    rt= json.load(f)
  cores = rt['latency']['cores']
  cores[0].append(max(cores[0]) + 1)

  fig, ax = plt.subplots()
  fig.set_figwidth(16)
  fig.set_figheight(9)

  try:
    rt['kernel']['patches']
    patched = 'patched '
  except:
    patched = ''
  plt.title('Latency histogram of ' + rt['system']['hostname'].split('.')[0] + ' with ' + rt['processor']['vendor'] +
   ' ' + rt['processor']['type'] + ' (' + rt['processor']['family'] + '), ' + patched + 'kernel ' + rt['kernel']['version'], fontsize=14)
  plt.yscale('log')
  plt.ylim(0.8E0, 1E8)
  plt.ylabel('Number of samples per latency class')
  maxofmax = 0
  for i in range(1, len(cores)):
    maxofcore = maxlat(cores[0], cores[i])
    if maxofcore > maxofmax:
      maxofmax = maxofcore
      coreofmax = i
    if i <= 10:
      space = '  '
    else:
      space = ''
    ax.stairs(cores[i], cores[0], label='Core #' + str(i-1) + ': ' + space + str(maxofcore) + ' µs')
  plt.xlabel('Maximum latency: ' + str(maxofmax) + ' µs, with "' + rt['condition']['cyclictest'] + '" on ' + rt['timestamps']['origin'].split('T')[0])
  plt.margins(0, 0)
  ax.yaxis.set_minor_locator(matplotlib.ticker.LogLocator(base=10.0, subs=(0.2,0.4,0.6,0.8), numticks=12))
  ax.yaxis.set_major_locator(matplotlib.ticker.LogLocator(base=10.0, numticks=10))
  plt.legend(ncol=6).get_texts()[coreofmax - 1].set_fontweight('bold')
  if len(outfilename) == 0:
    plt.show()
  else:
    plt.savefig(outfilename)

def main(argv):
  if len(argv) > 1:
    infilename = argv[1]
  else:
    infilename = 'rt.json'
  if len(argv) > 2:
    outfilename = argv[2]
  else:
    outfilename = ''
  plot(infilename, outfilename)

if __name__ == '__main__':
  main(sys.argv)
