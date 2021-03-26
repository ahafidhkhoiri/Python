import config


def getQueryRelationUserTag(userEmail):
    sql = """
    Some queries'{0}')
    """.format(userEmail)
    return sql


def geQuerytR2UserGuid(userEmail):
    sql = """
    Some queries= '{0}'""".format(userEmail)
    return sql
