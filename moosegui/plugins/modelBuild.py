# -*- coding: utf-8 -*-

__author__     = "Harsha Rani"
__credits__    = ["Upi Lab"]
__license__    = "GPLv3"
__maintainer__ = "Harsha Rani, Dilawar Singh"
__email__      = "hrani@ncbs.res.in"

import moose
from moosegui.plugins import kkitQGraphics
from moosegui.plugins import kkitUtil
from PyQt5 import Qt, QtCore
from PyQt5 import QtGui


def updateCompartmentSize(qGraCompt):
    #childBoundingRect = qGraCompt.childrenBoundingRect()
    childBoundingRect = kkitUtil.calculateChildBoundingRect(qGraCompt)
    comptBoundingRect = qGraCompt.boundingRect()
    rectcompt = comptBoundingRect.united(childBoundingRect)
    comptPen = qGraCompt.pen()
    comptWidth = 1
    comptPen.setWidth(comptWidth)
    qGraCompt.setPen(comptPen)
    if not comptBoundingRect.contains(childBoundingRect):
        qGraCompt.setRect(rectcompt.x() - comptWidth,
                          rectcompt.y() - comptWidth,
                          rectcompt.width() + (comptWidth * 2),
                          rectcompt.height() + (comptWidth * 2))


def checkCreate(scene, view, modelpath, mobj, string, ret_string, num,
                event_pos, layoutPt):
    # The variable 'compt' will be empty when dropping cubeMesh,cyclMesh, but rest it shd be
    # compartment
    if moose.exists(modelpath + '/info'):
        moose.Annotator((moose.element(modelpath + '/info'))).modeltype
    itemAtView = view.sceneContainerPt.itemAt(view.mapToScene(event_pos))
    pos = view.mapToScene(event_pos)
    modelpath = moose.element(modelpath)
    if num:
        string_num = ret_string + str(num)
    else:
        string_num = ret_string
    if string == "CubeMesh" or string == "CylMesh":
        if string == "CylMesh":
            mobj = moose.CylMesh(modelpath.path + '/' + string_num)
        else:
            mobj = moose.CubeMesh(modelpath.path + '/' + string_num)

        mobj.volume = 1e-15
        qGItem = kkitQGraphics.ComptItem(scene,
                                         pos.toPoint().x(),
                                         pos.toPoint().y(), 100, 100, mobj)
        qGItem.setPen(
            QtGui.QPen(Qt.QColor(66, 66, 66, 100), 1, Qt.Qt.SolidLine,
                       Qt.Qt.RoundCap, Qt.Qt.RoundJoin))
        view.sceneContainerPt.addItem(qGItem)

        qGItem.cmptEmitter.connect(
            qGItem.cmptEmitter,
            QtCore.SIGNAL("qgtextPositionChange(PyQt_PyObject)"),
            layoutPt.positionChange1)

        qGItem.cmptEmitter.connect(
            qGItem.cmptEmitter,
            QtCore.SIGNAL("qgtextItemSelectedChange(PyQt_PyObject)"),
            layoutPt.objectEditSlot)
        layoutPt.qGraCompt[mobj] = qGItem

        # Attach a drop signal.
        qGItem.dropped.emit()

    elif string == "Pool" or string == "BufPool":
        #getting pos with respect to compartment otherwise if compartment is moved then pos would be wrong
        posWrtComp = (itemAtView.mapFromScene(pos)).toPoint()
        if string == "Pool":
            poolObj = moose.Pool(mobj.path + '/' + string_num)
        else:
            poolObj = moose.BufPool(mobj.path + '/' + string_num)

        poolinfo = moose.Annotator(poolObj.path + '/info')

        qGItem = kkitQGraphics.PoolItem(poolObj, itemAtView)
        layoutPt.mooseId_GObj[poolObj] = qGItem
        posWrtComp = (itemAtView.mapFromScene(pos)).toPoint()
        bgcolor = kkitUtil.getRandColor()
        qGItem.setDisplayProperties(posWrtComp.x(), posWrtComp.y(),
                                    QtGui.QColor('green'), bgcolor)
        poolinfo.color = str(bgcolor.getRgb())
        qGItem.dropped.emit()

        kkitUtil.setupItem(modelpath.path, layoutPt.srcdesConnection)
        layoutPt.drawLine_arrow(False)
        x, y = roundoff(qGItem.scenePos(), layoutPt)
        poolinfo.x = x
        poolinfo.y = y
        #Dropping is on compartment then update Compart size
        if isinstance(mobj, moose.ChemCompt):
            compt = layoutPt.qGraCompt[moose.element(mobj)]
            updateCompartmentSize(compt)

    elif string == "Reac":
        posWrtComp = (itemAtView.mapFromScene(pos)).toPoint()
        reacObj = moose.Reac(mobj.path + '/' + string_num)
        reacinfo = moose.Annotator(reacObj.path + '/info')
        qGItem = kkitQGraphics.ReacItem(reacObj, itemAtView)
        qGItem.setDisplayProperties(posWrtComp.x(), posWrtComp.y(), "white",
                                    "white")
        layoutPt.mooseId_GObj[reacObj] = qGItem
        qGItem.dopped.emit()
        #  view.emit(QtCore.SIGNAL("dropped"), reacObj)
        kkitUtil.setupItem(modelpath.path, layoutPt.srcdesConnection)
        layoutPt.drawLine_arrow(False)
        #Dropping is on compartment then update Compart size
        if isinstance(mobj, moose.ChemCompt):
            compt = layoutPt.qGraCompt[moose.element(mobj)]
            updateCompartmentSize(compt)
        x, y = roundoff(qGItem.scenePos(), layoutPt)
        reacinfo.x = x
        reacinfo.y = y

    elif string == "StimulusTable":
        posWrtComp = (itemAtView.mapFromScene(pos)).toPoint()
        tabObj = moose.StimulusTable(mobj.path + '/' + string_num)
        tabinfo = moose.Annotator(tabObj.path + '/info')
        qGItem = kkitQGraphics.TableItem(tabObj, itemAtView)
        qGItem.setDisplayProperties(posWrtComp.x(), posWrtComp.y(),
                                    QtGui.QColor('white'),
                                    QtGui.QColor('white'))
        layoutPt.mooseId_GObj[tabObj] = qGItem
        qGItem.dropped.emit()
        #  view.emit(QtCore.SIGNAL("dropped"), tabObj)
        kkitUtil.setupItem(modelpath.path, layoutPt.srcdesConnection)
        layoutPt.drawLine_arrow(False)
        # Dropping is on compartment then update Compart size
        if isinstance(mobj, moose.ChemCompt):
            compt = layoutPt.qGraCompt[moose.element(mobj)]
            updateCompartmentSize(compt)
        x, y = roundoff(qGItem.scenePos(), layoutPt)
        tabinfo.x = x
        tabinfo.y = y

    elif string == "Function":
        posWrtComp = (itemAtView.mapFromScene(pos)).toPoint()
        funcObj = moose.Function(mobj.path + '/' + string_num)
        funcinfo = moose.Annotator(funcObj.path + '/info')
        #moose.connect( funcObj, 'valueOut', mobj ,'setN' )
        poolclass = ["ZombieBufPool", "BufPool"]
        comptclass = ["CubeMesh", "cyclMesh"]

        if mobj.className in poolclass:
            funcParent = layoutPt.mooseId_GObj[moose.element(mobj.path)]
        elif mobj.className in comptclass:
            funcParent = layoutPt.qGraCompt[moose.element(mobj)]
            posWrtComp = funcParent.mapFromScene(pos).toPoint()
        elif mobj.className in "Neutral":
            funcParent = layoutPt.qGraGrp[moose.element(mobj)]

        qGItem = kkitQGraphics.FuncItem(funcObj, funcParent)
        qGItem.setDisplayProperties(posWrtComp.x(), posWrtComp.y(),
                                    QtGui.QColor('red'), QtGui.QColor('green'))
        layoutPt.mooseId_GObj[funcObj] = qGItem
        qGItem.dropped.emit()
        #  view.emit(QtCore.SIGNAL("dropped"), funcObj)
        kkitUtil.setupItem(modelpath.path, layoutPt.srcdesConnection)
        layoutPt.drawLine_arrow(False)
        #Dropping is on compartment then update Compart size
        mooseCmpt = findCompartment(mobj)
        if isinstance(mooseCmpt, moose.ChemCompt):
            compt = layoutPt.qGraCompt[moose.element(mooseCmpt)]
            updateCompartmentSize(compt)
        x, y = roundoff(qGItem.scenePos(), layoutPt)
        funcinfo.x = x
        funcinfo.y = y

    elif string == "Enz" or string == "MMenz":
        # FIXME: If 2 enz has same pool parent, then pos of the 2nd enz shd be
        # displaced by some position, need to check how to deal with it
        posWrtComp = pos
        if ((mobj.parent).className == "Enz"):
            QtGui.QMessageBox.information(
                None, "Drop Not possible",
                "'{}' has to have Pool as its parent and not Enzyme Complex".
                format(string), QtGui.QMessageBox.Ok)
            return None
        else:
            enzparent = findCompartment(mobj)
            parentcompt = layoutPt.qGraCompt[enzparent]
        if string == "Enz":
            enzObj = moose.Enz(moose.element(mobj).path + '/' + string_num)
            enzinfo = moose.Annotator(enzObj.path + '/info')
            moose.connect(enzObj, 'enz', mobj, 'reac')
            qGItem = kkitQGraphics.EnzItem(enzObj, parentcompt)
            layoutPt.mooseId_GObj[enzObj] = qGItem
            posWrtComp = pos
            bgcolor = kkitUtil.getRandColor()
            qGItem.setDisplayProperties(posWrtComp.x(),
                                        posWrtComp.y() - 40,
                                        QtGui.QColor('green'), bgcolor)
            x, y = roundoff(qGItem.scenePos(), layoutPt)
            enzinfo.x = x
            enzinfo.y = y
            enzinfo.color = str(bgcolor.name())
            enzinfo.textColor = str(QtGui.QColor('green').name())
            moose.Annotator(enzinfo)
            Enz_cplx = enzObj.path + '/' + string_num + '_cplx'
            cplxItem = moose.Pool(Enz_cplx)
            moose.Annotator(cplxItem.path + '/info')
            qGEnz = layoutPt.mooseId_GObj[enzObj]
            kkitQGraphics.CplxItem(cplxItem, qGEnz)
            layoutPt.mooseId_GObj[cplxItem] = qGItem
            enzboundingRect = qGEnz.boundingRect()
            moose.connect(enzObj, 'cplx', cplxItem, 'reac')
            qGItem.setDisplayProperties(int(enzboundingRect.height() / 2),
                                        enzboundingRect.height() - 40,
                                        QtGui.QColor('white'),
                                        QtGui.QColor('white'))
            qGItem.dropped.emit()
            #  view.emit(QtCore.SIGNAL("dropped"), enzObj)
        else:
            enzObj = moose.MMenz(mobj.path + '/' + string_num)
            enzinfo = moose.Annotator(enzObj.path + '/info')
            moose.connect(mobj, "nOut", enzObj, "enzDest")
            qGItem = kkitQGraphics.MMEnzItem(enzObj, parentcompt)
            posWrtComp = pos
            bgcolor = kkitUtil.getRandColor()
            qGItem.setDisplayProperties(posWrtComp.x(),
                                        posWrtComp.y() - 30,
                                        QtGui.QColor('green'), bgcolor)
            enzinfo.color = str(bgcolor.name())
            layoutPt.mooseId_GObj[enzObj] = qGItem
            qGItem.dropped.emit()
            #  view.emit(QtCore.SIGNAL("dropped"), enzObj)
            x, y = roundoff(qGItem.scenePos(), layoutPt)
            enzinfo.x = x
            enzinfo.y = y
        kkitUtil.setupItem(modelpath.path, layoutPt.srcdesConnection)
        layoutPt.drawLine_arrow(False)

        # Dropping is on compartment then update Compart size
        if isinstance(enzparent, moose.ChemCompt):
            updateCompartmentSize(parentcompt)
    if view.iconScale != 1:
        view.updateScale(view.iconScale)


def createObj(scene, view, modelpath, string, pos, layoutPt):
    event_pos = pos
    num = 0
    ret_string = " "
    pos = view.mapToScene(event_pos)
    itemAt = view.sceneContainerPt.itemAt(float(pos.x()), float(pos.y()), QtGui.QTransform())
    moose.wildcardFind(modelpath + '/##[ISA=ChemCompt]')
    moose.mooseDeleteChemSolver(modelpath)
    mobj = ""

    if itemAt != None:
        itemAtView = view.sceneContainerPt.itemAt(view.mapToScene(event_pos))
        itemClass = type(itemAtView).__name__
        if (itemClass == 'QGraphicsRectItem'):
            mobj = itemAtView.parentItem().mobj
        elif (itemClass == 'QGraphicsSvgItem'):
            mobj = itemAtView.parent().mobj
        else:
            mobj = itemAtView.mobj

    if string == "CubeMesh" or string == "CylMesh":
        ret_string, num = findUniqId(moose.element(modelpath), "Compartment",
                                     0)
        comptexist = moose.wildcardFind(modelpath + '/##[ISA=ChemCompt]')
        if not len(comptexist):
            if itemAt != None:
                QtGui.QMessageBox.information(
                    None, 'Drop Not possible',
                    "'{}' currently single compartment model building is allowed"
                    .format(string), QtGui.QMessageBox.Ok)
                return False
            else:
                mobj = moose.element(modelpath)
                return True
        else:
            QtGui.QMessageBox.information(
                None, 'Drop Not possible',
                '\'{newString}\' currently single compartment model building is allowed'
                .format(newString=string), QtGui.QMessageBox.Ok)
            return False

    elif string == "Pool" or string == "BufPool" or string == "Reac" or string == "StimulusTable":
        if itemAt == None:
            QtGui.QMessageBox.information(
                None, 'Drop Not possible',
                '\'{newString}\' has to have compartment as its parent'.format(
                    newString=string), QtGui.QMessageBox.Ok)
            return False
        else:
            mobj = findCompartment(mobj)
            ret_string, num = findUniqId(mobj, string, num)
            return True

    elif string == "Function":
        #mobj = findCompartment(mobj)
        ret_string, num = findUniqId(mobj, string, num)
        return True
    elif string == "Enz" or string == "MMenz":
        if itemAt != None:
            if ((mobj).className != "Pool" and (mobj).className != "BufPool"):
                QtGui.QMessageBox.information(
                    None, 'Drop Not possible',
                    "'{}' has to have Pool as its parent".format(string),
                    QtGui.QMessageBox.Ok)
                return False
            else:
                ret_string, num = findUniqId(mobj, string, num)
                return True
        else:
            QtGui.QMessageBox.information(
                None, 'Drop Not possible',
                "'{}' has to have Pool as its parent".format(string),
                QtGui.QMessageBox.Ok)
            return False

    if ret_string != " ":
        checkCreate(scene, view, modelpath, mobj, string, ret_string, num,
                    event_pos, layoutPt)


def roundoff(scenePos, layoutPt):
    xtest = scenePos.x() / layoutPt.defaultScenewidth
    xroundoff = round(xtest, 1)

    ytest = scenePos.y() / layoutPt.defaultSceneheight
    yroundoff = round(ytest, 1)

    return (xroundoff, yroundoff)


def findUniqId(mobj, string, num):
    if num == 0:
        path = mobj.path + '/' + string
    else:
        path = mobj.path + '/' + string + str(num)
    if not moose.exists(path):
        return (string, num)
    else:
        num += 1
        return (findUniqId(mobj, string, num))


def findCompartment(mooseObj):
    if mooseObj.path == '/':
        return None
    elif isinstance(mooseObj, kkitQGraphics.ChemCompt):
        return (mooseObj)
    else:
        return findCompartment(moose.element(mooseObj.parent))
