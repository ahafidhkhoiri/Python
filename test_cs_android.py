import unittest
import config
import requests
import json
import CommonTestHelper
import xml.etree.ElementTree as ET
from rts.rest import R2RestClient
from requests.packages.urllib3.exceptions import InsecureRequestWarning
try:
    from urllib.parse import urlparse
except ImportError:
    import urlparse
import time
try:
    from html.parser import HTMLParser
except ImportError:
    from HTMLParser import HTMLParser
from io import StringIO, BytesIO
import re
from io import StringIO, BytesIO
from numpy import *
import numpy as np
import os
from os import path


class fakeUrl_cs_android(unittest.TestCase):
    def setUp(self):
        # fakeUrl GeneralCOnfig
        self.restfakeUrl = R2RestClient(config.fakeUrl_URL)

        # DNRAPI General Config
        self.restDNRAPI = R2RestClient(config.DNRAPI_URL)
        self.headers = config.DNRAPI_HEADERS

        # RCS General Config
        self.restRcs = R2RestClient(config.RCS_URL)
        self.rcsHearders = config.RCS_AUTH
        self.machineName = config.RCS_MACHINE

        # other config
        self.clear = lambda: os.system('cls')
        self.initialization()

        # We are going to unassign a test user from their TAG
        CommonTestHelper.unAssignUserFromTag(self)

    def getR2UserGuid(self):
        try:
            route = (
                'fakeUrl/cs_mobile.aspx?txid={0}&PARTNER_URI={1}'
                '&ACTION=PROV_AUTODETECT_IPHONE&DEVICE_TYPE=android'
                '&LOGIN_ALIAS={2}&USER_PASSWORD={3}'
                '&CLIENTID={4}&REQ_SEQ=1'.format(
                    config.fakeUrl_TXID,
                    config.fakeUrl_PARTNER_URI,
                    config.fakeUrl_NONSSO_USER_EMAIL,
                    config.fakeUrl_NONSSO_PASSWORD,
                    config.ANDROID_CLIENT_ID))
            extract = self.restfakeUrl.get(route)
            responses = extract.json()
            R2USERGUID = responses['R2USER_GUID']
            return R2USERGUID
        except BaseException:
            R2USERGUID = CommonTestHelper.getR2UserGuid(self)
            return R2USERGUID

    def initialization(self):
        isPathExists = path.exists('tmp')
        if isPathExists:
            pass
        else:
            directory = "tmp"
            # get current working path
            currPath = os.getcwd()
            tmpPath = os.path.join(currPath, directory)
            os.mkdir(tmpPath)

    def test_fakeUrl_user_bind_get(self):
        try:
            print('\n======== ANDROID USER_BIND_TO_DEVICE - GET ========\n')
            txID = 'TXID'
            route = (config.fakeUrl_URL + ('/fakeUrl/cs_mobile.aspx?txid=txid\
                &PARTNER_URI={0}&ACTION=USER_BIND_TO_DEVICE&R2USER_GUID={5}\
                &REGISTRATION_TTL={6}&REGISTRATION_URI={1}&CLIENTID={2}\
                &TEMPLATE_TYPE=mobile-3&REQ_SEQ=2&DEVICE_ANDROID_ID={4}\
                &DEVICE_IMEI={3}&NOTIFICATION_TOKEN={7}\
                &DEVICE_TYPE=android').format(
                config.fakeUrl_PARTNER_URI,
                config.ANDROID_REGISTRATION_URI,
                config.ANDROID_CLIENT_ID,
                config.ANDROID_DEVICE_IMEI,
                config.ANDROID_DEVICE_ID,
                config.ANDROID_R2USER_GUID,
                config.ANDROID_REGISTRATION_TTL,
                config.fakeUrl_APP_TOKEN))

            response = requests.get(route)
            print(response.content)
            if response.content.__contains__('"STATUS":"200"') is True:
                print('test_passed')
            else:
                print('AssertionError')

        except AssertionError as e:
            print('An error occurred: {}'.format(e))

    def test_fakeUrl_user_bind_post(self):
        try:
            print('\n======== ANDROID USER_BIND_TO_DEVICE - POST ========\n')
            txID = 'TXID'
            route = config.fakeUrl_URL + '/fakeUrl/cs_mobile.aspx'
            body = {
                'ACTION': 'USER_BIND_TO_DEVICE',
                'PARTNER_URI': config.fakeUrl_PARTNER_URI,
                'TXID': txID,
                'REGISTRATION_URI': config.ANDROID_REGISTRATION_URI,
                'CLIENTID': config.ANDROID_CLIENT_ID,
                'DEVICE_IMEI': config.ANDROID_DEVICE_IMEI,
                'DEVICE_TYPE': 'android',
                'DEVICE_ANDROID_ID': config.ANDROID_DEVICE_ID,
                'R2USER_GUID': config.ANDROID_R2USER_GUID,
                'REGISTRATION_TTL': config.ANDROID_REGISTRATION_TTL,
                'REQ_SEQ': '2',
                'TEMPLATE_TYPE': 'mobile-3',
                'NOTIFICATION_TOKEN': config.fakeUrl_APP_TOKEN
            }

            response = requests.post(route, data=body)
            print(response.content)
            if response.content.__contains__('"STATUS":"200"') is True:
                print('test_passed')
            else:
                print('AssertionError')

        except AssertionError as e:
            print('An error occurred: {}'.format(e))

    def test_invitationTemplateShouldNotReturn412(self):
        try:
            ufkAccount = CommonTestHelper.getUfkAccount(
                config.fakeUrl_NONSSO_USER_EMAIL)
            status = "Checking that Invitation Details still return 412\n"
            print status

            CommonTestHelper.unAssignAccountFromTemplate(ufkAccount)
            route = 'invitationDialinNumbers?clearCache=true&ufkaccount={0}'.format(
                ufkAccount)
            response = self.restDNRAPI.get(route, headers=self.headers)
            self.assertEqual(response.status_code, 412)
            print "Status code = " + str(response.status_code)

            status = "Calling fakeUrl......\n"
            print status

            route = (
                'fakeUrl/cs_mobile.aspx?txid={0}&PARTNER_URI={1}'
                '&ACTION=USER_BIND_TO_DEVICE&R2USER_GUID={2}'
                '&REGISTRATION_TTL={3}&REGISTRATION_URI={4}'
                '&CLIENTID={5}&TEMPLATE_TYPE={6}'
                '&REQ_SEQ=2&DEVICE_ANDROID_ID={7}'
                '&DEVICE_IMEI={8}&NOTIFICATION_TOKEN={9}'
                '&DEVICE_TYPE=android'.format(
                    config.fakeUrl_TXID,
                    config.fakeUrl_PARTNER_URI,
                    self.getR2UserGuid(),
                    config.ANDROID_REGISTRATION_TTL,
                    config.ANDROID_REGISTRATION_URI,
                    config.ANDROID_CLIENT_ID,
                    config.ANDROID_TEMPLATE_TYPE,
                    config.ANDROID_DEVICE_ID,
                    config.ANDROID_DEVICE_IMEI,
                    config.ANDROID_NOTIFICATION_TOKEN))
            CommonTestHelper.callfakeUrl(route, "ANDROID")
            print "Done\n"

            status = "Checking Invite Template doesn't Return 412\n"
            print status

            route = 'invitationDialinNumbers?clearCache=true&ufkaccount={0}'.format(
                ufkAccount)
            response = self.restDNRAPI.get(route, headers=self.headers)
            self.assertEqual(response.status_code, 200)
            print "Status code = " + str(response.status_code)

            status = "Checking if DNRS is Matching.....\n"
            print status

            dnrs = CommonTestHelper.InvitationDnrs(self, '')
            fakeUrlDnrs = CommonTestHelper.parsingJson_Android(self)
            dnrs.sort()
            fakeUrlDnrs.sort()
            arrayEqueal = np.array_equal(fakeUrlDnrs, dnrs)
            self.assertEqual(arrayEqueal, True)
            print fakeUrlDnrs
            print dnrs
            print 'test_passed'
        except AssertionError as e:
            print('An error occurred: {}'.format(e))

    def test_ResponsesReturnCorrectDNRS(self):
        try:
            dnrAPI_Disable = CommonTestHelper.dnsSetingsRCS(self)
            asciiConvert = []
            data = []
            _dnrs = []
            fakeUrlDnrsResponses = []
            route = (
                'fakeUrl/cs_mobile.aspx?txid={0}&PARTNER_URI={1}'
                '&ACTION=USER_BIND_TO_DEVICE&R2USER_GUID={2}'
                '&REGISTRATION_TTL={3}&REGISTRATION_URI={4}'
                '&CLIENTID={5}&TEMPLATE_TYPE={6}'
                '&REQ_SEQ=2&DEVICE_ANDROID_ID={7}'
                '&DEVICE_IMEI={8}&NOTIFICATION_TOKEN={9}'
                '&DEVICE_TYPE=android'.format(
                    config.fakeUrl_TXID,
                    config.fakeUrl_PARTNER_URI,
                    self.getR2UserGuid(),
                    config.ANDROID_REGISTRATION_TTL,
                    config.ANDROID_REGISTRATION_URI,
                    config.ANDROID_CLIENT_ID,
                    config.ANDROID_TEMPLATE_TYPE,
                    config.ANDROID_DEVICE_ID,
                    config.ANDROID_DEVICE_IMEI,
                    config.ANDROID_NOTIFICATION_TOKEN))
            extract = self.restfakeUrl.get(route)
            contents = json.loads(extract.content)

            # Dnrs Source
            if dnrAPI_Disable:
                dnrs = CommonTestHelper.antaresDNRS(
                    config.fakeUrl_NONSSO_USER_EMAIL)
            else:
                dnrs = CommonTestHelper.InvitationDnrs(self, '')

            # populatin all dnrs from android responses
            counter = contents['DNRG_COUNT']
            a = 0
            b = 0
            while a < counter:
                dnr = contents['DNRG_LIST'][a]['DNR_LIST']
                inCounter = contents['DNRG_LIST'][a]['DNR_COUNT']
                dnrgTypeID = contents['DNRG_LIST'][a]['DNRG_TYPE_ID']
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
                # 4 it's because we wanna take dnr_displayname, dnr_disp_numb, ufk_dnr, primSecorAvail
                # into one list. Eg: [Antigua Barbuda JK', '1 (866) 310-8637', 'Orinoco:10243', '100', 'Bahrain', 'BAH-089-3434', 'dnr:6f26f437-95c5-4adc-97bb-49c454331793', '100']
                # into something like this [['Antigua Barbuda JK', '1 (866) 310-8637', 'Orinoco:10243', '100'], ['Bahrain', 'BAH-089-3434', 'dnr:6f26f437-95c5-4adc-97bb-49c454331793', '100'],
                # ['Bahrain', 'BAH-089-3434', 'dnr:6f26f437-95c5-4adc-97bb-49c454331793', '110']]
                if i == 4:
                    fakeUrlDnrsResponses.append(inner)
                    i = 0
                    inner = []
            fakeUrlDnrsResponses.sort()
            dnrs.sort()
            arrayEqueal = np.array_equal(fakeUrlDnrsResponses, dnrs)
            self.assertEqual(arrayEqueal, True)
            print fakeUrlDnrsResponses
            print "\n"
            print dnrs
            print 'test_passed'

        except AssertionError as e:
            print('An error occurred: {}'.format(e))

    def test_ResponsesReturnCorrectDNRSWithTag(self):
        try:
            dnrAPI_Disable = CommonTestHelper.dnsSetingsRCS(self)
            ufkUser = CommonTestHelper.getUfkUser(self)

            # create TAG
            ufkTag = CommonTestHelper.createTAG(self)
            # assign user to tag
            CommonTestHelper.assignTagtoUser(self, ufkTag)

            # Change the tag selection to be different with account template
            CommonTestHelper.changeTemplateSelection(self, ufkTag)

            asciiConvert = []
            data = []
            _dnrs = []
            fakeUrlDnrsResponses = []
            route = (
                'fakeUrl/cs_mobile.aspx?txid={0}&PARTNER_URI={1}'
                '&ACTION=USER_BIND_TO_DEVICE&R2USER_GUID={2}'
                '&REGISTRATION_TTL={3}&REGISTRATION_URI={4}'
                '&CLIENTID={5}&TEMPLATE_TYPE={6}'
                '&REQ_SEQ=2&DEVICE_ANDROID_ID={7}'
                '&DEVICE_IMEI={8}&NOTIFICATION_TOKEN={9}'
                '&DEVICE_TYPE=android'.format(
                    config.fakeUrl_TXID,
                    config.fakeUrl_PARTNER_URI,
                    self.getR2UserGuid(),
                    config.ANDROID_REGISTRATION_TTL,
                    config.ANDROID_REGISTRATION_URI,
                    config.ANDROID_CLIENT_ID,
                    config.ANDROID_TEMPLATE_TYPE,
                    config.ANDROID_DEVICE_ID,
                    config.ANDROID_DEVICE_IMEI,
                    config.ANDROID_NOTIFICATION_TOKEN))
            extract = self.restfakeUrl.get(route)
            contents = json.loads(extract.content)

            # Dnrs Source
            if dnrAPI_Disable:
                dnrs = CommonTestHelper.antaresDNRS(
                    config.fakeUrl_NONSSO_USER_EMAIL)
            else:
                dnrs = CommonTestHelper.InvitationDnrs(self, ufkUser)

            # populatin all dnrs from android responses
            counter = contents['DNRG_COUNT']
            a = 0
            b = 0
            while a < counter:
                dnr = contents['DNRG_LIST'][a]['DNR_LIST']
                inCounter = contents['DNRG_LIST'][a]['DNR_COUNT']
                dnrgTypeID = contents['DNRG_LIST'][a]['DNRG_TYPE_ID']
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
                # 4 it's because we wanna take dnr_displayname, dnr_disp_numb, ufk_dnr, primSecorAvail
                # into one list. Eg: [Antigua Barbuda JK', '1 (866) 310-8637', 'Orinoco:10243', '100', 'Bahrain', 'BAH-089-3434', 'dnr:6f26f437-95c5-4adc-97bb-49c454331793', '100']
                # into something like this [['Antigua Barbuda JK', '1 (866) 310-8637', 'Orinoco:10243', '100'], ['Bahrain', 'BAH-089-3434', 'dnr:6f26f437-95c5-4adc-97bb-49c454331793', '100'],
                # ['Bahrain', 'BAH-089-3434', 'dnr:6f26f437-95c5-4adc-97bb-49c454331793', '110']]
                if i == 4:
                    fakeUrlDnrsResponses.append(inner)
                    i = 0
                    inner = []
            fakeUrlDnrsResponses.sort()
            dnrs.sort()
            arrayEqueal = np.array_equal(fakeUrlDnrsResponses, dnrs)
            self.assertEqual(arrayEqueal, True)
            print fakeUrlDnrsResponses
            print "\n"
            print dnrs
            print 'test_passed'

        except AssertionError as e:
            print('An error occurred: {}'.format(e))


if __name__ == "__main__":
    unittest.main()
