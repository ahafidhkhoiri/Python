import json
from rts.rest import R2RestClient
import config
import pyodbc
import queries
import uuid
import xml.etree.ElementTree as ET
import requests


def setUp(self):
    # DNRAPI General Config
    self.restDNRAPI = R2RestClient(config.DNRAPI_URL)
    self.headers = config.DNRAPI_HEADERS

    # RCS General Config
    self.restRcs = R2RestClient(config.RCS_URL)
    self.rcsHeaders = config.RCS_AUTH
    self.machineName = config.RCS_MACHINE


def parseOrionResponse(content):
    resp_dict = {}
    for x in content.strip().split('\r\n'):
        resp_dict[x.split('=')[0]] = x.split('=')[1]
    return resp_dict


def verifyJsonResponse200(self, response):
    self.assertEqual(response.status_code, 200)
    # Parse the response body and make sure the status is 200
    self.assertEqual(int(json.loads(response.content)["STATUS"]), 200)


def extractValue(parsed_response, pack, key):
    for x in parsed_response[0]:
        if x.attrib['name'] == pack:
            for y in x[0]:
                if y.attrib['name'] == key:
                    return y.text


def dnsSetingsRCS(self):
    route = self.machineName
    responseRCS = self.restRcs.get(route, headers=self.rcsHeaders)
    responses = responseRCS.content
    responses = json.loads(responses)
    rsp = (responses['orion']['DNRAPI_DISABLED']).encode("ascii")
    respons = eval(rsp.title())
    return respons


def antaresDNRS(loginAlias):
    conn = pyodbc.connect(config._default_db_conn_string)
    result = []
    if conn:
        query = """\
           Hidden
            """.format(loginAlias)

        conn.autocommit = 'True'
        cursor = conn.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        del cursor
        conn.close()
        for row in rows:
            modified_row = []
            for element in row:
                element_ascii = (str(element)).encode('ascii')
                modified_row.append(element_ascii)
            result.append(modified_row)
        return result


def getUfkAccount(loginAlias):
    conn = pyodbc.connect(config._default_db_conn_string)
    ufkAccount = 0
    if conn:
        query = """\
        Hidden')""".format(loginAlias)

        conn.autocommit = 'True'
        cursor = conn.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        del cursor
        conn.close()

        ufkAccount = (rows[0][0]).encode("ascii")
        return ufkAccount


def getUfkUser(self):
    conn = pyodbc.connect(config._default_db_conn_string)
    ufkUser = 0
    if conn:
        query = """\
            Hidden'{0}'
            """.format(config.ORION_NONSSO_USER_EMAIL)

        conn.autocommit = 'True'
        cursor = conn.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        del cursor
        conn.close()

        ufkUser = (rows[0][0]).encode("ascii")
        return ufkUser


def checkUserTag(userEmail):
    conn = pyodbc.connect(config._default_db_conn_string)
    query = queries.getQueryRelationUserTag(userEmail)
    if conn:
        conn.autocommit = 'True'
        cursor = conn.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        del cursor
        conn.close()
        return rows


def getR2UserGuid(self):
    conn = pyodbc.connect(config._default_db_conn_string)
    query = queries.geQuerytR2UserGuid(config.ORION_NONSSO_USER_EMAIL)
    if conn:
        conn.autocommit = 'True'
        cursor = conn.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        del cursor
        conn.close()
        result = "{" + (str(rows[0][0])).encode("utf-8") + "}"
        return result


def unAssignUserFromTag(self):
    row = checkUserTag(config.ORION_NONSSO_USER_EMAIL)
    if (len(row)) > 0:
        ufkTag = row[0][0]
        ufkUser = row[0][1]
        route = '/hidden/' + \
                ufkTag.encode("utf-8") + '/users'
        body = [ufkUser.encode("utf-8")]
        responses = self.restDNRAPI.delete(route, headers=self.headers,
                                           data=json.dumps(body))

        if responses.status_code == 200:
            print 'Unset {0} from {1} success'.format(ufkUser, ufkTag)
        else:
            print 'No tag found from this user'


def createTAG(self):
    ufkAccount = getUfkAccount(config.ORION_NONSSO_USER_EMAIL)
    ufkTag = 'tag:' + str(uuid.uuid4())
    groupDisplayName = 'pythonTag :' + config.RAND_UFK_TAG

    route = '/hidden'
    body = {
        'ufkTag': ufkTag,
        'ufkAccount': ufkAccount,
        'groupDisplayName': groupDisplayName
    }

    response = self.restDNRAPI.post(
        route, headers=self.headers, data=json.dumps(body))
    ufkTag = (response.json()['ufkTag']).encode("ascii")
    return ufkTag


def assignTagtoUser(self, ufkTag):
    ufkUser = getUfkUser(self)
    route = '/hidden/' + ufkTag.encode("utf-8") + '/users'
    body = [ufkUser]

    self.restDNRAPI.post(route, headers=self.headers, data=json.dumps(body))


def changeTemplateSelection(self, ufkTag):
    ufkTemplate = '__TAG:' + ufkTag
    dnrs = InvitationDnrs(self, '')
    ufkDnrs = []
    for dnrs_ in dnrs:
        if filter(lambda x: '100' in x, dnrs_):
            ufkDnrs.append(dnrs_[2])
            if len(ufkDnrs) > 1:
                break
    strUfkdnrs = ','.join("'{0}'".format(x) for x in ufkDnrs)
    discUrn = ufkDnrsDiscUrn(strUfkdnrs)

    # now we have availabe dnr so let's make that availabe dnr into primary
    # and secondary

    url = config.DNRAPI_URL + '/hidden/' + ufkTemplate + '/items'
    body = [{
        'discUrn': discUrn[0],
        'selection': 'Primary'
        },
        {
            'discUrn': discUrn[1],
            'selection': 'Secondary'
          }]

    r = requests.patch(url, data=json.dumps(body), headers=self.headers)
    if r.status_code == 200:
        print 'TAG Updated'
    else:
        print 'Failed to update TAG'


def ufkDnrsDiscUrn(strUfkDnrs):
    conn = pyodbc.connect(config._default_db_conn_string)
    tmpDiscUrn = []
    discUrn = []
    if conn:
        query = """\
            hidden ({0})""".format(strUfkDnrs)
        conn.autocommit = 'True'
        cursor = conn.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        del cursor
        conn.close()
        for row in rows:
            modified_row = []
            for element in row:
                element_ascii = (str(element)).encode('ascii')
                modified_row.append(element_ascii)
            tmpDiscUrn.append(modified_row)
        for val in tmpDiscUrn:
            for a in val:
                discUrn.append(a)
        return discUrn


def InvitationDnrs(self, ufkUser):
    if not ufkUser:
        ufkUser = ''

    _primary = []
    asciiConvert = []
    _secondary = []
    _selected = []
    _avalaibe = []
    dnrsjSONResponses = []
    ufkAccount = getUfkAccount(config.ORION_NONSSO_USER_EMAIL)
    route = 'hidden?account={0}&clearCache=true&User={1}'.format(
        ufkAccount, ufkUser)
    response = self.restDNRAPI.get(route, headers=self.headers)
    jsonContents = json.loads(response.content)

    countSelected = len(jsonContents['selected'])
    countAvailable = len(jsonContents['available'])
    countSecondary = jsonContents['secondary']

    # Populating All Primary Number From Json into one List
    _primary.append(jsonContents['primary']['dnrE164DisplayName'])
    _primary.append(jsonContents['primary']['dnrE164DisplayNumber'])
    _primary.append(jsonContents['primary']['ufkDnr'])
    _primary.append("110")
    _avalaibe.append(jsonContents['primary']['dnrE164DisplayName'])
    _avalaibe.append(jsonContents['primary']['dnrE164DisplayNumber'])
    _avalaibe.append(jsonContents['primary']['ufkDnr'])
    _avalaibe.append("100")

    # Populating All Secondary Number From Json into one List
    if countSecondary is not None:
        _secondary.append(jsonContents['secondary']['dnrE164DisplayName'])
        _secondary.append(jsonContents['secondary']['dnrE164DisplayNumber'])
        _secondary.append(jsonContents['secondary']['ufkDnr'])
        _secondary.append("110")
        _avalaibe.append(jsonContents['secondary']['dnrE164DisplayName'])
        _avalaibe.append(jsonContents['secondary']['dnrE164DisplayNumber'])
        _avalaibe.append(jsonContents['secondary']['ufkDnr'])
        _avalaibe.append("100")
    else:
        pass

    # Populating All Selected Number From Json into One List
    if countSelected != 0:
        # process selected dnrs
        a = 0
        while (a < countSelected):
            _selected.append(jsonContents['selected'][a]['dnrE164DisplayName'])
            _selected.append(
                jsonContents['selected'][a]['dnrE164DisplayNumber'])
            _selected.append(jsonContents['selected'][a]['ufkDnr'])
            _selected.append("120")
            _avalaibe.append(jsonContents['selected'][a]['dnrE164DisplayName'])
            _avalaibe.append(
                jsonContents['selected'][a]['dnrE164DisplayNumber'])
            _avalaibe.append(jsonContents['selected'][a]['ufkDnr'])
            _avalaibe.append("100")
            a += 1
    else:
        pass

    # Populating All Available Number From Json into One List
    if countAvailable != 0:
        # process selected dnrs
        a = 0
        while (a < countAvailable):
            _avalaibe.append(
                jsonContents['available'][a]['dnrE164DisplayName'])
            _avalaibe.append(
                jsonContents['available'][a]['dnrE164DisplayNumber'])
            _avalaibe.append(jsonContents['available'][a]['ufkDnr'])
            _avalaibe.append("100")
            a += 1

    else:
        pass

    join = _primary + _secondary + _selected + _avalaibe
    # converting to ascii
    for element in join:
        join = (str(element)).encode('ascii')
        asciiConvert.append(join)
    dnrsjSONResponses.extend(asciiConvert)
    i = 0
    dnrs = []
    inner = []
    for item in dnrsjSONResponses:
        inner.append(item)
        i += 1
        if i == 4:
            dnrs.append(inner)
            i = 0
            inner = []
    return dnrs


def unAssignAccountFromTemplate(ufkAccount):
    ufkacc = ufkAccount
    conn = pyodbc.connect(config._default_db_conn_string)
    if conn:
        query = """\
        Hidden'{0}'""".format(ufkacc)

        conn.autocommit = 'True'
        cursor = conn.execute(query)
        cursor.close()
        del cursor
        conn.close()
    else:
        print "unassignDnrgTemplateToAccount - FAILED CONNECT TO DB"


def callOrion(route, identifier):
    rest = R2RestClient(config.ORION_URL)
    response = rest.get(route)
    if identifier == "OLT":
        f = open("tmp/temp.xml", "w")
        for x in response:
            f.write(x)
        f.close()
    elif identifier == "ANDROID":
        f = open("tmp/temp.json", "w")
        for x in response:
            f.write(x)
        f.close()
    elif identifier == "IPHONE":
        f = open("tmp/tmpIphone.txt", "w")
        for x in response:
            f.write(x)
        f.close()


def parsingXML_OLT(countDnrs):
    countDNR = countDnrs
    listDisplayName = []
    listDisplayNumber = []
    listUfkDnr = []
    listDnrgType = []
    dnrsXmlValue = []
    tree = ET.parse('tmp/temp.xml')
    root = tree.getroot()
    for x in root[0]:
        if x.attrib['name'] == 'CC':
            for y in x[0]:
                if y.attrib['name'] == 'CONF[1]':
                    for z in y[0]:
                        pop = 1
                        while pop <= countDNR:
                            if z.attrib['name'] == 'DI[{0}]'.format(pop):
                                for a in z[0]:
                                    if a.attrib['name'] == 'DISPLAY_NAME':
                                        dnrgName = a.text
                                        listDisplayName.append(dnrgName)
                                    elif a.attrib['name'] == 'DISPLAY_NUMBER':
                                        dnrDisplayNumber = a.text
                                        listDisplayNumber.append(
                                            dnrDisplayNumber)
                                    elif a.attrib['name'] == 'UFK_DIALIN':
                                        dnrUfkDnr = a.text
                                        listUfkDnr.append(dnrUfkDnr)
                                    elif a.attrib['name'] == 'DNRG_TYPE_ID':
                                        dnrgType = a.text
                                        listDnrgType.append(dnrgType)
                            pop += 1

                    leng = len(listDisplayName)
                    counter = 0
                    while counter < leng:
                        innerItem = []
                        innerItem.append(listDisplayName[counter])
                        innerItem.append(listDisplayNumber[counter])
                        innerItem.append(listUfkDnr[counter])
                        innerItem.append(listDnrgType[counter])
                        dnrsXmlValue.append(innerItem)
                        counter += 1

                    dnrsXmlValue.sort()
                    return dnrsXmlValue


def parsingJson_Android(self):
    asciiConvert = []
    content = ""
    data = []
    _dnrs = []
    OrionDnrsResponses = []
    with open('tmp/temp.json') as json_file:
        content = json.load(json_file)

    counter = content['DNRG_COUNT']

    a = 0
    b = 0
    while a < counter:
        dnr = content['DNRG_LIST'][a]['DNR_LIST']
        inCounter = content['DNRG_LIST'][a]['DNR_COUNT']
        dnrgTypeID = content['DNRG_LIST'][a]['DNRG_TYPE_ID']
        while b < inCounter:
            data.append(dnr[b]['DNR_DISPLAY_NAME'])
            data.append(dnr[b]['DNR_DISPLAY_NUMBER'])
            data.append(dnr[b]['UFK_DNR'])
            data.append(dnrgTypeID)
            b += 1
        b = 0
        a += 1
    # converting to ascii
    for element in data:
        data = (str(element)).encode('ascii')
        asciiConvert.append(data)
    _dnrs.extend(asciiConvert)

    i = 0
    inner = []
    for item in _dnrs:
        inner.append(item)
        i += 1
        if i == 4:
            OrionDnrsResponses.append(inner)
            i = 0
            inner = []
    OrionDnrsResponses.sort()
    return OrionDnrsResponses


def parsingTxt_iPhone(self):
    with open("tmp/tmpIphone.txt") as file:
        lines = [i.strip() for i in file]
        find = 'CC.CONF[1]._DIALIN_COUNT='
        for temp in lines:
            if find in temp:
                countDnr = (int(temp[25:]) + 1)

    dnrs = []
    a = 0
    while a < countDnr:
        for tryy in lines:
            if a <= 9:
                if 'CC.CONF[1].DI[{0}].DISPLAY_NAME='.format(a) in tryy:
                    dnrs.append(tryy[30:])
                if 'CC.CONF[1].DI[{0}].DISPLAY_NUMBER='.format(a) in tryy:
                    dnrs.append(tryy[32:])
                if 'CC.CONF[1].DI[{0}].DNRG_TYPE_ID='.format(a) in tryy:
                    dnrs.append(tryy[30:])
            elif a >= 10 and a < 100:
                if 'CC.CONF[1].DI[{0}].DISPLAY_NAME='.format(a) in tryy:
                    dnrs.append(tryy[31:])
                if 'CC.CONF[1].DI[{0}].DISPLAY_NUMBER='.format(a) in tryy:
                    dnrs.append(tryy[33:])
                if 'CC.CONF[1].DI[{0}].DNRG_TYPE_ID='.format(a) in tryy:
                    dnrs.append(tryy[31:])
            else:
                if 'CC.CONF[1].DI[{0}].DISPLAY_NAME='.format(a) in tryy:
                    dnrs.append(tryy[32:])
                if 'CC.CONF[1].DI[{0}].DISPLAY_NUMBER='.format(a) in tryy:
                    dnrs.append(tryy[34:])
                if 'CC.CONF[1].DI[{0}].DNRG_TYPE_ID='.format(a) in tryy:
                    dnrs.append(tryy[32:])

        a += 1

    a = 0
    tmp = []
    inner = []
    i = 0
    for x in dnrs:
        inner.append(x)
        i += 1
        if i == 3:
            tmp.append(inner)
            i = 0
            inner = []

    b = 0
    countLeng = len(tmp)
    while b < countLeng:
        dnrgType = tmp[b][0]
        del tmp[b][0]
        tmp[b].append(dnrgType)
        b += 1
    dnrsIphoneResponses = sorted(tmp)
    return dnrsIphoneResponses
