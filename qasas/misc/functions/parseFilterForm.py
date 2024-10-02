def PARSE_FILTER_FORM(POST):
    form = {}
    form['type'] = POST['type'] if 'type' in POST else None
    form['is_public'] = POST['is_public'] if 'is_public' in POST else None
    form['sort_by'] = POST['sort_by'] if 'sort_by' in POST else None
    form['ascending'] = POST['ascending'] if 'ascending' in POST else None

    form['is_public'] = True if form['is_public'] == 'true' else False if form['is_public'] == 'false' else None
    form['sort_by'] = None if form['sort_by'] == 'null' else form['sort_by']
    form['ascending'] = True if form['ascending'] == 'true' else False

    form['attributes'] = []
    form['keywords'] = []
    form['tags'] = []

    for field in POST:
        if (field.startswith('ak_')):
            form['attributes'].append({
                'key': POST['ak_' + field[3:]],
                'value': POST['av_' + field[3:]],
            })
        if (field.startswith('k_')):
            form['keywords'].append(POST['k_' + field[2:]])
        if (field.startswith('t_')):
            form['tags'].append(POST['t_' + field[2:]])

    return form
