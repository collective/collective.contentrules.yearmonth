from zope.interface import Interface


class ITargetFolder(Interface):
    """
       In this package we provide a new kind of move action for content rules
       The administrator choose a target root folder but contents won't be
       moved there but in dynamic subfolders. For example target/YYYY/MM
       depending on the move date. The YYYY and MM folders will be created
       automatically if needed.

       This should adapt the content to be moved and the content rule action
       IMoveAction defined in this package.
    """

    def setup_target():
        """
           Creates if needed and returns the target folder into the target
           root folder
        """
