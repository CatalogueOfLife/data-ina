# -*- coding: utf-8 -*-

import csv, re

basionymCol   = 8
idMatcher   = re.compile('<(\d+)>(.+)')

with open('extract_output.csv', 'r') as inFile:
    reader = csv.reader(inFile, delimiter='\t')
    with open('taxon.csv', 'w', newline='') as outFile:
        out = csv.writer(outFile, delimiter='\t')
        for row in reader:
            basionym   = row[basionymCol]
            basionymID = None
            if basionym:
                m = idMatcher.search(basionym)
                if m:
                    basionym   = m.group(2)
                    basionymID = m.group(1)
            row[basionymCol]   = basionym
            row.append(basionymID)
            out.writerow(row)
