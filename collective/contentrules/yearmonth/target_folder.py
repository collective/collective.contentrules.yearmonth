from datetime import datetime
from AccessControl import SecurityManagement
from AccessControl import SpecialUsers

from zope.interface import Interface
from zope.interface import implements
from zope.component import adapts
from zope.component import getMultiAdapter

from plone import api

from collective.contentrules.yearmonth.actions.move import IMoveAction
from collective.contentrules.yearmonth.interfaces import ITargetFolder


class TargetFolder(object):
    """ Default implementation of ITargetFolder """
    implements(ITargetFolder)
    adapts(Interface, IMoveAction)

    def __init__(self, context, action):
        self.context = context
        self.action = action

    def setup_target(self):
        """ """
        now = datetime.now()
        year_id, month_id = now.strftime('%Y/%m').split('/')

        portal = getMultiAdapter((self.context, self.context.REQUEST),
                                 name=u'plone_portal_state').portal()
        path = self.action.target_root_folder
        if len(path) > 1 and path[0] == '/':
            path = path[1:]

        target_root = portal.unrestrictedTraverse(str(path), None)

        if not target_root.hasObject(year_id):
            year = self.create_folder(target_root, year_id)
        else:
            year = getattr(target_root, year_id)

        if not year.hasObject(month_id):
            month = self.create_folder(year, month_id)
        else:
            month = getattr(year, month_id)

        return month

    def create_folder(self, context, id, title=''):
        old_sm = SecurityManagement.getSecurityManager()
        SecurityManagement.newSecurityManager(None, SpecialUsers.system)
        try:
            folder = api.content.create(type=self.action.folderish_type,
                                        id=id,
                                        title=title,
                                        container=context)
            for transition in self.action.transitions:
                api.content.transition(obj=folder,
                                       transition=transition)
        finally:
            SecurityManagement.setSecurityManager(old_sm)
        return folder
