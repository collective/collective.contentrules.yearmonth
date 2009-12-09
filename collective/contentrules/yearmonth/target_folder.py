import datetime
from AccessControl import SecurityManagement
from AccessControl import SpecialUsers

from zope.interface import Interface
from zope.interface import implements
from zope.component import adapts
from zope.component import getMultiAdapter

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
        now = datetime.datetime.now()
        year_id = str(now.year)
        month_id = str(now.month)

        portal = getMultiAdapter((self.context, self.context.REQUEST),
                                 name=u'plone_portal_state').portal()
        path = self.action.target_root_folder
        if len(path) > 1 and path[0] == '/':
            path = path[1:]

        target_root = portal.unrestrictedTraverse(str(path), None)

        if not target_root.hasObject(year_id):
            year_id = self._invokeFactory(target_root, 'Folder', year_id)
            year = getattr(target_root, year_id)
            self._invokeFactory(year, 'Folder', month_id)
            return getattr(year, month_id)
        else:
            year = getattr(target_root, year_id)
            if not year.hasObject(month_id):
                month_id = self._invokeFactory(year, 'Folder', month_id)
                return getattr(year, month_id)

        return None

    def _invokeFactory(self, context, type, id, title=''):
        old_sm = SecurityManagement.getSecurityManager()
        SecurityManagement.newSecurityManager(None, SpecialUsers.system)
        try:
            new_id = context.invokeFactory(type, id=id, title=title)
        finally:
            SecurityManagement.setSecurityManager(old_sm)
        return new_id
