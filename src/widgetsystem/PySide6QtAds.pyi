"""Type stubs for PySide6QtAds (Qt Advanced Docking System).

This file provides type hints for the PySide6-QtAds library.
Updated for 2026 standards with complete API coverage.
"""

from typing import Any, ClassVar

from PySide6.QtCore import QByteArray, QObject, Qt
from PySide6.QtWidgets import QFrame, QSplitterHandle, QWidget


class CDockManager(QFrame):
    """Main dock manager that contains all dock widgets and dock areas."""

    class ConfigFlag:
        """Configuration flags for dock manager behavior."""

        ActiveTabHasCloseButton: ClassVar[int]
        DockAreaHasCloseButton: ClassVar[int]
        DockAreaHasUndockButton: ClassVar[int]
        DockAreaHasTabsMenuButton: ClassVar[int]
        DockAreaHideDisabledButtons: ClassVar[int]
        DockAreaDynamicTabsMenuButtonVisibility: ClassVar[int]
        OpaqueSplitterResize: ClassVar[int]
        XmlCompressionEnabled: ClassVar[int]
        XmlAutoFormattingEnabled: ClassVar[int]
        AllTabsHaveCloseButton: ClassVar[int]
        RetainTabSizeWhenCloseButtonHidden: ClassVar[int]
        OpaqueUndocking: ClassVar[int]
        DragPreviewIsDynamic: ClassVar[int]
        DragPreviewShowsContentPixmap: ClassVar[int]
        DragPreviewHasWindowFrame: ClassVar[int]
        AlwaysShowTabs: ClassVar[int]
        DockAreaHasUndockButton: ClassVar[int]
        DockAreaHasTabsMenuButton: ClassVar[int]
        DockAreaCloseButtonClosesTab: ClassVar[int]
        EqualSplitOnInsertion: ClassVar[int]
        FloatingContainerHasWidgetTitle: ClassVar[int]
        FloatingContainerHasWidgetIcon: ClassVar[int]
        HideSingleWidgetTitleBar: ClassVar[int]
        MinimumSplitterSize: ClassVar[int]
        FloatingContainerForceNativeTitleBar: ClassVar[int]
        FloatingContainerForceQWidgetTitleBar: ClassVar[int]
        MiddleMouseButtonClosesTab: ClassVar[int]
        DisableTabTextEliding: ClassVar[int]
        ShowTabTextOnlyForActiveTab: ClassVar[int]
        DefaultDockAreaButtons: ClassVar[int]
        DefaultBaseConfig: ClassVar[int]
        DefaultOpaqueConfig: ClassVar[int]
        DefaultNonOpaqueConfig: ClassVar[int]
        NonOpaqueWithWindowFrame: ClassVar[int]

    # Alias for compatibility
    eConfigFlag = ConfigFlag

    def __init__(self, parent: QWidget) -> None: ...
    @staticmethod
    def configFlags() -> int: ...
    @staticmethod
    def setConfigFlag(flag: int, enabled: bool = True) -> None: ...
    @staticmethod
    def setConfigFlags(flags: int) -> None: ...
    @staticmethod
    def testConfigFlag(flag: int) -> bool: ...
    def saveState(self, version: int = 0) -> QByteArray: ...
    def restoreState(self, state: QByteArray, version: int = 0) -> bool: ...
    def addDockWidget(
        self,
        area: int,
        dockwidget: CDockWidget,
        areawidget: CDockAreaWidget | None = None,
    ) -> CDockAreaWidget: ...
    def addDockWidgetTab(
        self, area: int, dockwidget: CDockWidget
    ) -> CDockAreaWidget: ...
    def addDockWidgetTabToArea(
        self, dockwidget: CDockWidget, area: CDockAreaWidget, index: int = -1
    ) -> CDockAreaWidget: ...
    def addDockWidgetToContainer(
        self, area: int, dockwidget: CDockWidget, container: CDockContainerWidget
    ) -> CDockAreaWidget: ...
    def removeDockWidget(self, dockwidget: CDockWidget) -> None: ...
    def findDockWidget(self, objectName: str) -> CDockWidget | None: ...
    def allOpenDockWidgets(self) -> list[CDockWidget]: ...
    def dockWidgetsMap(self) -> dict[str, CDockWidget]: ...
    def dockContainers(self) -> list[CDockContainerWidget]: ...
    def floatingWidgets(self) -> list[CFloatingDockContainer]: ...
    def centralWidget(self) -> CDockWidget | None: ...
    def setCentralWidget(self, widget: CDockWidget) -> CDockAreaWidget: ...
    def isRestoringState(self) -> bool: ...
    def splitterSizes(self, area: CDockAreaWidget) -> list[int]: ...
    def setSplitterSizes(self, area: CDockAreaWidget, sizes: list[int]) -> None: ...


class CDockWidget(QFrame):
    """Dock widget that can be docked into a dock area."""

    class DockWidgetFeature:
        """Features that can be enabled/disabled for dock widgets."""

        DockWidgetClosable: ClassVar[int]
        DockWidgetMovable: ClassVar[int]
        DockWidgetFloatable: ClassVar[int]
        DockWidgetDeleteOnClose: ClassVar[int]
        CustomCloseHandling: ClassVar[int]
        DockWidgetFocusable: ClassVar[int]
        DockWidgetForceCloseWithArea: ClassVar[int]
        NoTab: ClassVar[int]
        DeleteContentOnClose: ClassVar[int]
        DockWidgetPinnable: ClassVar[int]
        DefaultDockWidgetFeatures: ClassVar[int]
        AllDockWidgetFeatures: ClassVar[int]
        NoDockWidgetFeatures: ClassVar[int]

    class eState:
        """Dock widget states."""

        StateHidden: ClassVar[int]
        StateDocked: ClassVar[int]
        StateFloating: ClassVar[int]

    class eToggleViewActionMode:
        """Toggle view action modes."""

        ActionModeToggle: ClassVar[int]
        ActionModeShow: ClassVar[int]

    class eToolBarStyleSource:
        """Toolbar style source."""

        ToolBarStyleFromDockManager: ClassVar[int]
        ToolBarStyleFromDockWidget: ClassVar[int]

    def __init__(
        self, title: str, parent: QWidget | None = None
    ) -> None: ...
    def setWidget(
        self, widget: QWidget, insertMode: int = 0
    ) -> None: ...
    def widget(self) -> QWidget: ...
    def tabWidget(self) -> CDockWidgetTab: ...
    def setFeature(self, flag: int, enabled: bool) ->None: ...
    def setFeatures(self, features: int) -> None: ...
    def features(self) -> int: ...
    def dockManager(self) -> CDockManager: ...
    def dockContainer(self) -> CDockContainerWidget: ...
    def dockAreaWidget(self) -> CDockAreaWidget | None: ...
    def isFloating(self) -> bool: ...
    def isClosed(self) -> bool: ...
    def toggleView(self, open: bool = True) -> None: ...
    def setFloating(self) -> None: ...
    def deleteDockWidget(self) -> None: ...
    def closeDockWidget(self) -> None: ...
    def setObjectName(self, name: str) -> None: ...
    def objectName(self) -> str: ...
    def windowTitle(self) -> str: ...
    def setWindowTitle(self, title: str) -> None: ...


class CDockAreaWidget(QFrame):
    """Container for multiple dock widgets in tabs."""

    def dockWidgets(self) -> list[CDockWidget]: ...
    def currentDockWidget(self) -> CDockWidget: ...
    def setCurrentDockWidget(self, dockwidget: CDockWidget) -> None: ...
    def dockManager(self) -> CDockManager: ...
    def titleBar(self) -> CDockAreaTitleBar: ...
    def isVisible(self) -> bool: ...
    def toggleView(self, open: bool) -> None: ...


class CDockAreaTitleBar(QFrame):
    """Title bar of a dock area with tabs."""

    def dockAreaWidget(self) -> CDockAreaWidget: ...
    def showContextMenu(self, pos: Any) -> None: ...


class CDockContainerWidget(QFrame):
    """Container that manages floating or docked widgets."""

    def dockAreaWidgets(self) -> list[CDockAreaWidget]: ...
    def dockWidgets(self) -> list[CDockWidget]: ...
    def dockManager(self) -> CDockManager: ...
    def floatingWidget(self) -> CFloatingDockContainer | None: ...
    def isFloating(self) -> bool: ...


class CFloatingDockContainer(QWidget):
    """Floating window container for dock widgets."""

    def dockContainer(self) -> CDockContainerWidget: ...
    def dockWidgets(self) -> list[CDockWidget]: ...


class CDockWidgetTab(QFrame):
    """Tab widget for a dock widget."""

    def dockWidget(self) -> CDockWidget: ...
    def isActiveTab(self) -> bool: ...
    def setActiveTab(self, active: bool) -> None: ...


class CDockSplitter(QFrame):
    """Splitter for resizing dock areas."""

    def handle(self, index: int) -> QSplitterHandle: ...
    def setHandleWidth(self, width: int) -> None: ...
    def handleWidth(self) -> int: ...


# Dock areas (integer constants)
LeftDockWidgetArea: int
RightDockWidgetArea: int
TopDockWidgetArea: int
BottomDockWidgetArea: int
CenterDockWidgetArea: int
InvalidDockWidgetArea: int
OuterDockAreas: int
AllDockAreas: int

# Additional constants
NoDockWidgetArea: int
