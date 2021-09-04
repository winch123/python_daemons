# 2019.05.31 11:29:47 +04
# Embedded file name: /var/www/vhosts/menuforme.online/httpdocs/special/py/wu.py


def minidomTag(name, text = None, attributes = None, cdata = False):
    from xml.dom import minidom
    doc = minidom.Document()
    if name is None:
        return doc
    else:
        tag = doc.createElement(name)
        if text is not None:
            if cdata:
                tag.appendChild(doc.createCDATASection(text))
            else:
                tag.appendChild(doc.createTextNode(text))
        if attributes is not None:
            for k, v in attributes.items():
                if v is not None:
                    tag.setAttribute(k, str(v))

        return tag


def json_dt(obj):
    from datetime import datetime, date
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    from decimal import Decimal
    if isinstance(obj, Decimal):
        return float(obj)


def pretty(obj):
    import json
    return json.dumps(obj, sort_keys=True, indent=4, ensure_ascii=False, default=json_dt)

import logging

def ConfLog(InFile, level=logging.WARNING):
    import os, inspect
    if InFile:
        BaseFullName = inspect.stack()[1][1]
        ppp = os.path.abspath(os.curdir) + '/../../../menuforme_logs/' + os.path.splitext(os.path.basename(BaseFullName))[0] + '.log'
    else:
        ppp = None

    logging.basicConfig(format=u'\x1b[95m %(levelname)s %(filename)s[Line:%(lineno)d]# %(funcName)s  [%(asctime)s] \x1b[0m \n%(message)s \n', filename=ppp, level=level)



# okay decompyling wu.pyc 
# decompiled 1 files: 1 okay, 0 failed, 0 verify failed
# 2019.05.31 11:29:47 +04
