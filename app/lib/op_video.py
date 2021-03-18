from .. import db

def add_simple(modelclass,selectdata,inputdata):
    cy = False
    if selectdata:
        if isinstance(selectdata,list):
            selectdata = selectdata[0]
        cy = modelclass.query.filter_by(id=int(selectdata)).first()
    
    if inputdata:
        cid_text = inputdata.upper()
        c_cate = modelclass.query.filter_by(name=cid_text).first()
        if c_cate:
            cy = c_cate
        else:
            cli = modelclass(

                name2up = cid_text

            )
            db.session.add(cli)
            cy = cli

    return cy

def add_multiple(modelclass,selectdata,texts):
    modellist = []
    if texts:
        aid_text_strip = texts.strip(';')
        aid_arr = aid_text_strip.split(';')
        for aid_name  in aid_arr:
            a_obj = modelclass.query.filter_by(name=aid_name).first()
            if a_obj:
                for obj_id in selectdata:
                    if a_obj.id == int(obj_id):
                        break
                else:
                    modellist.append(a_obj)

            else:
                act = modelclass(
                    name = aid_name,
                    sortnum = 99
                )
                db.session.add(act)
                modellist.append(act)

    for actor in selectdata:
            a = modelclass.query.filter_by(id = int(actor)).first()
            if a:

                modellist.append(a)
    return modellist
