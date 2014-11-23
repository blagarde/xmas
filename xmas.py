from collections import defaultdict, Counter
from unicodecsv import DictReader
from itertools import chain
from pprint import pprint

XMAS_FILE = 'xmas.csv'


class Participant(object):
    def __init__(self, uid, name, group, godfather=None, families=[]):
        self.uid = uid
        self.name = name
        self.group = group
        self.godfather = godfather if godfather != '' else None
        self.families = families

    def __repr__(self):
        return '<%s>' % self.uid

class SecretSanta(object):
    def __init__(self, filepath):
        self.participants = {}
        self.presents = defaultdict(list)
        with open(filepath) as fh:
            rdr = DictReader(fh)
            for r in rdr:
                families = set([f for f in r['families'].split('|') if f != ''])
                self.participants[r['uid']] = Participant(r['uid'], r['name'],  r['group'], r['godfather'], families)
    
    def allocate(self):
        remaining = self.left_to_go()
        # godparents always give to their godchildren
        for p in self.participants.values():
            if p.godfather is not None:
                self.presents[p.uid] += [self.participants[p.godfather]]

        while sum(remaining.values()) > 0:
            cand_dct = {uid: self.santa_candidates(uid) for uid in self.participants}

            luckyguy = self.picksomeone(cand_dct, remaining)
            # Who hasn't yet given to 'luckyguy'
            candidate_lst = cand_dct[luckyguy.uid]
            # Check how many presents each santa has done so far
            counts = Counter(chain(*self.presents.values()))
            GIVES_AT_MOST = {'1': 1, '2': 0}
            candidates = [c for c in candidate_lst if c.group == '0' or counts[c] < GIVES_AT_MOST[c.group]]
            # Sort by presents given so far
            f = lambda c: counts[c] - GIVES_AT_MOST.get(c.group, 2)
            santa = sorted(candidates, key=f)[0]
            self.presents[luckyguy.uid] += [santa]
            remaining = self.left_to_go()
    
    def picksomeone(self, cand_dct, rem_dct):
        for u, n in rem_dct.items():
            if n > 0:
                assert cand_dct[u] >= n
        DCT = {u: float(rem_dct[u]) / len(cand_dct[u]) for u in self.participants}
        f = lambda u: DCT[u]
        uid = sorted(DCT.keys(), key=f)[-1]
        return self.participants[uid]
    
    def santa_candidates(self, uid):
        participant = self.participants[uid]
        already_giving = [s.uid for s in self.presents[uid]]
        santas = []
        for p in self.participants.values():
            if p.uid not in already_giving and len(participant.families.intersection(p.families)) == 0 and p.uid != uid:
                santas += [p]
        return santas

    def left_to_go(self):
        return {u: self.still_deserves(u) for u in self.participants}
    
    def still_deserves(self, uid):
        p = self.participants[uid]
        DESERVES_IN_TOTAL = {'0': 1, '1': 1, '2': 2}
        return DESERVES_IN_TOTAL[p.group] - len(self.presents[uid])
    
    def display(self):
        for u, lst in self.presents.items():
            for santa in lst:
                print santa.name, '\t', self.participants[u].name

        print "Presents per Santa"
        pprint(dict(Counter(chain(*self.presents.values()))))


if __name__ == "__main__":
    ss = SecretSanta(XMAS_FILE)
    ss.allocate()
    ss.display()