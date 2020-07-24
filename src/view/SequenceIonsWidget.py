from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import (
    QFont,
    QFontMetricsF,
    QPainter, QColor,
    QPen, QBrush,
    QPaintEvent
)

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QSpacerItem, QSizePolicy
from typing import Union


class SequenceIonsWidget(QWidget):
    """
    Used to create a window for a peptide sequence with its given ions,
    which is adjusted to the sequence size.
    To avoid contortions of the window, spaceritems are added.

    Attributes
    ----------
    HEIGHT : float or int
        The window height adjusted to the drawn peptide

    WEIGHT : float or int
        The window width adjusted to the drawn peptide

    SUFFIX_HEIGHT : float or int
        The given maximum height over all given (stacked) suffix ions


    Methods
    -------
    setPeptide()
        Sets the peptide sequence

    setSuffix()
        Sets the suffix ions from the given peptide sequence

    setPrefix()
        Sets the prefix ions from the given peptide sequence

    updateWindowSize()
        Calculates the window size accordingly for the given heights to fit the
        peptide sequence

    clear()
        Resets the SequenceIons widget back to the default setting

    """

    HEIGHT: Union[float, int] = 0.0
    WIDTH: Union[float, int] = 0.0
    SUFFIX_HEIGHT: Union[float, int] = 0.0

    def __init__(self, *args):
        QWidget.__init__(self, *args)

        self.initUI()

    def initUI(self):
        self.mainlayout = QHBoxLayout(self)
        self.mainlayout.setContentsMargins(0, 0, 0, 0)
        self.container = QWidget(self)
        self.container.setStyleSheet("background-color:white;")

        self.setWindowTitle("SequenceIons Viewer")
        self.seqIons_layout = QHBoxLayout(self.container)

        # change default setting of 11 px
        self.seqIons_layout.setContentsMargins(0, 0, 0, 0)
        self._pep = observed_peptide()
        # resize window to fit peptide size
        self._resize()

        self._pep.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self._pep.setMinimumSize(
            SequenceIonsWidget.WIDTH, SequenceIonsWidget.HEIGHT)
        self.seqIons_layout.addItem(
            QSpacerItem(
                40,
                SequenceIonsWidget.HEIGHT,
                QSizePolicy.MinimumExpanding,
                QSizePolicy.Minimum,
            )
        )
        self.seqIons_layout.addWidget(self._pep)
        self.seqIons_layout.addItem(
            QSpacerItem(
                40,
                SequenceIonsWidget.HEIGHT,
                QSizePolicy.MinimumExpanding,
                QSizePolicy.Minimum,
            )
        )

        self.setFixedHeight(SequenceIonsWidget.HEIGHT)
        self.mainlayout.addWidget(self.container)
        self.show()

    def _resize(self):
        """
        The integer 8 represents the additional space needed
        for the in addition drawn lines. The 18 represents the
        monospace width.

        """
        if self._pep.seqLength != 0:
            SequenceIonsWidget.WIDTH = \
                (self._pep.seqLength * 18.0) + \
                (self._pep.seqLength - 1.0) * 8.0

        # calculate heights
        prefix: Dict = self._pep.prefix
        suffix: Dict = self._pep.suffix

        if suffix == {}:
            max_ion_suff = 1
        else:
            max_ion_suff = len(
                suffix[max(suffix, key=lambda key: len(suffix[key]))])

        if prefix == {}:
            max_ion_pre = 1
        else:
            max_ion_pre = len(
                prefix[max(prefix, key=lambda key: len(prefix[key]))])

        metrics_pep = QFontMetricsF(self._pep.getFont_Pep())
        metrics_ion = QFontMetricsF(self._pep.getFont_Ion())
        height_pep = metrics_pep.height()
        height_ion = metrics_ion.height()

        # window height calculated with the sum of max prefix and suffix height
        height_ion_pre = height_ion * max_ion_pre + 15.0
        SequenceIonsWidget.SUFFIX_HEIGHT = height_ion * max_ion_suff + 5.0
        SequenceIonsWidget.HEIGHT = \
            (
                height_pep + height_ion_pre + SequenceIonsWidget.SUFFIX_HEIGHT
            )

    def setPeptide(self, seq):
        self._pep.setSequence(seq)
        self.updateWindowSize()

    def setSuffix(self, suff):
        self._pep.setSuffix(suff)
        self.updateWindowSize()

    def setPrefix(self, pre):
        self._pep.setPrefix(pre)
        self.updateWindowSize()

    def updateWindowSize(self):
        self._resize()
        self._pep.setMinimumSize(
            SequenceIonsWidget.WIDTH, SequenceIonsWidget.HEIGHT)
        self.setFixedHeight(SequenceIonsWidget.HEIGHT)
        self.update()

    def clear(self):
        self._pep.sequence = ""
        self._pep.suffix = {}
        self._pep.prefix = {}
        self.update()

class observed_peptide(QWidget):
    """
    Used for creating a peptide sequence with its given ions.
    The ions can be stacked above each other, e.g. in case for
    a1, b1. Each amino letter is also separated by a line
    and prefixes are colored blue, otherwise suffixes are colored
    red.

    Attributes
    ----------
    sequence : str
        The peptide sequence from a MS2 spectrum

    seqLength : int
        The number of aa in the peptide sequence

    suffix : dict
        Containing all suffix ion information for the given sequence

    prefix : dict
        Containing all prefix ion information for the given sequence

    colors : dict
        Containing the colors for the drawn lines (black), suffix (red) and
        prefix (blue) ions


    Methods
    -------
    setSequence()
        Sets the peptide sequence

    setSuffix()
        Sets the suffix ions from the given peptide sequence

    setPrefix()
        Sets the prefix ions from the given peptide sequence

    getFont_Pep()
        Returns a QFont object with the selected font type and font size (30)
        for the peptide sequence

    getFont_Ion()
        Returns a QFont object with the selected font type and font size (10)
        for the ion(s)

    """

    def __init__(self):
        QWidget.__init__(self)
        self.initUI()

    def initUI(self):
        self.sequence = ""
        self.seqLength = 0
        self.suffix = {}
        self.prefix = {}
        self.colors = {
            "black": QColor(0, 0, 0),
            "red": QColor(255, 0, 0),
            "blue": QColor(0, 0, 255),
        }

    def setSequence(self, seq: str) -> None:
        self.sequence = seq
        self.seqLength = len(seq)

    def setSuffix(self, lst: dict) -> None:
        self.suffix = lst

    def setPrefix(self, lst: dict) -> None:
        self.prefix = lst

    def paintEvent(self, event: QPaintEvent) -> None:
        qp = QPainter()
        qp.begin(self)
        qp.setRenderHint(QPainter.Antialiasing)
        qp.fillRect(event.rect(), QBrush(Qt.white))  # or changed to Qt.white
        self._drawPeptide(qp)
        qp.end()

    def _drawPeptide(self, qp: QPainter) -> None:
        qp.setWindow(0, 0, SequenceIonsWidget.WIDTH, SequenceIonsWidget.HEIGHT)
        qp.setPen(self.colors["black"])
        qp.setFont(self.getFont_Pep())
        self._fragmentPeptide(qp)

    def _fragmentPeptide(self, qp: QPainter) -> None:
        """
        The sequence will be generated stepwise by drawing each aa of the
        sequence separately and adding in each step lines and existing ions.

        The procedure can be described in two steps:
        1. Check if sequence is given, if so
        then transform seq into a dictionary
        (with the indices representing the positions of the chars).
        2. For each char in the sequence:
            Firstly, calculate start position of char
            (be aware that the char rect is created
            at the left bottom corner of
            the char, meaning we have to add the height of the Font
            & possible suffixes to the starting height position
            to move it into the center of the window).

            Secondly, calculate the center point for the vertical Line.
            The Line consists of a point start and point end.
            The starting line xPos yield in the
            start_point + blank - (SPACE/2),
            where blank represents the additional
            space from the starting point after each new char.

            Third, if prefix or suffix ions are given,
            then distinguish between suffix and prefix to draw the vertical
            line with either left or right line or both.

            Because of changing the fonts for the ions,
            the fonts needs to be reset.

        Parameters
        ----------
        qp : QPainter
            The QPainter class provides functions required to paint within the
            widget

        """
        blankspace: int = 8

        if self.sequence != "":

            seq = list(self.sequence)
            dict_seq = {i: seq[i] for i in range(0, len(seq))}

            metrics = QFontMetricsF(self.getFont_Pep())

            blank = 0
            for i, s in dict_seq.items():
                i_rev = self._getReverseIndex(i, dict_seq)

                width = metrics.boundingRect(s).width()
                height = metrics.boundingRect(s).height()

                start_point = 0

                # position of char with center indent
                position = QPointF(
                    start_point + blank,
                    SequenceIonsWidget.SUFFIX_HEIGHT + height
                )
                qp.drawText(position, s)

                # position lines for possible ions
                centerOfLine = \
                    (
                        SequenceIonsWidget.SUFFIX_HEIGHT + height - height / 4
                    ) - 1

                start_linePos = QPointF(
                    start_point + blank - (blankspace / 2),
                    centerOfLine - height / 2 - 2.5
                )
                end_linePos = QPointF(
                    start_linePos.x(), centerOfLine + height / 2 + 2.5
                )

                qp.setFont(self.getFont_Ion())
                metrics_ion = QFontMetricsF(self.getFont_Ion())

                if i in self.prefix:
                    left_linePos = self._drawIonsLines(
                        qp, start_linePos, end_linePos, blankspace, "prefix"
                    )
                    self._drawPrefixIon(qp, i, metrics_ion, left_linePos)

                # for given line of existing prefix, expand with given suffix
                if i in self.prefix and i_rev in self.suffix:
                    right_linePos = self._drawIonsLines(
                        qp, start_linePos, end_linePos, blankspace, "suffix"
                    )
                    self._drawSuffixIon(
                        qp, i_rev, metrics_ion, end_linePos, right_linePos
                    )

                elif i_rev in self.suffix and i not in self.prefix:
                    right_linePos = self._drawIonsLines(
                        qp, start_linePos, end_linePos, blankspace, "suffix"
                    )
                    self._drawSuffixIon(
                        qp, i_rev, metrics_ion, start_linePos, right_linePos
                    )

                blank += width + blankspace
                qp.setPen(self._getPen(self.colors["black"]))
                qp.setFont(self.getFont_Pep())

    def _drawPrefixIon(self,
                       qp: QPainter,
                       index: int,
                       metrics_ion: QFontMetricsF,
                       pos_left: QPointF) -> None:
        """
        Draws existing prefix ion(s) and the left line at this position.

        Parameters
        ----------
        qp : QPainter
            The QPainter class provides functions required to paint within the
            widget

        index: int
            The position of the prefix ion(s) within the peptide

        metrics_ion : QFontMetricsF
            The font metrics of the ion(s) for the given font

        pos_left : QPointF
            The coordination of the left line provided for the prefix ion(s)

        """
        qp.setPen(self._getPen(self.colors["blue"]))
        prefix_ions = sorted(self.prefix[index])
        blank_ion = 10

        for ion in prefix_ions:
            height_ion = metrics_ion.boundingRect(ion).height()
            pos_ion = QPointF(pos_left.x(), pos_left.y() + blank_ion)
            qp.drawText(pos_ion, ion)
            blank_ion += height_ion

    def _drawSuffixIon(self,
                       qp: QPainter,
                       index_reverse: int,
                       metrics_ion: QFontMetricsF,
                       pos_end: QPointF,
                       pos_right: QPointF) -> None:
        """
        Draws existing suffix ion(s) and the right line at this position.

        Parameters
        ----------
        qp : QPainter
            The QPainter class provides functions required to paint within the
            widget

        index_reverse: int
            The position of the suffix ion(s) within the peptide. The
            positions are in reverse order compared to the prefix ion(s)

        metrics_ion : QFontMetricsF
            The font metrics of the ion(s) for the given font

        pos_end : QPointF
            The start position of the right line

        pos_right : QPointF
            The end position of the right line

        """
        qp.setPen(self._getPen(self.colors["red"]))
        suffix_ions = sorted(self.suffix[index_reverse], reverse=True)
        blank_ion = 5

        for ion in suffix_ions:
            height_ion = metrics_ion.boundingRect(ion).height()
            pos_ion = QPointF(pos_end.x() + 2.5, pos_right.y() - blank_ion)
            qp.drawText(pos_ion, ion)
            blank_ion += height_ion

    def _drawIonsLines(self,
                       qp: QPainter,
                       pos_start: QPointF,
                       pos_end: QPointF,
                       blankspace: int,
                       iontype: str) -> QPointF:
        """
        Draw the middle line between each aa in the peptide.

        Parameters
        ----------
        qp : QPainter
            The QPainter class provides functions required to paint within the
            widget

        pos_start: QPointF
            The start position of the line

        pos_end : QPointF
            The end position of the line

        blankspace : int
            The extra space of between each aa

        iontype : str
            The type differentiation between suffix or prefix (ions)


        Returns
        -------
        QPointF
            The end position of the left or right line depending on the ion
            type

        """

        qp.setPen(self._getPen(self.colors["black"]))

        if iontype == "prefix":
            qp.drawLine(pos_start, pos_end)
            pos_left = QPointF(pos_end.x() - 2 * blankspace, pos_end.y())
            qp.drawLine(pos_end, pos_left)
            return pos_left

        if iontype == "suffix":
            qp.drawLine(pos_start, pos_end)
            pos_right = QPointF(pos_start.x() + 2 * blankspace, pos_start.y())
            qp.drawLine(pos_start, pos_right)
            return pos_right

    def getFont_Pep(self) -> QFont:
        """
        Initializes the font character for the aa's.

        Returns
        -------
        QFont
            The font is Courier and of size 30

        """
        font = QFont("Courier")
        font.setStyleHint(QFont.TypeWriter)
        font.setPixelSize(30)
        return font

    def getFont_Ion(self) -> QFont:
        """
        Initializes the font character for the ion(s).

        Returns
        -------
        QFont
            The font is Courier and of size 10

        """
        font = QFont("Courier")
        font.setStyleHint(QFont.TypeWriter)
        font.setPixelSize(10)
        return font

    def _getPen(self, color: QColor) -> QPen:
        """
        Style setting for the lines

        Parameters
        ----------
        color : QColor
            The coloration of the lines. Typically, the lines are black


        Returns
        -------
        QPen
            The style for the lines are dash dot lines

        """
        pen = QPen(color, 0.75, Qt.SolidLine)
        pen.setStyle(Qt.DashDotLine)
        return pen

    def _getReverseIndex(self, i: int, dict_seq: dict) -> int:
        """
        Calculates the reverse index for a given index.

        Parameters
        ----------
        i : int
            A given index

        dict_seq : Dict
            A dict that contains the given ion index


        Returns
        -------
        int
            The reverse index from the given index

        """
        i_rev = 0
        if i != 0:
            i_rev = list(dict_seq.keys())[-i]
        return i_rev
