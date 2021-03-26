import config


def getQueryRelationUserTag(userEmail):
    sql = """
    select TAG.UFK_TAG, relTag.UFK_USER from
    antares_dnr.dbo.relationUser_TAG relTag
    inner join antares_dnr.dbo.tblTemplateAssignmentGroup TAG
    on relTag.TAG_ID = TAG.TAG_ID
    where relTag.UFK_USER in (
    select ufk_user
    from antares.dbo.tblUser where USER_ADDRESS_EMAIL = '{0}')
    """.format(userEmail)
    return sql


def geQuerytR2UserGuid(userEmail):
    sql = """
    select R2USER_GUID
    from antares.dbo.tblUser
    where USER_ADDRESS_EMAIL = '{0}'""".format(userEmail)
    return sql
