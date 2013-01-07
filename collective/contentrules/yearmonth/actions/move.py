from datetime import datetime
from OFS.SimpleItem import SimpleItem

from zope.interface import implements, Interface
from zope.component import adapts
from zope.component import getMultiAdapter
from zope.formlib import form
from zope import schema

from plone.contentrules.rule.interfaces import IExecutable, IRuleElementData

from plone.app.contentrules.browser.formhelper import AddForm, EditForm
from plone.app.vocabularies.catalog import SearchableTextSourceBinder
from plone.app.form.widgets.uberselectionwidget import UberSelectionWidget

from collective.contentrules.yearmonth.interfaces import ITargetFolder
from plone.app.contentrules.actions.move import IMoveAction as \
                                                IOriginalMoveAction
from plone.app.contentrules.actions.move import MoveActionExecutor as \
                                                OriginalMoveActionExecutor

from Products.CMFPlone import PloneMessageFactory as _

TYPES_VOCABULARY = "plone.app.vocabularies.ReallyUserFriendlyTypes"
TRANSITIONS_VOCABULARY = "plone.app.vocabularies.WorkflowTransitions"


class IMoveAction(Interface):
    """
       Interface for the configurable aspects of a move action.
       We don't want to have a static target folder but a target folder inwhich
       contents will be stored in subfolders YYYY/MM
    """

    target_root_folder = schema.Choice(title=_(u"label_target_root",
                                               default=u"Root target folder"),
                                       description=_(u"help_target_root",
                                                     default=u"As a path \
                                                               relative \
                                                               to the \
                                                               portal root"),
                                       required=True,
                                       source=SearchableTextSourceBinder(
                                                      {'is_folderish': True},
                                                      default_query='path:'))

    folderish_type = schema.Choice(title=_(u"Type used to create folder"),
                                   default="Folder",
                                   required=True,
                                   vocabulary=TYPES_VOCABULARY)

    transitions = schema.List(title=_(u"Transitions to execute"),
                              value_type=schema.Choice(title=_(u"Transition"),
                                       vocabulary=TRANSITIONS_VOCABULARY),
                              default=["publish"],
                              required=False)


class MoveAction(SimpleItem):
    """The actual persistent implementation of the action element.
    """
    implements(IMoveAction, IOriginalMoveAction, IRuleElementData)

    target_root_folder = ''
    folderish_type = 'Folder'
    transitions = ['publish']
    element = 'collective.contentrules.yearmonth.actions.Move'

    @property
    def target_folder(self):
        now = datetime.now()
        return "%s/%s" % (self.target_root_folder, now.strftime('%Y/%m'))

    @property
    def summary(self):
        return _(u"Move to folder ${folder}",
                 mapping=dict(folder=self.target_folder))


class MoveActionExecutor(OriginalMoveActionExecutor):
    """The executor for this action.
    """
    implements(IExecutable)
    adapts(Interface, IMoveAction, Interface)

    def __init__(self, context, element, event):
        super(MoveActionExecutor, self).__init__(context, element, event)
        getMultiAdapter((event.object, element), ITargetFolder).setup_target()


class MoveAddForm(AddForm):
    """An add form for move-to-folder actions.
    """
    form_fields = form.FormFields(IMoveAction)
    form_fields['target_root_folder'].custom_widget = UberSelectionWidget
    label = _(u"Add Move Action")
    description = _(u"A move action can move an object to a different \
                      folder/YYYY/MM.")
    form_name = _(u"Configure element")

    def create(self, data):
        a = MoveAction()
        form.applyChanges(a, self.form_fields, data)
        return a


class MoveEditForm(EditForm):
    """An edit form for move rule actions.
    Formlib does all the magic here.
    """
    form_fields = form.FormFields(IMoveAction)
    form_fields['target_root_folder'].custom_widget = UberSelectionWidget
    label = _(u"Edit Move Action YYYY/MM")
    description = _(u"A move action can move an object to a different \
                      folder/YYYY/MM.")
    form_name = _(u"Configure element")
