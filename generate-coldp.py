# -*- coding: utf-8 -*-

import csv, re

idCol   = 0
nameCol = 1
authCol = 2
yearCol   = 3
sourceCol = 4
pagesCol  = 5
misspellingCol = 6
assessmentCol  = 7
remarksCol  = 8
basionymCol = 10
linkCol = 11

idMatcher    = re.compile('<(\d+)>(.+)')
asMatcher    = re.compile('^as +(.+)')
badMatcher   = re.compile('([";<>?*]| in )')
brackMatcher = re.compile('[\[\]]')
brackAuthMatcher = re.compile('\[([^\[\]]+) *(\]|$)')



global parsedAuthors

def unescape(x):
    # TODO: html entities
    return x

def replBracketAuthors(m):
    global parsedAuthors
    #print("Bracket found: " + m.group(0))
    if (m.group(1)[0].islower()):
        return m.group(1)
    else:
        parsedAuthors.append(m.group(1))
        return ""


with open('extract_output.csv', 'r') as inFile:
    species = csv.reader(inFile, delimiter='\t')
    with open('name.tsv', 'w', newline='') as nameFile:
        name = csv.writer(nameFile, delimiter='\t')
        name.writerow(["ID","scientificName","authorship", "publishedInID", "publishedInYear", "status", "remarks", "link"])
        with open('name-rel.tsv', 'w', newline='') as nameRelFile:
            nameRel = csv.writer(nameRelFile, delimiter='\t')
            nameRel.writerow(["nameID","relatedNameID","type"])
            with open('reference.tsv', 'w', newline='') as referenceFile:
                reference = csv.writer(referenceFile, delimiter='\t')
                reference.writerow(["ID","year","source","details"])
                refs  = {}
                for row in species:
                    id      = row[idCol]
                    if "code" in id:
                        continue
                    refID = None
                    ref = "|".join([row[sourceCol], row[yearCol], row[pagesCol]])
                    if ref:
                        if ref in refs:
                            refID = refs[ref]
                        else:
                            refID = "r"+id
                            refs[ref] = refID
                            reference.writerow([refID, row[yearCol], row[sourceCol], row[pagesCol]])
                    parsedAuthors = []
                    auth    = brackMatcher.sub("", unescape(row[authCol]))
                    sciname = brackAuthMatcher.sub(replBracketAuthors, unescape(row[nameCol]))
                    remarks = unescape(row[remarksCol])
                    if parsedAuthors:
                        auth = " ".join(parsedAuthors + [auth])
                        #print(sciname + "  ||  " + auth)
                    name.writerow([id, sciname, auth, refID, row[yearCol], row[assessmentCol], remarks, row[linkCol]])
                    if row[basionymCol]:
                        m = idMatcher.search(row[basionymCol])
                        if m:
                            nameRel.writerow([id, m.group(1), "basionym"])
                        else:
                            print("Basionym without ID: " + row[basionymCol])
                    if row[misspellingCol]:
                        m = asMatcher.search(row[misspellingCol])
                        if m:
                            # usually a full name, but sometime with comments and weird stuff we simply ignore
                            if badMatcher.search(m.group(1)):
                                print("BAD misspelling: " + m.group(1))
                                misspelling = None
                            else:
                                misspelling = unescape(m.group(1))
                                print("Unparsed misspelling: " + misspelling)
                        else:
                            # epithet only
                            misspelling = sciname.rpartition(' ')[0]  + ' ' + unescape(row[misspellingCol])

                        if misspelling:
                            #print("Misspelling: " + misspelling)
                            idAlt = id + "-alt"
                            name.writerow([idAlt, misspelling, auth, refID, row[yearCol], row[assessmentCol], remarks, row[linkCol]])
                            nameRel.writerow([id, idAlt, "spelling correction"])

