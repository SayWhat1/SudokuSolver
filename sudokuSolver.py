from random import choice
from time import time


def getPuzzle(filename):
    infile = open(filename, 'r')
    raw_data = infile.readlines()
    puzzles = []
    for i in raw_data:
        puzzles.append(i.lstrip())
    return puzzles


# Code borrowed from http://norvig.com/sudoku.html, because why reinvent the wheel?
def cross(A, B):
    return [a + b for a in A for b in B]

digits = '123456789'
rows = 'ABCDEFGHI'
cols = digits
squares = cross(rows, cols)
allunits = ([cross(rows, c) for c in cols] + [cross(r,cols) for r in rows] + [cross(rs, cs) for rs in ('ABC', 'DEF', 'GHI') for cs in ('123','456','789')])
units = dict((s, [u for u in allunits if s in u]) for s in squares)
peers = dict((s, set(sum(units[s], [])) - set([s])) for s in squares)
# I borrowed it, but I had to change it a bit to fit my needs.


def isSolved(values):
    if len([v for s in squares for v in values[s]]) == 81:
        return True
    else:
        return False


def fillPuzzle(puzzle):
    values = dict(zip(squares, [v for v in puzzle]))
    for s in values.keys():
        if values[s] == '0':
            values[s] = digits
    return values


def elimCanidates(values):
    changed = False
    if isSolved(values):
        return False

    else:
        for s in values.keys():
            if len(values[s]) == 1:
                continue
            else:
                testsquares = [v for v in peers[s]]
                testval = [values[sq] for sq in testsquares if len(values[sq]) == 1]
                for v in testval:
                    if v in values[s] and len(values[s]) != 1:
                        values[s] = values[s].replace(v, '')
                        changed = True
                for v in values[s]:
                    testsquare = [sq for sq in set(sum([units[s][0]], [])) if v in values[sq]]
                    if len(testsquare) == 1 and len(values[s]) != 1:
                        values[s] = v
                        changed = True
                for v in values[s]:
                    testsquare = [sq for sq in set(sum([units[s][1]], [])) if v in values[sq]]
                    if len(testsquare) == 1 and len(values[s]) != 1:
                        values[s] = v
                        changed = True
                for v in values[s]:
                    testblock = [sq for sq in units[s][2] if v in values[sq]]
                    if len(testblock) == 1 and len(values[s]) != 1:
                        values[s] = v
                        changed = True
    return changed


def nakedDoubles(values):
    changed = False
    if isSolved(values):
        return False
# Rows First.
    else:
        for s in values.keys():
            if len(values[s]) != 2:
                continue
            else:
                testsq = dict(zip(units[s][1], [values[sq] for sq in units[s][1]]))
                for sq in testsq.keys():
                    if testsq[sq] == values[s] and sq != s:
                        toremove = values[s]
                        for v in toremove:
                            for key in testsq.keys():
                                if (key == sq or key == s) or len(values[key]) != 1 or v not in values[key]:
                                    continue
                                else:
                                    values[key] = values[key].replace(v, '')
                                    changed = True
                            while elimCanidates(values):
                                elimCanidates(values)
    # Now Columns
        for s in values.keys():
            if len(values[s]) != 2:
                continue
            else:
                testsq = dict(zip(units[s][0], [values[sq] for sq in units[s][0]]))
                for sq in testsq.keys():
                    if testsq[sq] == values[s] and sq != s:
                        toremove = values[s]
                        for v in toremove:
                            for key in testsq.keys():
                                if (key == sq or key == s) or len(values[key]) != 1 or v not in values[key]:
                                    continue
                                else:
                                    values[key] = values[key].replace(v, '')
                                    changed = True
                            while elimCanidates(values):
                                elimCanidates(values)
    return changed


def hiddenDoubles(values):
    changed = False
    if isSolved(values):
        return False
# Rows first.
    else:
        for s in values.keys():
            if len(values[s]) == 1:
                continue
            else:
                for sq in units[s][1]:
                    test = list(set(cross(values[s], values[s])).intersection(cross(values[sq], values[sq])))
                    test = list(set(''.join(test)))
                    test = [a+b for a in test for b in test if a != b]
                    test = [''.join(sorted(a)) for a in test]
                    test = list(set(test))
                    test2 = list(set([values[squ] for squ in units[s][1] if squ != s]).intersection([values[squ] for squ in units[sq][1] if squ != sq]))
                    test2 = ''.join(list(set(''.join(test2))))
                    for i in test:
                        if i[0] in test2 or i[1] in test2:
                            continue
                        else:
                            values[s], values[sq] = i, i
                            changed = True
                            elimCanidates(values)
# Now Columns!
        for s in values.keys():
            if len(values[s]) == 1:
                continue
            else:
                for sq in units[s][0]:
                    test = list(set(cross(values[s], values[s])).intersection(cross(values[sq], values[sq])))
                    test = list(set(''.join(test)))
                    test = [a+b for a in test for b in test if a != b]
                    test = [''.join(sorted(a)) for a in test]
                    test = list(set(test))
                    test2 = list(set([values[squ] for squ in units[s][0] if squ != s]).intersection([values[squ] for squ in units[sq][0] if squ != sq]))
                    test2 = ''.join(list(set(''.join(test2))))
                    for i in test:
                        if i[0] in test2 or i[1] in test2:
                            continue
                        else:
                            values[s], values[sq] = i, i
                            changed = True
                            elimCanidates(values)
    while elimCanidates(values):
            elimCanidates(values)
    return changed


# This is just for testing purposes, but I lifted this from http://norvig.com/sudoku.html also
def printPuzzle(values):
    width = 1+max(len(values[s]) for s in squares)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print ''.join(values[r+c].center(width)+('|' if c in '36' else '') for c in cols)
        if r in 'CF': print line
    print


def sodukuSolver():
    solved, solvedpuz, times = 0, [], []
    puzzles = getPuzzle('subig20.txt')
    for puz in puzzles[:50]:
        start = time()
        value = fillPuzzle(puz)
        while elimCanidates(value):
            if isSolved(value):
                break
            elimCanidates(value)
        while nakedDoubles(value) or hiddenDoubles(value):
            if isSolved(value):
                break
            nakedDoubles(value)
            hiddenDoubles(value)
        if isSolved(value):
            solved += 1
            solvedpuz.append(value)
        end = time() - start
        times.append(end)
        if end >= 1:
            printPuzzle(value)
    print 'Number solved {} out of {} or {:.2f}% with an average time of {:.3f}s'.format(solved, len(puzzles), (float(solved)/len(puzzles))*100, sum(times)/float(len(times)))
    printPuzzle(choice(solvedpuz))
sodukuSolver()

# I used http://www.sudokudragon.com/sudokustrategy.htm to get a detailed run down of
# the strategies I employed and I got the files of puzzles from
# http://www2.warwick.ac.uk/fac/sci/moac/people/students/peter_cock/python/sudoku/
# My script doesn't deal with the '.' like the downloaded files have, so you have to
# use your favorite text editor and Find and Replace all the '.' with '0'.  Also, the
# last line of each of those txt files has a weird character, so you'll have to go in and
# delete it by hand or the getPuzzle() function will hang on it.