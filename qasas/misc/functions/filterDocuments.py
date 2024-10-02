def FILTER_DOCUMENT(docdirQuery, form):
    if form['type']:
        docdirQuery = docdirQuery.filter(
            Q(document__type__name=form['type'])
        )
    if form['is_public'] != None:
        docdirQuery = docdirQuery.filter(
            Q(is_public=form['is_public'])
        )
    for attr in form['attributes']:
        docdirQuery = docdirQuery.filter(
            Q(
                document__attributes__key=attr['key'],
                document__attributes__value=attr['value']
            )
        )
    for key in form['keywords']:
        docdirQuery = docdirQuery.filter(
            Q(document__keywords__keyword=key)
        )
    for tag in form['tags']:
        docdirQuery = docdirQuery.filter(
            Q(document__tags__tag__name=tag)
        )
    return docdirQuery
