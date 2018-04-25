import os
from osgeo import ogr

def get_pointfid2q(lyrsrcp,qfieldnames):
    pointfid2q = {}
    for point in lyrsrcp:
        subdict = {}
        pointfid = point.GetFID()
        for qfieldname in qfieldnames:
            subdict[qfieldname] = point.GetField(qfieldname)
        pointfid2q[pointfid] = subdict
    return pointfid2q

def get_linefid2q_pointsatdownstreamend(lyrsrcl,lyrsrcp,pointfid2q):
    linefid2q = {}
    linefid2pointfid = {}
    for line in lyrsrcl:
        subdict = {}
        linefid = line.GetFID()
        geomline = line.GetGeometryRef().Clone()
        coordslastvertex = geomline.GetPoint(geomline.GetPointCount()-1)
        pointatlastvertex = ogr.Geometry(ogr.wkbPoint)
        pointatlastvertex.AddPoint(coordslastvertex[0], coordslastvertex[1])
        #print(pointatlastvertex)
        bufferatlastvertex = pointatlastvertex.Buffer(1)
        #print(bufferatlastvertex)
        lyrsrcp.SetSpatialFilter(bufferatlastvertex)
        mindist = 999999999999999999999999999999
        bestmatch = None
        pointfid = None
        for pointcandidate in lyrsrcp:
            geompointcandidate = pointcandidate.GetGeometryRef().Clone()
            distance = geompointcandidate.Distance(pointatlastvertex)
            #print(distance)
            if distance < mindist:
                pointfid = pointcandidate.GetFID()
                mindist = distance
            coordspoint = geompointcandidate.GetPoint()
        linefid2pointfid[linefid] = pointfid
        try:
            linefid2q[linefid] = pointfid2q[pointfid]
        except:
            continue
    return linefid2q

def get_linefid2q_pointsatupstreamend(lyrsrcl,lyrsrcp,pointfid2q):
    linefid2q = {}
    linefid2pointfid = {}
    for line in lyrsrcl:
        subdict = {}
        linefid = line.GetFID()
        geomline = line.GetGeometryRef().Clone()
        coordsfirstvertex = geomline.GetPoint(0)
        pointatfirstvertex = ogr.Geometry(ogr.wkbPoint)
        pointatfirstvertex.AddPoint(coordsfirstvertex[0], coordsfirstvertex[1])
        bufferatfirstvertex = pointatfirstvertex.Buffer(1)
        lyrsrcp.SetSpatialFilter(bufferatfirstvertex)
        mindist = 999999999999999999999999999999
        bestmatch = None
        pointfid = None
        for pointcandidate in lyrsrcp:
            geompointcandidate = pointcandidate.GetGeometryRef().Clone()
            distance = geompointcandidate.Distance(pointatfirstvertex)
            if distance < mindist:
                pointfid = pointcandidate.GetFID()
                mindist = distance
            coordspoint = geompointcandidate.GetPoint()
        linefid2pointfid[linefid] = pointfid
        try:
            linefid2q[linefid] = pointfid2q[pointfid]
        except:
            continue
    return linefid2q
    
def write_nested_dict_to_csv(linefid2q, outfilename, qfieldnames):
    with open(outfilename,"w") as f:
        f.write("linefid,"+",".join(qfieldnames)+"\n")
        for linefid,qcategories in linefid2q.items():
            stringtowrite = str(linefid) + ","
            for qfieldname in qfieldnames:
                stringtowrite += str(qcategories[qfieldname])
                stringtowrite += ","
            stringtowrite += "\n"
            f.write(stringtowrite)
    f.close()           
 
def main():
    for i in range (1 , 3):
        
        driver = ogr.GetDriverByName("ESRI Shapefile")
        datasrcl = driver.Open("Split.shp", 0)       #? Edit for line shapefile name
        lyrsrcl = datasrcl.GetLayerByName("Split")   #? Edit for line shapefile name (enter the name without extension here)
        projl = lyrsrcl.GetSpatialRef()
        datasrcp = driver.Open("final_RAS.shp", 0)      #? Edit for point shapefile name
        lyrsrcp = datasrcp.GetLayerByName("final_RAS")  #? Edit for point shapefile name (enter the name without extension here)
        projp = lyrsrcp.GetSpatialRef()
        #print(projl[0])
        #print(projp[0])
        #assert projl[0] == projp[0]
        qfieldnames = ["Q2_1","Q5_1","Q10_1","Q50_1","Q100_1","Q25","Q500_1","Q_100Plus","Q_100minus"]  #? Edit for q field names
        pointfid2q = get_pointfid2q(lyrsrcp,qfieldnames)
        if i==1 :
            linefid2q = get_linefid2q_pointsatupstreamend(lyrsrcl,lyrsrcp,pointfid2q)
            write_nested_dict_to_csv(linefid2q=linefid2q, outfilename="upstream.csv", qfieldnames=qfieldnames)
        else:
            linefid2q = get_linefid2q_pointsatdownstreamend(lyrsrcl,lyrsrcp,pointfid2q)
            write_nested_dict_to_csv(linefid2q=linefid2q, outfilename="downstream.csv", qfieldnames=qfieldnames)
        
    
    
    #print("\npointfid2q",pointfid2q)
    #print("\nlinefid2q",linefid2q)
    
if __name__ == "__main__":
    main()
