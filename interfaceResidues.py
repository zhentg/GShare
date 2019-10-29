checkIdx=1
def check():
    global checkIdx
    print('check',checkIdx)
    checkIdx+=1

def residueSA2bfactor(protein):
    """
    This function will write the SASA of a residue to the b-factor property of alpha carbon of the residue
    This function takes a long time to run, and need to be optimized.
    
    Author: Zhenting Gao
    Update: 7/9/2019
    """
    cmd.get_area(protein, load_b=1) #;check();print(protein)
    sel1=protein+' and name ca+P' #P is the root atom for a DNA residue
    #print sel1
    #objs=cmd.get_object_list(sel1)
    #https://pymolwiki.org/index.php/Get_Models
    atoms=cmd.get_model(sel1) #;check()
    for calpha in atoms.atom:
        residueObj=protein+" and chain "+calpha.chain+' and resn '+calpha.resn+' and resi '+calpha.resi
        #print("original b-factor is",calpha.b)
        #print residueObj
        #resSASA=cmd.get_area(residueObj)
        resSASA = []
        atomsOfRes=cmd.get_model(residueObj)
        for atom in atomsOfRes.atom:
            resSASA.append(atom.b)
        cmd.alter(residueObj+" and name ca+P", 'b='+str(sum(resSASA)))
        #print(residueObj,sum(resSASA))
        

def interfaceResidues(cmpx, gA='c. A', gB='c. B', cutoff=1.0, selName="interface",output='csv'):
    """
    Example:
    interfaceResidues complex, c. A, c. B
    
    interfaceResidues -- finds 'interface' residues between two chains in a complex.
    https://pymolwiki.org/index.php/InterfaceResidues
    PARAMS
        cmpx
            The complex containing gA and gB
        
        gA
            The first group in which we search for residues at an interface
            with gB
        
        gB
            The second group in which we search for residues at an interface
            with gA
        
        cutoff
            Residues whose dASA from the complex to single chain is greater than this cutoff are considered as interface residues. Zero    keeps all residues.
            
        selName
            The name of the selection to return.
            
    RETURNS
        * An array of values is returned where each value is:
            ( 'model','resiName','residue id','dSASA','SASAInCplx','BuriedSASA%' )
        * An csv file contains all the output parameters:
            ( 'model','resiName','residue id','dSASA','SASAInCplx','BuriedSASA%')
        * A selection of interface residues is created and named
            depending on what you passed into selName
            
    NOTES
        If you have two chains that are not from the same PDB that you want
        to complex together, use the create command like:
            create myComplex, pdb1WithChainA or pdb2withChainX
        then pass myComplex to this script like:
            interfaceResidues myComlpex, c. A, c. X
            
        This script calculates the area of the complex as a whole.  Then,
        it separates the two chains that you pass in through the arguments
        gA and gB, alone.  Once it has this, it calculates the difference
        and any residues ABOVE the cutoff are called interface residues.
            
    AUTHOR:
        Jason Vertrees, 2009.
        Zhenting Gao, 2019
    """
    from pymol import cmd, stored
    import csv
    #import numpy as np  #add chain name as a suffix
    import time

    start = time.time()

    # Save user's settings, before setting dot_solvent
    oldDS = cmd.get("dot_solvent")
    #Dot_solvent must be set to 1, otherwise the surface area change will not be detected in most cases (Zhenting on 12/24/2018)
    cmd.set("dot_solvent", 1)
    
    # set some string names for temporary objects/selections
    tempC, selName1 = "tempComplex", selName + "2"
    #print selName1
    groupA, groupB = "groupA", "groupB"
    
    # operate on a new object & turn off the original
    # limiting the selected residues to those that are within 6 A of each other, this will reduce the calculation time to 1/10
    # 6A is used based on the example of 1qox chain I and J (Zhenting on 12/25/2018)
    cmd.create(tempC, cmpx + " and ( (byres ((" + gA + ") a. 6 )) or (byres ((" + gB + ") a. 6)))")
    cmd.disable(cmpx)
    
    # remove cruft and irrelevant atoms. Water and ligands are all removed
    cmd.remove(tempC + " and not (polymer and (%s or %s))" % (gA, gB))
    
    print("1. Get the SASA of the intact complex")
    residueSA2bfactor(tempC)
    #cmd.get_area(tempC, load_b=1)
    # copy the areas from the loaded b to the "q" field.
    cmd.alter(tempC+" and name ca+P", 'q=b')
    
    print("2. Extract the two groups and calculate the SASA of the separate objects")
    # note: the q fields are copied to the new objects
    # groupA and groupB
    cmd.create(groupA, tempC + " and (" + gA + ")")
    cmd.create(groupB, tempC + " and (" + gB + ")")
    residueSA2bfactor(groupA)
    residueSA2bfactor(groupB)
    #cmd.get_area(groupA, load_b=1)
    #cmd.get_area(groupB, load_b=1)
    
    # update the chain-only objects w/the difference
    cmd.alter( "(%s or %s) and name ca+P" % (groupA,groupB), "b=b-q" )
    
    #print  "The calculations are done.  Now, all we need to"
    # do is to determine which residues are over the cutoff
    # and save them.
    stored.r, rVal, seen = [], [], []
    cmd.iterate('(%s or %s) and name ca+P' % (groupA, groupB), 'stored.r.append((model,chain,resn,resi,b,q))')

    cmd.enable(cmpx)
    cmd.select(selName1, 'none')
    cutoff=float(cutoff)
    for (model,chain,resn,resi,diff,SASAInCplx) in stored.r:
        key=resi+"-"+model
        if abs(diff)>=cutoff:
            #if key in seen: continue
            #else: seen.append(key)
            rVal.append( (model,chain,resn,resi,diff,SASAInCplx, 100*diff/(diff+SASAInCplx)) )
            # expand the selection here; I chose to iterate over stored.r instead of
            # creating one large selection b/c if there are too many residues PyMOL
            # might crash on a very large selection.  This is pretty much guaranteed
            # not to kill PyMOL; but, it might take a little longer to run.
            cmd.select( selName1, selName1 + " or (%s and i. %s and c. %s)" % (model,resi,chain))

    # this is how you transfer a selection to another object.
    cmd.select(selName, cmpx + " in " + selName1)
    # clean up after ourselves
    cmd.delete(selName1)
    cmd.delete(groupA)
    cmd.delete(groupB)
    cmd.delete(tempC)
    # show the selection
    cmd.enable(selName)
    
    # reset users settings
    cmd.set("dot_solvent", oldDS)
    #chainArray=np.array(rVal) #add chain name as a suffix
    if output=="":
        print('group','chain','resiName','residue id','dSASA','SASAInCplx','BuriedSASA%')
        print(rVal)
    if output=="csv":
        with open('interfaceResidues'+cmpx[:5]+'.csv', "wb") as csv_file:
            writer = csv.writer(csv_file, dialect='excel')
            writer.writerow(['group','chain','resiName','residue id','dSASA','SASAInCplx','BuriedSASA%'])
            for line in rVal:
                writer.writerow(line)
        print( "3. Results saved in interfaceResidues"+cmpx[:5]+".csv")
    end = time.time()
    print("Finished in %.1f s" % (end - start))
    return rVal

cmd.extend("interfaceResidues", interfaceResidues)
