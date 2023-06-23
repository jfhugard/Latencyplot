#!/usr/bin/env python3

# This software is licensed under GPL-3.0
# Copyright (c) 2023 Open Source Automation Development Lab (OSADL) eG <info@osadl.org>
# Author Carsten Emde <C.Emde@osadl.org>

import sys
import json
import matplotlib.pyplot as plt
import matplotlib.ticker
import xml.etree.ElementTree as ET
from io import BytesIO

ET.register_namespace("", "http://www.w3.org/2000/svg")

def maxlat(x, y):
    maximum = 0
    for lat in x:
        if lat == max(x):
            break
        if y[lat] > 0:
            maximum = lat
    return maximum

def plot(infilename, outfilename):
    """Read JSON data from "infilename" and create latency histogram "outfilename" with format derived from file name suffix."""
    with open(infilename, 'r', encoding='utf-8') as f:
        rt = json.load(f)
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
    if 'clock' in rt['processor'].keys():
        clock = ' @' + rt['processor']['clock'] + ' MHz'
    else:
        clock = ''
    plt.title('Latency histogram of ' + rt['system']['hostname'].split('.')[0] + ' with ' + rt['processor']['vendor'] +
     ' ' + rt['processor']['type'] + clock + ' (' + rt['processor']['family'] + '), ' + patched + 'kernel ' + rt['kernel']['version'], fontsize=14)
    plt.yscale('log')
    plt.ylim(0.8E0, rt['condition']['cycles'])
    plt.ylabel('Number of samples per latency class')
    maxofmax = -1
    containers = []
    for i in range(1, len(cores)):
        if len(rt['latency']['maxima']) == 0:
            maxofcore = maxlat(cores[0], cores[i])
        else:
            maxofcore = rt['latency']['maxima'][i-1]
        if maxofcore >= maxofmax:
            if maxofcore > maxofmax:
                coresofmax = []
            coresofmax.append(i-1)
            maxofmax = maxofcore
        if i <= 10:
            space = '  '
        else:
            space = ''
        container = ax.stairs(cores[i], cores[0], label='Core #' + str(i-1) + ': ' + space + str(maxofcore) + ' µs')
        containers.append(container)
    plt.xlabel('Latency (µs) with "' + rt['condition']['cyclictest'] + '"')
    plt.margins(0, 0)
    plt.locator_params(axis = 'x', nbins = 8)
    ax.yaxis.set_minor_locator(matplotlib.ticker.LogLocator(base=10.0, subs=(0.2,0.4,0.6,0.8), numticks=12))
    ax.yaxis.set_major_locator(matplotlib.ticker.LogLocator(base=10.0, numticks=10))
    leg = plt.legend(ncol=6)
    for i in coresofmax:
        leg.get_texts()[i].set_color('red')
    ax.text(0.995, 0.5, 'Measurement on ' + rt['timestamps']['origin'].split('T')[0], fontsize = 'x-small', color = 'grey',
        horizontalalignment='center', verticalalignment='center', rotation='vertical', transform=ax.transAxes)

    if len(outfilename) != 0:
        suffix = outfilename.split('.')
        suffix = suffix[len(suffix) - 1]
    else:
        suffix = ''

    if suffix == 'svg':

        for i in range(0, len(containers)):
            containers[i].set_gid(f'stairs_{i}')

        f = BytesIO()
        plt.savefig(f, format=suffix)

        tree, xmlid = ET.XMLID(f.getvalue())
        tree.attrib.pop('width', None)
        tree.attrib.pop('height', None)

        legend1 = xmlid['legend_1']
        text1 = -1
        line1 = -1
        for child in legend1:
            id = child.attrib['id']
            if id.startswith('text_'):
                if text1 == -1:
                    text1 = int(id.split('_')[1])
                for nextchild in child:
                    if nextchild.tag[len(nextchild.tag) - 1] == 'g':
                        endofstring = float(nextchild[len(nextchild) - 1].get('x')) + 60
                        path = ET.SubElement(nextchild, 'path')
                        path.set('d', 'M 0 -11 H ' + str(endofstring) + ' V 80 H 0 Z')
                        path.set('style', 'fill: #fff; opacity: 0;')
                        path.set('cursor', 'pointer')
                        path.set('onclick', "toggle_stairsfromtext(event, this)")
                        break
            if line1 == -1 and id.startswith('line2d_'):
                line1 = int(id.split('_')[1])

        offsets = [text1, line1]

        texts = leg.get_texts()
        for i in range(0, len(texts)):
            el = xmlid[f'line2d_{i+line1}']
            el.set('cursor', 'pointer')
            el.set('onclick', "toggle_stairsfromline(event, this)")
            el.set('style', 'opacity: 1; stroke-width: 8px;')

        script = """
<script type="text/javascript">
<![CDATA[
var offsets = %s;
function toggle(oid, attribute, values) {
    var obj = document.getElementById(oid);
    var a = obj.style[attribute];

    a = (a == values[0] || a == "") ? values[1] : values[0];
    obj.style[attribute] = a;
}

function allenable() {
    var i = 0;

    while ((ele = document.getElementById('stairs_' + i)) != null) {
        ele.style.opacity =
        document.getElementById('text_' + (i + offsets[0])).style.opacity =
        document.getElementById('line2d_' + (i + offsets[1])).style.opacity = 1;
        i++;
    }
}

function allbutonedisable(thisnot) {
    var i = 0;

    while ((ele = document.getElementById('stairs_' + i)) != null) {
        if (i != thisnot) {
            ele.style.opacity = 0;
            document.getElementById('text_' + (i + offsets[0])).style.opacity = 0.5;
            document.getElementById('line2d_' + (i + offsets[1])).style.opacity = 0.3;
        }
        i++;
    }
    document.getElementById('stairs_' + thisnot).style.opacity = 1;
    document.getElementById('text_' + (thisnot + offsets[0])).style.opacity = 1;
    document.getElementById('line2d_' + (thisnot + offsets[1])).style.opacity = 1;
}

function toggle_stairsfromtext(event, obj) {
    var num = obj.parentElement.parentElement.id.split('_')[1];

    if (event.ctrlKey)
        allbutonedisable(parseInt(num) - offsets[0]);
    else if (event.shiftKey)
        allenable();
    else {
        toggle('text_' + num, 'opacity', [1, 0.5]);
        toggle('line2d_' + (parseInt(num) + offsets[1] - offsets[0]), 'opacity', [1, 0.3]);
        toggle('stairs_' + (parseInt(num) - offsets[0]), 'opacity', [1, 0]);
    }
}

function toggle_stairsfromline(event, obj) {
    var num = obj.id.split('_')[1];

    if (event.ctrlKey)
        allbutonedisable(parseInt(num) - offsets[1]);
    else if (event.shiftKey)
        allenable();
    else {
        toggle('line2d_' + num, 'opacity', [1, 0.3]);
        toggle('text_' + (parseInt(num) + offsets[0] - offsets[1]), 'opacity', [1, 0.5]);
        toggle('stairs_' + (parseInt(num) - offsets[1]), 'opacity', [1, 0]);
    }
}
]]>
</script>
""" % json.dumps(offsets)

        css = tree.find('.//{http://www.w3.org/2000/svg}style')
        css.text = css.text + "g {-webkit-transition:opacity 0.4s ease-out;" + \
            "-moz-transition:opacity 0.4s ease-out;}"

        tree.insert(0, ET.XML(script))

        ET.ElementTree(tree).write(outfilename)

    else:
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
