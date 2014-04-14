def translate(q):
    q=q.split()
    orSegment = []
    for qsegment in q:
        orSegment.append({'keyword':str(qsegment)})
    return {'$or':orSegment}


def interpreter(sq,isApprox):

    tag = None
    mark = ['minutes','minutes']
    for m in mark:
        if m in sq: 
            tag = m
            break
    flags = {}
    match_query = None
	
    if tag!= None:

        flags['vicinity']=True

        sq = sq.split(tag)
        sq1=sq[0].split()
        sq2=sq[1].split()

        distance_measure = sq1[len(sq1)-1]
        distance_unit = tag
        mq = ''
        del sq1[-1]
        for i in sq1:
           mq = mq + ' ' + i
    
    else:
        flags['vicinity'] = False
        mq = sq
        distance_measure = None
        distance_unit = None
    
    match_query = translate(mq)  
    if isApprox:
        flags['approximate']=1
    else:
        flags['exact']=1
	
    vicinity_param = {"distance-measure":distance_measure,"distance-unit":distance_unit} 

    return match_query,flags,vicinity_param,mq

