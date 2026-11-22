# -*- coding: utf-8 -*-
from OCC.Core.BRepMesh import BRepMesh_IncrementalMesh
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.TopAbs import TopAbs_FACE
from OCC.Core.BRep import BRep_Tool
from OCC.Core.TopLoc import TopLoc_Location
from OCC.Core.Bnd import Bnd_Box
from OCC.Core.BRepBndLib import brepbndlib

def extract_mesh_and_bounds(shapes, deflection=0.8):
    """对 OCC Shape 列表进行网格化并提取面片与三维包围盒。
    
    返回: (triangles, (xmin, ymin, zmin, xmax, ymax, zmax))
    """
    all_triangles = []
    total_box = Bnd_Box()

    for s in shapes:
        shape = s.shape if hasattr(s, 'shape') else s
        if shape is None or shape.IsNull():
            continue

        # 1. 计算三维包围盒
        brepbndlib.Add(shape, total_box)

        # 2. 局部增量网格剖分
        BRepMesh_IncrementalMesh(shape, deflection)
        exp = TopExp_Explorer(shape, TopAbs_FACE)
        while exp.More():
            face = exp.Current()
            loc = TopLoc_Location()
            triangulation = BRep_Tool.Triangulation(face, loc)
            if triangulation:
                trsf = loc.Transformation()
                nb_nodes = triangulation.NbNodes()
                nodes = [triangulation.Node(i).Transformed(trsf) for i in range(1, nb_nodes + 1)]
                nb_triangles = triangulation.NbTriangles()
                for i in range(1, nb_triangles + 1):
                    t = triangulation.Triangle(i)
                    n1, n2, n3 = t.Get()
                    p1 = (nodes[n1 - 1].X(), nodes[n1 - 1].Y(), nodes[n1 - 1].Z())
                    p2 = (nodes[n2 - 1].X(), nodes[n2 - 1].Y(), nodes[n2 - 1].Z())
                    p3 = (nodes[n3 - 1].X(), nodes[n3 - 1].Y(), nodes[n3 - 1].Z())
                    all_triangles.append([p1, p2, p3])
            exp.Next()

    if total_box.IsVoid():
        bounds = (-50.0, -50.0, -50.0, 50.0, 50.0, 50.0)
    else:
        bounds = total_box.Get()

    return all_triangles, bounds
