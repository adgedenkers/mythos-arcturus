#!/usr/bin/env python3
"""Western Tropical Ephemeris Engine v2 - Placidus, full precision."""
import swisseph as swe
import json, sys, copy, math

PLANETS = {'Sun': swe.SUN, 'Moon': swe.MOON, 'Mercury': swe.MERCURY,
    'Venus': swe.VENUS, 'Mars': swe.MARS, 'Jupiter': swe.JUPITER,
    'Saturn': swe.SATURN, 'Uranus': swe.URANUS, 'Neptune': swe.NEPTUNE,
    'Pluto': swe.PLUTO, 'North Node': swe.TRUE_NODE, 'Mean Node': swe.MEAN_NODE}
LILITH_ID = swe.MEAN_APOG
ASTEROIDS = {'Ceres': swe.AST_OFFSET+1, 'Pallas': swe.AST_OFFSET+2,
    'Juno': swe.AST_OFFSET+3, 'Vesta': swe.AST_OFFSET+4, 'Chiron': 15}
SIGNS = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo',
    'Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
SIGN_G = {s: chr(0x2648+i) for i,s in enumerate(SIGNS)}
PLANET_G = {'Sun':'\u2609','Moon':'\u263d','Mercury':'\u263f','Venus':'\u2640',
    'Mars':'\u2642','Jupiter':'\u2643','Saturn':'\u2644','Uranus':'\u2645',
    'Neptune':'\u2646','Pluto':'\u2647','North Node':'\u260a','South Node':'\u260b',
    'Chiron':'\u26b7','Ceres':'\u26b3','Pallas':'\u26b4','Juno':'\u26b5',
    'Vesta':'\u26b6','Lilith':'\u26b8'}
ELEMENTS = {'Aries':'Fire','Taurus':'Earth','Gemini':'Air','Cancer':'Water',
    'Leo':'Fire','Virgo':'Earth','Libra':'Air','Scorpio':'Water',
    'Sagittarius':'Fire','Capricorn':'Earth','Aquarius':'Air','Pisces':'Water'}
MODALITIES = {'Aries':'Cardinal','Taurus':'Fixed','Gemini':'Mutable',
    'Cancer':'Cardinal','Leo':'Fixed','Virgo':'Mutable','Libra':'Cardinal',
    'Scorpio':'Fixed','Sagittarius':'Mutable','Capricorn':'Cardinal',
    'Aquarius':'Fixed','Pisces':'Mutable'}
TRAD_RULERS = {'Aries':'Mars','Taurus':'Venus','Gemini':'Mercury','Cancer':'Moon',
    'Leo':'Sun','Virgo':'Mercury','Libra':'Venus','Scorpio':'Mars',
    'Sagittarius':'Jupiter','Capricorn':'Saturn','Aquarius':'Saturn','Pisces':'Jupiter'}
MOD_RULERS = dict(TRAD_RULERS)
MOD_RULERS.update({'Scorpio':'Pluto','Aquarius':'Uranus','Pisces':'Neptune'})
DIGNITIES = {
    'Sun':{'dom':'Leo','exa':'Aries','det':'Aquarius','fal':'Libra'},
    'Moon':{'dom':'Cancer','exa':'Taurus','det':'Capricorn','fal':'Scorpio'},
    'Mercury':{'dom':['Gemini','Virgo'],'exa':'Virgo','det':['Sagittarius','Pisces'],'fal':'Pisces'},
    'Venus':{'dom':['Taurus','Libra'],'exa':'Pisces','det':['Aries','Scorpio'],'fal':'Virgo'},
    'Mars':{'dom':['Aries','Scorpio'],'exa':'Capricorn','det':['Taurus','Libra'],'fal':'Cancer'},
    'Jupiter':{'dom':['Sagittarius','Pisces'],'exa':'Cancer','det':['Gemini','Virgo'],'fal':'Capricorn'},
    'Saturn':{'dom':['Capricorn','Aquarius'],'exa':'Libra','det':['Cancer','Leo'],'fal':'Aries'}}
DECAN_RULERS = {'Aries':['Mars','Sun','Venus'],'Taurus':['Mercury','Moon','Saturn'],
    'Gemini':['Jupiter','Mars','Sun'],'Cancer':['Venus','Mercury','Moon'],
    'Leo':['Saturn','Jupiter','Mars'],'Virgo':['Sun','Venus','Mercury'],
    'Libra':['Moon','Saturn','Jupiter'],'Scorpio':['Mars','Sun','Venus'],
    'Sagittarius':['Mercury','Moon','Saturn'],'Capricorn':['Jupiter','Mars','Sun'],
    'Aquarius':['Venus','Mercury','Moon'],'Pisces':['Saturn','Jupiter','Mars']}
FIXED_STARS_J2000 = {
    'Algol':{'lon':56.17,'mag':2.12,'nat':'Saturn-Jupiter','m':'Intensity, transformation'},
    'Aldebaran':{'lon':69.87,'mag':0.85,'nat':'Mars','m':'Royal star of East, integrity'},
    'Rigel':{'lon':78.63,'mag':0.12,'nat':'Jupiter-Saturn','m':'Teaching, ambition'},
    'Sirius':{'lon':104.07,'mag':-1.46,'nat':'Jupiter-Mars','m':'Brilliance, fame'},
    'Regulus':{'lon':149.83,'mag':1.35,'nat':'Jupiter-Mars','m':'Royal star, glory'},
    'Spica':{'lon':203.84,'mag':0.97,'nat':'Venus-Mars','m':'Brilliance, gifts'},
    'Arcturus':{'lon':214.07,'mag':-0.04,'nat':'Mars-Jupiter','m':'Pathfinding, navigation'},
    'Antares':{'lon':249.79,'mag':0.96,'nat':'Mars-Jupiter','m':'Royal star of West'},
    'Vega':{'lon':279.23,'mag':0.03,'nat':'Venus-Mercury','m':'Charisma, art'},
    'Fomalhaut':{'lon':333.86,'mag':1.16,'nat':'Venus-Mercury','m':'Royal star of South'},
    'Betelgeuse':{'lon':88.79,'mag':0.50,'nat':'Mars-Mercury','m':'Martial honors'},
    'Procyon':{'lon':115.95,'mag':0.34,'nat':'Mercury-Mars','m':'Sudden rise and fall'},
    'Altair':{'lon':301.87,'mag':0.77,'nat':'Mars-Jupiter','m':'Boldness'},
    'Deneb Algedi':{'lon':326.50,'mag':2.87,'nat':'Saturn-Jupiter','m':'Justice, law'},
    'Achernar':{'lon':15.28,'mag':0.46,'nat':'Jupiter','m':'Royal honors'},
    'Vindemiatrix':{'lon':189.79,'mag':2.83,'nat':'Saturn-Mercury','m':'Loss'},
    'Scheat':{'lon':349.36,'mag':2.42,'nat':'Mars-Mercury','m':'Extreme intellect'}}
ASPECT_DEFS = {
    'conjunction':{'ang':0,'orb':8,'sym':'conj','major':True},
    'opposition':{'ang':180,'orb':8,'sym':'opp','major':True},
    'trine':{'ang':120,'orb':8,'sym':'tri','major':True},
    'square':{'ang':90,'orb':7,'sym':'sq','major':True},
    'sextile':{'ang':60,'orb':6,'sym':'sxt','major':True},
    'quincunx':{'ang':150,'orb':3,'sym':'qnx'},
    'semisquare':{'ang':45,'orb':2,'sym':'ssq'},
    'sesquiquadrate':{'ang':135,'orb':2,'sym':'ses'},
    'semisextile':{'ang':30,'orb':2,'sym':'ssx'},
    'quintile':{'ang':72,'orb':2,'sym':'Q'},
    'biquintile':{'ang':144,'orb':2,'sym':'bQ'}}
P_JOYS = {'Mercury':1,'Moon':3,'Venus':5,'Mars':6,'Sun':9,'Jupiter':11,'Saturn':12}

def lon_to_sign(lon):
    idx = int(lon/30)%12; return SIGNS[idx], lon%30
def fmt_pos(lon):
    s,dg = lon_to_sign(lon); d=int(dg); r=(dg-d)*60; m=int(r); sc=int((r-m)*60)
    return str(d)+"d"+str(m).zfill(2)+"m"+s
def fmt_full(lon):
    s,dg = lon_to_sign(lon); d=int(dg); r=(dg-d)*60; m=int(r); sc=int((r-m)*60)
    return str(d)+" deg "+str(m).zfill(2)+"' "+str(sc).zfill(2)+" "+s
def get_decan(sign, deg):
    n=min(int(deg/10)+1,3); return {'decan':n,'ruler':DECAN_RULERS[sign][n-1]}
def get_dignity(planet, sign):
    if planet not in DIGNITIES: return None
    d=DIGNITIES[planet]
    for st,key in [('domicile','dom'),('exaltation','exa'),('detriment','det'),('fall','fal')]:
        v=d[key]
        if isinstance(v,list):
            if sign in v: return st
        elif sign==v: return st
    return 'peregrine'
def ang_dist(a,b):
    d=abs(a-b)%360; return 360-d if d>180 else d
def calc_aspect(l1, l2, s1=None, s2=None):
    diff = ang_dist(l1, l2)
    for nm, a in ASPECT_DEFS.items():
        orb = abs(diff - a['ang'])
        if orb <= a['orb']:
            app = None
            if s1 is not None and s2 is not None: app = orb > 0.01
            return {'aspect':nm,'symbol':a['sym'],'angle':a['ang'],'orb':round(orb,4),'exact':orb<1.0,'tight':orb<2.0,'applying':app,'major':a.get('major',False)}
    return None
def det_sect(sun_lon, asc_lon, mc_lon):
    d=(sun_lon-asc_lon)%360
    return 'diurnal' if 180<d<=360 or d==0 else 'nocturnal'
def sect_status(planet, sect):
    if planet in ['Sun','Jupiter','Saturn']:
        return 'of sect' if sect=='diurnal' else 'contrary to sect'
    if planet in ['Moon','Venus','Mars']:
        return 'of sect' if sect=='nocturnal' else 'contrary to sect'
    return 'neutral'
def precess(lon_j2000, year):
    return (lon_j2000 + 50.29/3600*(year-2000))%360

# --- Core Calculations ---
def calc_planets(jd, flags=0):
    swe.set_ephe_path(None)
    results = {}
    for name, bid in PLANETS.items():
        pos = swe.calc_ut(jd, bid, flags)
        lon,lat,dist,spd = pos[0][0],pos[0][1],pos[0][2],pos[0][3]
        sign, deg = lon_to_sign(lon)
        results[name] = {
            'longitude':lon,'latitude':lat,'distance':dist,'speed':spd,
            'sign':sign,'sign_glyph':SIGN_G.get(sign,''),'degree_in_sign':deg,
            'formatted':fmt_full(lon),'retrograde':spd<0,
            'element':ELEMENTS[sign],'modality':MODALITIES[sign],
            'decan':get_decan(sign,deg),'glyph':PLANET_G.get(name,'')}
        dg = get_dignity(name, sign)
        if dg: results[name]['dignity'] = dg
        results[name]['trad_ruler'] = TRAD_RULERS[sign]
        results[name]['mod_ruler'] = MOD_RULERS[sign]
    # South Node
    if 'North Node' in results:
        nn=results['North Node']['longitude']; sn=(nn+180)%360
        sign,deg=lon_to_sign(sn)
        results['South Node']={'longitude':sn,'sign':sign,'degree_in_sign':deg,
            'formatted':fmt_full(sn),'retrograde':True,'element':ELEMENTS[sign],
            'modality':MODALITIES[sign],'glyph':PLANET_G.get('South Node','')}
    # Lilith
    try:
        pos=swe.calc_ut(jd,LILITH_ID,flags); lon=pos[0][0]; sign,deg=lon_to_sign(lon)
        results['Lilith']={'longitude':lon,'sign':sign,'degree_in_sign':deg,
            'formatted':fmt_full(lon),'retrograde':pos[0][3]<0,'speed':pos[0][3],
            'element':ELEMENTS[sign],'modality':MODALITIES[sign],'glyph':PLANET_G.get('Lilith','')}
    except: results['Lilith']={'note':'calc failed'}
    # Asteroids
    for name, bid in ASTEROIDS.items():
        try:
            pos=swe.calc_ut(jd,bid,flags); lon=pos[0][0]; sign,deg=lon_to_sign(lon)
            results[name]={'longitude':lon,'sign':sign,'degree_in_sign':deg,
                'formatted':fmt_full(lon),'retrograde':pos[0][3]<0,'speed':pos[0][3],
                'element':ELEMENTS[sign],'modality':MODALITIES[sign],'glyph':PLANET_G.get(name,'')}
        except: results[name]={'note':'needs SE data files'}
    return results

def calc_fixed_stars(jd, year):
    stars = {}
    for name, data in FIXED_STARS_J2000.items():
        plon = precess(data["lon"], year)
        sign, deg = lon_to_sign(plon)
        stars[name] = {"longitude":plon,"sign":sign,"degree_in_sign":deg,"formatted":fmt_full(plon),"magnitude":data["mag"],"nature":data["nat"],"meaning":data["m"]}
    return stars

def find_star_conj(planets, stars, orb=1.5):
    conj = []
    for pn, pd in planets.items():
        if 'longitude' not in pd: continue
        for sn, sd in stars.items():
            d = ang_dist(pd['longitude'], sd['longitude'])
            if d <= orb:
                conj.append({'planet':pn,'star':sn,'orb':round(d,4),
                    'nature':sd['nature'],'meaning':sd['meaning']})
    return sorted(conj, key=lambda x: x['orb'])

def calc_houses(jd, lat, lon, system='P'):
    swe.set_ephe_path(None)
    hd = swe.houses(jd, lat, lon, system.encode())
    cusps, angles = hd[0], hd[1]
    names = {'P':'Placidus','W':'Whole Sign','K':'Koch','E':'Equal'}
    result = {'system':names.get(system,system),'cusps':{},'angles':{},'_raw':list(cusps)}
    for label, idx in [('ASC',0),('MC',1)]:
        v = angles[idx]; sign,deg = lon_to_sign(v)
        result['angles'][label] = {'longitude':v,'formatted':fmt_full(v),'sign':sign,'degree_in_sign':deg}
    dsc=(angles[0]+180)%360; ic=(angles[1]+180)%360
    result['angles']['DSC'] = {'longitude':dsc,'formatted':fmt_full(dsc),'sign':lon_to_sign(dsc)[0]}
    result['angles']['IC'] = {'longitude':ic,'formatted':fmt_full(ic),'sign':lon_to_sign(ic)[0]}
    if len(angles)>3:
        result['angles']['Vertex'] = {'longitude':angles[3],'formatted':fmt_full(angles[3])}
    for i, cusp in enumerate(cusps):
        sign,deg = lon_to_sign(cusp)
        result['cusps']['House '+str(i+1)] = {'longitude':cusp,'formatted':fmt_full(cusp),'sign':sign,'degree_in_sign':deg}
    return result

def assign_houses(planets, houses):
    """Assign planets to houses using FULL PRECISION cusps. Call on deepcopy only."""
    cusps = houses['_raw']
    for name, data in planets.items():
        if 'longitude' not in data: continue
        lon = data['longitude']
        house = 12
        for i in range(12):
            ni = (i+1)%12
            start, end = cusps[i], cusps[ni]
            if start < end:
                if start <= lon < end: house = i+1; break
            else:
                if lon >= start or lon < end: house = i+1; break
        data['house'] = house
        for aname in ['ASC','MC','DSC','IC']:
            alon = houses['angles'][aname]['longitude']
            if ang_dist(lon, alon) <= 5.0:
                data['angular'] = aname
                data['angular_orb'] = round(ang_dist(lon, alon), 4)
                break
        if name in P_JOYS and house == P_JOYS[name]:
            data['in_joy'] = True
    return planets

def detect_intercepted(houses):
    cs = set()
    for i in range(1,13): cs.add(houses['cusps']['House '+str(i)]['sign'])
    return [s for s in SIGNS if s not in cs]

def calc_aspects(planets, include_minor=True):
    aspects = []
    bodies = ['Sun','Moon','Mercury','Venus','Mars','Jupiter','Saturn',
              'Uranus','Neptune','Pluto','North Node','Chiron','Lilith']
    names = [n for n in bodies if n in planets and 'longitude' in planets[n]]
    for i, n1 in enumerate(names):
        for n2 in names[i+1:]:
            asp = calc_aspect(planets[n1]['longitude'], planets[n2]['longitude'],
                planets[n1].get('speed'), planets[n2].get('speed'))
            if asp:
                if not include_minor and not asp.get('major',False): continue
                asp['planet1'] = n1; asp['planet2'] = n2
                aspects.append(asp)
    return sorted(aspects, key=lambda x: x['orb'])

def detect_patterns(aspects, planets):
    patterns = []
    adj = {t:{} for t in ['conjunction','square','trine','opposition','sextile','quincunx']}
    for a in aspects:
        p1,p2,t = a['planet1'],a['planet2'],a['aspect']
        if t in adj:
            adj[t].setdefault(p1,[]).append(p2)
            adj[t].setdefault(p2,[]).append(p1)
    # Grand Trine
    seen=set()
    for p1 in adj['trine']:
        for p2 in adj['trine'][p1]:
            for p3 in adj['trine'].get(p2,[]):
                if p3!=p1 and p1 in adj['trine'].get(p3,[]):
                    k=tuple(sorted([p1,p2,p3]))
                    if k not in seen:
                        seen.add(k)
                        e=planets[p1].get('element','?') if p1 in planets else '?'
                        patterns.append({'pattern':'Grand Trine','planets':list(k),'element':e})
    # T-Square
    seen=set()
    for p1 in adj['opposition']:
        for p2 in adj['opposition'][p1]:
            sq1=set(adj['square'].get(p1,[])); sq2=set(adj['square'].get(p2,[]))
            for apex in sq1&sq2:
                k=tuple(sorted([p1,p2,apex]))
                if k not in seen:
                    seen.add(k)
                    patterns.append({'pattern':'T-Square','planets':list(k),'apex':apex})
    # Yod
    seen=set()
    for p1 in adj['sextile']:
        for p2 in adj['sextile'][p1]:
            q1=set(adj['quincunx'].get(p1,[])); q2=set(adj['quincunx'].get(p2,[]))
            for apex in q1&q2:
                if apex not in (p1,p2):
                    k=tuple(sorted([p1,p2,apex]))
                    if k not in seen:
                        seen.add(k)
                        patterns.append({'pattern':'Yod','planets':list(k),'apex':apex})
    # Stellium
    sg={}
    core=['Sun','Moon','Mercury','Venus','Mars','Jupiter','Saturn','Uranus','Neptune','Pluto']
    for n in core:
        if n in planets and 'sign' in planets[n]:
            sg.setdefault(planets[n]['sign'],[]).append(n)
    for sign, group in sg.items():
        if len(group)>=3:
            patterns.append({'pattern':'Stellium','planets':group,'sign':sign})
    return patterns

def calculate_natal(year, month, day, hour, minute, lat, lon, tz_offset=0, name=None):
    """Full natal chart - Western Tropical, Placidus houses."""
    ut_hour = hour + minute/60.0 - tz_offset
    jd = swe.julday(year, month, day, ut_hour)
    planets = calc_planets(jd)
    houses = calc_houses(jd, lat, lon, 'P')
    # CRITICAL: deep copy prevents cross-contamination
    pl = copy.deepcopy(planets)
    assign_houses(pl, houses)
    aspects = calc_aspects(pl, include_minor=True)
    patterns = detect_patterns(aspects, pl)
    sect = det_sect(planets['Sun']['longitude'],
        houses['angles']['ASC']['longitude'], houses['angles']['MC']['longitude'])
    for pn, data in pl.items():
        if 'longitude' in data: data['sect'] = sect_status(pn, sect)
    intercepted = detect_intercepted(houses)
    stars = calc_fixed_stars(jd, year)
    star_conj = find_star_conj(pl, stars)
    # Lot of Fortune
    sun_l=planets['Sun']['longitude']; moon_l=planets['Moon']['longitude']
    asc_l=houses['angles']['ASC']['longitude']
    if sect=='diurnal': lof=(asc_l+moon_l-sun_l)%360
    else: lof=(asc_l+sun_l-moon_l)%360
    lof_sign,lof_deg=lon_to_sign(lof)
    # Element/modality balance
    elem={'Fire':0,'Earth':0,'Air':0,'Water':0}
    mod={'Cardinal':0,'Fixed':0,'Mutable':0}
    for p in ['Sun','Moon','Mercury','Venus','Mars','Jupiter','Saturn']:
        if p in pl and 'element' in pl[p]:
            elem[pl[p]['element']]+=1; mod[pl[p]['modality']]+=1
    asc_sign=houses['angles']['ASC']['sign']; mc_sign=houses['angles']['MC']['sign']
    elem[ELEMENTS[asc_sign]]+=1; mod[MODALITIES[asc_sign]]+=1
    elem[ELEMENTS[mc_sign]]+=1; mod[MODALITIES[mc_sign]]+=1
    # Dispositors
    disp={}
    for p in ['Sun','Moon','Mercury','Venus','Mars','Jupiter','Saturn']:
        if p in pl and 'sign' in pl[p]: disp[p]=TRAD_RULERS[pl[p]['sign']]
    return {
        'meta':{'name':name,'birth_date':f'{year}-{month:02d}-{day:02d}',
            'birth_time':f'{hour:02d}:{minute:02d}','tz':tz_offset,
            'lat':lat,'lon':lon,'jd':jd,'house_system':'Placidus'},
        'planets':pl,'houses':houses,'aspects':aspects,'patterns':patterns,
        'sect':sect,
        'fixed_stars':{'all':stars,'conjunctions':star_conj},
        'lot_of_fortune':{'longitude':lof,'sign':lof_sign,'deg':lof_deg,'formatted':fmt_full(lof)},
        'intercepted':intercepted,'dispositors':disp,
        'synthesis':{'element_balance':elem,'modality_balance':mod,
            'dominant_element':max(elem,key=elem.get),
            'dominant_modality':max(mod,key=mod.get),
            'asc_sign':asc_sign,'mc_sign':mc_sign,
            'sun_sign':planets['Sun']['sign'],'moon_sign':planets['Moon']['sign'],
            'rising':asc_sign,
            'chart_ruler_trad':TRAD_RULERS[asc_sign],
            'chart_ruler_mod':MOD_RULERS[asc_sign]}}

def calculate_transits(natal_data, ty, tm, td, th=12, tmin=0, tz=0):
    ut = th + tmin/60.0 - tz
    jd = swe.julday(ty, tm, td, ut)
    tp = calc_planets(jd)
    np_ = natal_data['planets']
    ta = []
    for tn, td_ in tp.items():
        if 'longitude' not in td_: continue
        for nn, nd in np_.items():
            if 'longitude' not in nd: continue
            asp = calc_aspect(td_['longitude'], nd['longitude'], td_.get('speed'), nd.get('speed'))
            if asp: asp['transit_planet']=tn; asp['natal_planet']=nn; ta.append(asp)
    for aname in ['ASC','MC','DSC','IC']:
        alon = natal_data['houses']['angles'][aname]['longitude']
        for tn, td_ in tp.items():
            if 'longitude' not in td_: continue
            asp = calc_aspect(td_['longitude'], alon)
            if asp: asp['transit_planet']=tn; asp['natal_point']=aname; ta.append(asp)
    return {'meta':{'date':f'{ty}-{tm:02d}-{td:02d}','jd':jd},
        'transit_planets':tp,'aspects':sorted(ta,key=lambda x:x['orb'])}

def calculate_synastry(chart_a, chart_b):
    pa, pb = chart_a['planets'], chart_b['planets']
    cross = []
    for an, ad in pa.items():
        if 'longitude' not in ad: continue
        for bn, bd in pb.items():
            if 'longitude' not in bd: continue
            asp = calc_aspect(ad['longitude'], bd['longitude'])
            if asp: asp['a_planet']=an; asp['b_planet']=bn; cross.append(asp)
    # House overlays
    oa, ob = {}, {}
    for an, ad in pa.items():
        if 'longitude' not in ad: continue
        t = {an: copy.deepcopy(ad)}
        assign_houses(t, chart_b['houses'])
        oa[an] = t[an].get('house')
    for bn, bd in pb.items():
        if 'longitude' not in bd: continue
        t = {bn: copy.deepcopy(bd)}
        assign_houses(t, chart_a['houses'])
        ob[bn] = t[bn].get('house')
    return {'meta':{'a':chart_a['meta'].get('name','A'),'b':chart_b['meta'].get('name','B')},
        'cross_aspects':sorted(cross,key=lambda x:x['orb']),
        'a_in_b_houses':oa,'b_in_a_houses':ob}

if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser(description='Western Tropical Ephemeris')
    p.add_argument('mode', choices=['natal','transit','synastry'])
    p.add_argument('--year',type=int,required=True)
    p.add_argument('--month',type=int,required=True)
    p.add_argument('--day',type=int,required=True)
    p.add_argument('--hour',type=int,default=12)
    p.add_argument('--minute',type=int,default=0)
    p.add_argument('--lat',type=float,required=True)
    p.add_argument('--lon',type=float,required=True)
    p.add_argument('--tz',type=float,default=0)
    p.add_argument('--name',type=str,default=None)
    p.add_argument('--output',type=str,default=None)
    args = p.parse_args()
    if args.mode == 'natal':
        result = calculate_natal(args.year,args.month,args.day,args.hour,args.minute,
            args.lat,args.lon,args.tz,args.name)
    else:
        print(f"Mode '{args.mode}' needs extra inputs. Use as library.",file=sys.stderr); sys.exit(1)
    out = json.dumps(result, indent=2, default=str)
    if args.output:
        with open(args.output,'w') as f: f.write(out)
        print(f'Written to {args.output}',file=sys.stderr)
    else: print(out)
