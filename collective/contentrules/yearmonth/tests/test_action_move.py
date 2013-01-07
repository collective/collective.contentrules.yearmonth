from datetime import datetime

from zope.interface import implements
from zope.component import getUtility, getMultiAdapter
from zope.component.interfaces import IObjectEvent

from plone.contentrules.engine.interfaces import IRuleStorage
from plone.contentrules.rule.interfaces import IRuleAction
from plone.contentrules.rule.interfaces import IExecutable
from plone.app.contentrules.rule import Rule
from plone.app.contentrules.tests.base import ContentRulesTestCase
from Products.PloneTestCase.setup import default_user

from collective.contentrules.yearmonth.actions.move import MoveAction
from collective.contentrules.yearmonth.actions.move import MoveEditForm
from collective.contentrules.yearmonth.interfaces import ITargetFolder

now = datetime.now()
year, month = now.strftime('%Y/%m').split('/')


class DummyEvent(object):
    implements(IObjectEvent)

    def __init__(self, object):
        self.object = object


class TestMoveAction(ContentRulesTestCase):

    def afterSetUp(self):
        self.loginAsPortalOwner()
        self.portal.invokeFactory('Folder', 'target')
        self.folder.invokeFactory('Folder', 'source')
        self.login(default_user)
        self.folder.source.invokeFactory('Document', 'd1')

    def testRegistered(self):
        element = getUtility(IRuleAction,
                         name='collective.contentrules.yearmonth.actions.Move')
        self.assertEquals('collective.contentrules.yearmonth.actions.Move',
                          element.addview)
        self.assertEquals('edit', element.editview)
        self.assertEquals(None, element.for_)
        self.assertEquals(IObjectEvent, element.event)

    def testInvokeAddView(self):
        element = getUtility(IRuleAction,
                         name='collective.contentrules.yearmonth.actions.Move')
        storage = getUtility(IRuleStorage)
        storage[u'foo'] = Rule()
        rule = self.portal.restrictedTraverse('++rule++foo')
        adding = getMultiAdapter((rule, self.portal.REQUEST), name='+action')

        addview = getMultiAdapter((adding, self.portal.REQUEST),
                                  name=element.addview)

        addview.createAndAdd(data={'target_root_folder': '/target', })

        e = rule.actions[0]
        self.failUnless(isinstance(e, MoveAction))
        self.assertEquals('/target', e.target_root_folder)

    def testInvokeEditView(self):
        element = getUtility(IRuleAction,
                         name='collective.contentrules.yearmonth.actions.Move')
        e = MoveAction()
        editview = getMultiAdapter((e, self.folder.source.REQUEST),
                                   name=element.editview)
        self.failUnless(isinstance(editview, MoveEditForm))

    def testExecute(self):
        e = MoveAction()
        e.target_root_folder = '/target'

        ex = getMultiAdapter((self.folder.source,
                              e,
                              DummyEvent(self.folder.source.d1)),
                             IExecutable)
        self.assertEquals(True, ex())

        self.failIf('d1' in self.folder.source.objectIds())
        self.failUnless(year in self.portal.target.objectIds())

        self.failUnless(month in self.portal.target[year].objectIds())
        self.failUnless('d1' in self.portal.target[year][month].objectIds())

    def testTargetFolder(self):
        target_root = self.portal.target
        self.failIf(year in target_root.objectIds())

        e = MoveAction()
        e.target_root_folder = '/target'
        target_adapter = getMultiAdapter((self.folder.source.d1, e),
                                         ITargetFolder)
        target = target_adapter.setup_target()

        self.failUnless("/target/%s/%s" % (year, month) in
                        target.absolute_url())

#    def testExecuteWithError(self): 
#        e = MoveAction()
#        e.target_root_folder = '/dummy'
#        
#        ex = getMultiAdapter((self.portal.source, e, DummyEvent(self.portal.source.d1)), IExecutable)
#        self.assertEquals(False, ex())
#        
#        self.failUnless('d1' in self.portal.source.objectIds())
#        import datetime
#        now = datetime.datetime.now()
#        year = str(now.year)
#        month = str(now.month)
#        self.failIf('d1' in self.portal.target[year][month].objectIds())
#        
#    def testExecuteWithoutPermissionsOnTarget(self):
#        self.setRoles(('Member',))
#        
#        e = MoveAction()
#        e.target_folder = '/target'
#        
#        ex = getMultiAdapter((self.folder, e, DummyEvent(self.folder.d1)), IExecutable)
#        self.assertEquals(True, ex())
#        
#        self.failIf('d1' in self.folder.objectIds())
#        self.failUnless('d1' in self.portal.target.objectIds())
#        
#    def testExecuteWithNamingConflict(self):
#        self.setRoles(('Manager',))
#        self.portal.target.invokeFactory('Document', 'd1')
#        self.setRoles(('Member',))
#        
#        e = MoveAction()
#        e.target_folder = '/target'
#        
#        ex = getMultiAdapter((self.folder, e, DummyEvent(self.folder.d1)), IExecutable)
#        self.assertEquals(True, ex())
#        
#        self.failIf('d1' in self.folder.objectIds())
#        self.failUnless('d1' in self.portal.target.objectIds())
#        self.failUnless('d1.1' in self.portal.target.objectIds())
#        
#    def testExecuteWithSameSourceAndTargetFolder(self):
#        self.setRoles(('Manager',))
#        self.portal.target.invokeFactory('Document', 'd1')
#        self.setRoles(('Member',))
#        
#        e = MoveAction()
#        e.target_folder = '/target'
#        
#        ex = getMultiAdapter((self.portal.target, e, DummyEvent(self.portal.target.d1)), IExecutable)
#        self.assertEquals(True, ex())
#        
#        self.assertEquals(['d1'], list(self.portal.target.objectIds()))
#
#    def testExecuteWithNamingConflictDoesNotStupidlyAcquireHasKey(self):
#        # self.folder is an ATBTreeFolder and so has a has_key. self.folder.target
#        # does not. Let's make sure we don't accidentally acquire has_key and use
#        # this for the check for unique id.
#
#        self.folder.invokeFactory('Folder', 'target')
#        self.folder.target.invokeFactory('Document', 'd1')
#        
#        e = MoveAction()
#        e.target_folder = '/Members/%s/target' % default_user
#        
#        ex = getMultiAdapter((self.folder.target, e, DummyEvent(self.folder.d1)), IExecutable)
#        self.assertEquals(True, ex())
#        
#        self.failIf('d1' in self.folder.objectIds())
#        self.failUnless('d1' in self.folder.target.objectIds())
#        self.failUnless('d1.1' in self.folder.target.objectIds())


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestMoveAction))
    return suite
