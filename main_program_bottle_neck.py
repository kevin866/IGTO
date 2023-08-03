#AUTHOR : YASA VISWAMBHAR REDDY
#MATRICULATION NUMBER : 65074
#Personal Programming Project
#--------------------------------------------------------------------------#
#BOTTLE NECKS - Python file used for time analysis 
#--------------------------------------------------------------------------#
# NO commenting is done as all function used in IGTO are placed in a single file to perform time analysis
#each function as two global variables
#1- to calculate number of times the function was called
#2- to calculate the time taken by the function
from inputs import *
import matplotlib.pyplot as plt
import time
import os
from boundary_conditions import BC_Switcher
from visulaization import mesh_vis
import pyvista as pv
from gridtoVTK import VTK
import sys
from time_analysis_variables import *
from plotting import time_analysis_plotting

def Folder(path): 
    global Folder_Count
    global Folder_ex_time
    start = time.time()
    try:
        if not os.path.exists(path):
            os.makedirs(path)
    except OSError:
        print('Error: Creating directory. ' + path)
    stop = time.time()
    execution_time = stop - start
    Folder_Count+=1
    Folder_ex_time+=execution_time


def knot_index(degree,U,knotvector):

    global knot_index_Count
    global knot_index_ex_time
    start = time.time()
    n=np.size(knotvector)-1

    if U in knotvector[(degree+1):(n-degree)]:
        for i, j in enumerate(knotvector):
            if j == U:
                  stop = time.time()
                  knot_index_ex_time+= stop - start
                  knot_index_Count+=1  
                  return i
    else:   

        if degree>0:
            n=np.size(knotvector)
            index=n-degree-1
            if U == knotvector[index+1]:
                  stop = time.time()
                  knot_index_ex_time+= stop - start
                  knot_index_Count+=1
                  return (index)
            if U == knotvector[degree]:
                  stop = time.time()
                  knot_index_ex_time+= stop - start
                  knot_index_Count+=1
                  return (degree)
            for i,j in enumerate(knotvector):
                if U>j and U<knotvector[i+1]:
                        stop = time.time()
                        knot_index_ex_time+= stop - start
                        knot_index_Count+=1
                        return(i)



def bspline_basis(knot_index,degree,U,knotvector):

    global bspline_basis_Count
    global bspline_basis_ex_time
    start = time.time()

    if degree >0 :
        alpha=np.zeros(degree+1)
        beta=np.zeros(degree+1)
        Basis=np.zeros(degree+1)
        Basis[0]=1.0 

        for i in range(1,degree+1):
            value=0
            alpha[i]=U-knotvector[(knot_index-i+1)]
            beta[i]=knotvector[knot_index+i]-U  
            j=0

            while j<i:
                if (beta[j+1]+alpha[i-j])==0:
                     temp=0
                     Basis[j] = value+(beta[j+1]*temp)
                     value = alpha[i-j]*temp
                     Basis[i] = value
                     j=j+1
                else:
                    temp= Basis[j]/(beta[j+1]+alpha[i-j])
                    Basis[j] = value+(beta[j+1]*temp)
                    value = alpha[i-j]*temp
                    Basis[i] = value
                    j=j+1

    else:
        Basis=np.zeros(degree+1)
        if U<=knotvector[knot_index+1] and U> knotvector[knot_index]:
            Basis[0]=1
        else:
            Basis[0]=0

    stop = time.time()
    bspline_basis_ex_time= (stop - start)
    bspline_basis_Count+=1
    return Basis



def derbspline_basis(knot_index,degree,U,knotvector):

    global derbspline_basis_Count
    global derbspline_basis_ex_time
    start = time.time()
    if degree>=0:
        derBasis=np.zeros(degree+1)
        if  knot_index<degree or knot_index>(int(len(knotvector)-degree)):
            derBasis=np.zeros(degree+1)
            return derBasis
        else:
            alpha=np.zeros(degree+1)
            beta=np.zeros(degree+1)
            Basis=np.zeros((degree+1,degree+1))
            if U>knotvector[degree] and U<=knotvector[len(knotvector)-degree]:
                Basis[0,0]=1.0
            else:
                Basis[0,0]=0
            for i in range(1,degree+1):
                alpha[i]=U-knotvector[knot_index-i+1]
                beta[i]=knotvector[knot_index+i]-U 
                saved=0.0
                for j in range(0,i):
                    Basis[i,j]=beta[j+1]+alpha[i-j]    
                    temp= Basis[j,i-1]/(beta[j+1]+alpha[i-j])
                    Basis[j,i] = saved+(beta[j+1]*temp)
                    saved = alpha[i-j]*temp
                Basis[i,i] = saved  
        for r in range(0,degree+1):
            if (r>=1):
                derBasis[r]=Basis[r-1,degree-1]/Basis[degree,r-1]
            if (r<=degree-1):
                derBasis[r]=derBasis[r]-(Basis[r,degree-1]/Basis[degree,r])
        derBasis *=degree
    stop = time.time()
    derbspline_basis_ex_time+= (stop - start)
    derbspline_basis_Count+=1
    return np.array(derBasis)


def trilinear_der(Ux,Uy,Uz,weights,xdegree,xknotvector,ydegree,yknotvector,zdegree,zknotvector):

    global trilinear_der_Count
    global trilinear_der_ex_time
    start = time.time()
    x_index=knot_index(xdegree,Ux,xknotvector)
    y_index=knot_index(ydegree,Uy,yknotvector)
    z_index=knot_index(zdegree,Uz,zknotvector)


    Nx=bspline_basis(x_index,xdegree,Ux,xknotvector)
    Ny=bspline_basis(y_index,ydegree,Uy,yknotvector)
    Nz=bspline_basis(z_index,zdegree,Uz,zknotvector)


    DNx=derbspline_basis(x_index,xdegree,Ux,xknotvector)
    DNy=derbspline_basis(y_index,ydegree,Uy,yknotvector)
    DNz=derbspline_basis(z_index,zdegree,Uz,zknotvector)


    W=0
    W_dx=0
    W_dy=0
    W_dz=0
    p=0
    windex=0

    for k in range(zdegree+1):
        for j in range(ydegree+1):
            for i in range(xdegree+1):
                W+=Nx[i]*Ny[j]*Nz[k]*weights[windex]
                W_dx+=DNx[i]*Ny[j]*Nz[k]*weights[windex]
                W_dy+=Nx[i]*DNy[j]*Nz[k]*weights[windex]
                W_dz+=Nx[i]*Ny[j]*DNz[k]*weights[windex]
                windex+=1

    dR_dx=np.zeros((xdegree+1)*(ydegree+1)*(zdegree+1))
    dR_dy=np.zeros((xdegree+1)*(ydegree+1)*(zdegree+1))
    dR_dz=np.zeros((xdegree+1)*(ydegree+1)*(zdegree+1))
    R=np.zeros((xdegree+1)*(ydegree+1)*(zdegree+1))

    w=0
    windex=0

    if W==0:
        dR_dx=np.zeros((xdegree+1)*(ydegree+1)*(zdegree+1))
        dR_dy=np.zeros((xdegree+1)*(ydegree+1)*(zdegree+1))
        dR_dz=np.zeros((xdegree+1)*(ydegree+1)*(zdegree+1))
        R=np.zeros((xdegree+1)*(ydegree+1)*(zdegree+1))
    else:
        for k in range(zdegree+1):
            for j in range(ydegree+1):
                for i in range(xdegree+1):
                    w=weights[windex]/(W*W)
                    R[p]=(Nx[i]*Ny[j]*Nz[k]*W*w)
                    dR_dx[p]=(DNx[i]*Ny[j]*Nz[k]*W-Nx[i]*Ny[j]*Nz[k]*W_dx)*w
                    dR_dy[p]=(Nx[i]*DNy[j]*Nz[k]*W-Nx[i]*Ny[j]*Nz[k]*W_dy)*w
                    dR_dz[p]=(Nx[i]*Ny[j]*DNz[k]*W-Nx[i]*Ny[j]*Nz[k]*W_dz)*w
                    p=p+1
                    windex+=1
    stop = time.time()
    trilinear_der_ex_time+= (stop - start)
    trilinear_der_Count+=1
    return [dR_dx,dR_dy,dR_dz,R]


def elementorder(numx,numy,numz):
    index=0
    el_order=np.zeros((numx,numz,numy))
    for i in range(numz):
        for j in range(numy):
            for k in range(numx):
                el_order[k,i,j]=index
                index+=1
    return el_order



def knot_connectivity(n,p,q,knotconnectivityU,knotconnectivityV,knotconnectivityW):

    index=np.zeros((n*p*q,3))
    count=0
    for k in range(len(knotconnectivityW)):
        for j in range(len(knotconnectivityV)):
            for i in range(len(knotconnectivityU)):
                index[count,:]=[i,j,k]
                count+=1
    index=index.astype(int)
    return  index


def controlpointassembly(n,p,q,nU,nV,nW,xdegree,ydegree,zdegree,knotconnectivityU,knotconnectivityV,knotconnectivityW):

    elements_assembly=np.zeros(((nU*nV*nW),(xdegree+1)*(ydegree+1)*(zdegree+1)))
    elements_order=elementorder(n,p,q)
    a=0 
    for i in range(nW):
        for j in range(nV):
            for k in range(nU):
                c=0
                for l in range(len(knotconnectivityW[i,:])):
                    for m in range(len(knotconnectivityV[j,:])):
                        for n in range(len(knotconnectivityU[k,:])):
                            elements_assembly[a,c]=elements_order[knotconnectivityU[k,n],knotconnectivityW[i,l], knotconnectivityV[j,m]]
                            c+=1
                a+=1         
    elements_assembly=elements_assembly.astype(int)
    return elements_assembly


def gauss_quadrature(p,q,r):

    global gauss_quadrature_Count
    global gauss_quadrature_ex_time
    start = time.time()

    if p>=5:
        p=4
    else:
        p=p+1
    if q>=5:
        q=q+1
    else:
        q=q+1
    if r>=5:
        r=4
    else:
        r=r+1
    
    [xgauss_points,xweights]=np.polynomial.legendre.leggauss(p)
    [ygauss_points,yweights]=np.polynomial.legendre.leggauss(q)
    [zgauss_points,zweights]=np.polynomial.legendre.leggauss(r)
    gausspoints=np.zeros((p*q*r,3))
    weights=np.zeros(p*q*r)
    n=0
    for i in range(r):
        for j in range(q):
            for k in range(p):
                gausspoints[n,:]=[xgauss_points[k],ygauss_points[j],zgauss_points[i]]
                weights[n]=xweights[k]*yweights[j]*zweights[i]
                n+=1
    
    stop = time.time()
    gauss_quadrature_ex_time += (stop - start)
    gauss_quadrature_Count+=1
    return gausspoints,weights



def unittoparametric(gauss_point,span):
    global unittoparametric_Count
    global unittoparametric_ex_time
    start = time.time()

    unit_para=(np.dot(0.5,((span[1]-span[0])*gauss_point+(span[1]+span[0]))))
    stop = time.time()
    unittoparametric_ex_time += (stop - start)
    unittoparametric_Count+=1
    return unit_para



def jacobian(Xi,Eta,Nta,Uspan,Vspan,Wspan,X,Y,Z,weights,xdegree,xknot_vector,ydegree,yknot_vector,zdegree,zknot_vector):

    global jacobian_Count
    global jacobian_ex_time
    start = time.time()

    DXi_dxi=0.5*(Uspan[1]-Uspan[0])
    DEta_dEta=0.5*(Vspan[1]-Vspan[0])
    DNta_dNta=0.5*(Wspan[1]-Wspan[0])
    det_jacobian2=DXi_dxi*DEta_dEta*DNta_dNta
    #pts=np.array([X,Y,Z])
    [dR_dxi,dR_deta,dR_dnta,nurbs]=trilinear_der(Xi,Eta,Nta,weights,xdegree,xknot_vector,ydegree,yknot_vector,zdegree,zknot_vector)
    DR_DXi=np.array([dR_dxi,dR_deta,dR_dnta])
    #jacobian12=pts@ np.transpose(DR_DXi)
    jacobian1=np.zeros((3,3))

    dRxi_dx=np.dot(dR_dxi,X)
    jacobian1[0,0]=dRxi_dx
    
    dRxi_dy=np.dot(dR_dxi,Y)
    jacobian1[0,1]=dRxi_dy
    
    dRxi_dz=np.dot(dR_dxi,Z)
    jacobian1[0,2]=dRxi_dz
    
    dReta_dx=np.dot(dR_deta,X)
    jacobian1[1,0]=dReta_dx
    
    dReta_dy=np.dot(dR_deta,Y)
    jacobian1[1,1]=dReta_dy
    
    dReta_dz=np.dot(dR_deta,Z)
    jacobian1[1,2]=dReta_dz
    
    dRNta_dx=np.dot(dR_dnta,X)
    jacobian1[2,0]=dRNta_dx
    
    dRNta_dy=np.dot(dR_dnta,Y)
    jacobian1[2,1]=dRNta_dy
    
    dRNta_dz=np.dot(dR_dnta,Z)
    jacobian1[2,2]=dRNta_dz
    #jacobian1=jacobian12
    det_jacobian1=np.linalg.det(jacobian1)

    #print(jacobian1)
    stop = time.time()
    jacobian_ex_time += (stop - start)
    jacobian_Count+=1
    return jacobian1,det_jacobian1,det_jacobian2,DR_DXi,nurbs



def strain_displacement(Xi,Eta,Neta,jacobian1,det_jacobian1,DR_DXi,nurbs,nn):

    global strain_displacement_Count
    global strain_displacement_ex_time
    start = time.time()
    #if det_jacobian1==0:
    #    raise Exception("Jacobian cannot be zero")
    inverse_jacobian1=np.linalg.inv(jacobian1)
    DR_DX=np.matmul(inverse_jacobian1,DR_DXi)

    B=np.zeros((6,int(3*np.size(DR_DX,1))))
    R=np.zeros((3,int(3*np.size(DR_DX,1))))
    for i in range(int(np.size(DR_DX,1))):
        x=int(3*i)
        y=int(3*i+1)
        z=int(3*i+2)
        B[0,x]=DR_DX[0,i]
        B[1,y]=DR_DX[1,i]
        B[2,z]=DR_DX[2,i]
        B[3,x]=DR_DX[1,i]
        B[3,y]=DR_DX[0,i]
        B[4,y]=DR_DX[2,i]
        B[4,z]=DR_DX[1,i]
        B[5,x]=DR_DX[2,i]
        B[5,z]=DR_DX[0,i]
        R[0,x]=nurbs[i]
        R[0,y]=nurbs[i]
        R[2,z]=nurbs[i]
    #print(B)
    stop = time.time()
    strain_displacement_ex_time += (stop - start)
    strain_displacement_Count+=1
    return B,R

def Compliance_matrix(E=100000,v=0.3):

    global Compliance_matrix_Count
    global Compliance_matrix_ex_time
    start = time.time()

    C=np.zeros((6,6))
    C[0,0]=C[1,1]=C[2,2]=(E/((1+v)*(1-2*v)))*(1-v)
    C[3,3]=C[4,4]=C[5,5]=E/((1+v)*1)
    C[0,1]=C[0,2]=C[1,0]=C[2,0]=C[1,2]=C[2,1]=(E/((1+v)*(1-2*v)))*v

    stop = time.time()
    Compliance_matrix_ex_time += stop - start
    Compliance_matrix_Count+=1
    return C


def element_routine(X,Y,Z,weights,E,v,Uspan,Vspan,Wspan,xdegree,xknot_vector,ydegree,yknot_vector,zdegree,zknot_vector):
    global element_routine_Count
    global element_routine_ex_time
    start = time.time() 
    Gauss_points,gauss_weights=gauss_quadrature(xdegree,ydegree,zdegree)
    C=Compliance_matrix(E,v)
    Ke=np.zeros((3*((xdegree+1)*(ydegree+1)*(zdegree+1)),3*((xdegree+1)*(ydegree+1)*(zdegree+1))))
    nn=((xdegree+1)*(ydegree+1)*(zdegree+1))
    for i in range(len(gauss_weights)):
        gp=Gauss_points[i,:]
        Wt=gauss_weights[i]
        Xi=unittoparametric(gp[0],Uspan)
        Eta=unittoparametric(gp[1],Vspan)
        Neta=unittoparametric(gp[2],Wspan)
        [jacobian1,det_jacobian1,det_jacobian2,DR_DXi,nurbs]=jacobian(Xi,Eta,Neta,Uspan,Vspan,Wspan,X,Y,Z,weights,xdegree,xknot_vector,ydegree,yknot_vector,zdegree,zknot_vector)
        B,R=strain_displacement(Xi,Eta,Neta,jacobian1,det_jacobian1,DR_DXi,nurbs,nn)
        temp=np.transpose(B)@C
        Ke+=temp@B*(det_jacobian1*det_jacobian2*Wt)
    stop = time.time()
    element_routine_ex_time += (stop - start)
    element_routine_Count+=1
    return Ke,nurbs,R


def assemble(K_G,K_E,elindices,ncp,K_disp=False):
    global assemble_Count
    global assemble_ex_time
    start = time.time()  
    elindices=np.array(elindices)
    dof=3
    gindices=np.sort(np.concatenate((elindices*dof,dof*elindices+1,dof*elindices+2)))
    for i,ii in enumerate(gindices):
        for j,jj in enumerate(gindices):
            K_G[ii,jj]=K_G[ii,jj]+K_E[i,j]
    if K_disp:        
        print('Building Global Stiffness matrix \n')
    stop = time.time()
    assemble_ex_time += (stop - start)
    assemble_Count+=1
    return K_G


def apply_BC(F_E,fixed_dof,load_dof,P,abc_disp=False):
    global apply_BC_Count
    global apply_BC_ex_time
    start = time.time() 
    F_E[load_dof]=P
    reduced_F_E=np.delete(F_E,fixed_dof,axis=0)
    if abc_disp:
        print('Applying Boundary Conditions \n')
    stop = time.time()
    apply_BC_ex_time += (stop - start)
    apply_BC_Count+=1
    return reduced_F_E

def Knearestneighbours(rmin,nelx,nely,nelz):
    global Knearestneighbours_Count
    global Knearestneighbours_ex_time
    start = time.time() 

    nel=nelx*nely*nelz
    H=np.zeros((nel,nel))
    for i in range(nelz):
        for j in range(nely):
            for k in range(nelx):
                r=int(i*nelx*nely+j*nelx+k)
                imin=int(max(i-(np.ceil(rmin)-1),0))
                imax=int(min(i+np.ceil(rmin),nelz))
                jmin=int(max(j-(np.ceil(rmin)-1),0))
                jmax=int(min(j+np.ceil(rmin),nely))
                kmin=int(max(k-(np.ceil(rmin)-1),0))
                kmax=int(min(k+np.ceil(rmin),nelx))
                for ii in range(imin,imax): 
                    for jj in range(jmin,jmax):
                        for kk in range(kmin,kmax):
                            c= int(ii*nelx*nely+jj*nelx+kk)
                            distance=np.sqrt((i-ii)**2+(j-jj)**2+(k-kk)**2)
                            H[r,c]=np.maximum(0,(rmin-distance))
    H=np.array(H)
    DH=np.sum(H,1)
    stop = time.time()
    Knearestneighbours_ex_time += (stop - start)
    Knearestneighbours_Count+=1
    return H,DH  



def optimality_criteria(dfun,dCon,initial_X,constrain,H=None,DH=None,beta=0.1,oc_disp=True,g=1,tol=0.01,move=0.1,neta=0.5,initial_value=0,final_value=1e09):
    global optimality_criteria_Count
    global optimality_criteria_ex_time
    start = time.time() 

    X_new=np.zeros(len(initial_X))
    #X_filter=np.zeros(len(initial_X))
    X=np.array(initial_X)
    i=0
    max_iteration=150
    while i<=max_iteration:
        convergence_criteria=(final_value-initial_value)/(final_value+initial_value)

        #lagarian multiplier
        lamdba=0.5*(initial_value+final_value)
        #Bey
        Be=((-dfun/(dCon*lamdba))**neta)**g
        X_new[:]= np.maximum(0.0,np.maximum(X-move,np.minimum(1.0,np.minimum(X+move,X*Be))))
        #if H is not None:
        #    X_new=np.matmul(H,X_new/DH)
        #X_new=1-np.exp(-beta*X_filter)+X_filter*np.exp(-beta)
        update_condition=np.sum(X_new)
        #  bi-section algorthim updating lagaranian multiplier
        if update_condition>=constrain:
            initial_value=lamdba    
        else:
            final_value=lamdba
        i=i+1
        if convergence_criteria<=tol :#or (np.linalg.norm(abs(X_new-X_old)))>=1e-4:
            width=120
            if oc_disp:
                print('-'*width)
                fmt='{:^'+str(width)+'}'
                print(fmt.format('Optimiality Criterian'))
                print('.'*width)
                print('     exit_iter: %d    gray_filter(g):%f    lamdba:%f12      tot_vol:%f4     max_volume:%f4' %(i,g,lamdba,update_condition,constrain))  
                print('.'*width)
                stop = time.time()
                optimality_criteria_ex_time += (stop - start)
                optimality_criteria_Count+=1
            return X_new
        if i==(max_iteration-1):
            width=120
            if oc_disp:
                print('maximum iteration has reached, didnot converger')
                print('.'*width)
                fmt='{:^'+str(width)+'}'
                print(fmt.format('Optimiality Criterian'))
                print('.'*width)
                print('     exit_iter: %d        lamdba:%f12        tot_vol:%f4       max_volume:%f4' %(i,lamdba,update_condition,constrain))  
                print('*'*width)
                stop = time.time()
                optimality_criteria_ex_time += (stop - start)
                optimality_criteria_Count+=1
            return X_new

#def Moving_asymptoes

def Moving_asymptoes(dfun0,dcon,f0,c0,x0,x1,x2,L,U,loop,nel,vel,Xmin,Xmax,ma_disp,m=0.2,m_tol=0.1):
    
    
    global Moving_asymptoes_Count
    global Moving_asymptoes_ex_time
    start = time.time() 

    def Asymptoes(loop=loop,x0=x0,x1=x1,x2=x2,n=nel,Xmin=Xmin,Xmax=Xmax,L=L,U=U,move_tol_low=0.01,move_tol_high=10):
    
        global Asymptoes_Count
        global Asymptoes_ex_time
        start = time.time() 

        lower_value=np.ones(n)
        upper_value=np.ones(n)
        #iteration less then 3
        if loop<=2:
            lower_value=x0-0.5*(Xmax-Xmin)  
            upper_value=x0+0.5*(Xmax-Xmin)  
            #print(Lower,Upper,x)
            return lower_value,upper_value,x0
        else: #iteration greater then 3
            xval=x0  #current iteration value of x
            xold1=x1 #pervious iteration value of x (k-1)
            xold2=x2 #pervious iteration value of x (k-2)
            zzz = (xval-xold1)*(xold1-xold2)  
            gamma = np.ones(nel)
            gamma[np.where(zzz>0)] = 1.2      
            gamma[np.where(zzz<0)] = 0.7
            lower_value = xval-gamma*(xold1-L) 
            #print(Lower)
            upper_value = xval+gamma*(U-xold1)
            #print(Upper)
            lmin = xval-move_tol_high*(Xmax-Xmin) 
            lmax = xval-move_tol_low*(Xmax-Xmin) 
            umin = xval+move_tol_low*(Xmax-Xmin)  
            umax = xval+move_tol_high*(Xmax-Xmin) 
            lower_value = np.maximum(lower_value,lmin)  
            lower_value = np.minimum(lower_value,lmax) 
            upper_value = np.minimum(upper_value,umax)  
            upper_value = np.maximum(upper_value,umin)  
            
            stop = time.time()
            Asymptoes_ex_time += (stop - start)
            Asymptoes_Count+=1
        return lower_value,upper_value,x0
    
    def objective_constrains(x,Lower,Upper,dfun0=dfun0,f0=f0,Xmin=Xmin,Xmax=Xmax,tol=1e-5,tol1=0.001,tol2=1.001):
       
        global objective_constrains_Count
        global objective_constrains_ex_time
        start = time.time() 

        df_postive=np.maximum(dfun0,0)
        df_negative=np.maximum(-dfun0,0)
        #print(df_postive)
        Xd_inv=1/Xmax-Xmin
        UX=Upper-x
        
        LX=x-Lower
        
        p0=tol2*df_postive+tol1*df_negative+(tol*Xd_inv)
        #print('p0',p0)
        p=np.array([(UX**2)*p0]).T
        q0=tol1*df_postive+tol2*df_negative+(tol*Xd_inv)
        q=np.array([(LX**2)*q0]).T

        #print('p',p)
        #print('q',q)   
        stop = time.time()
        objective_constrains_ex_time += (stop - start)
        objective_constrains_Count+=1 
        return p,q

    def Minimizer_constrains(x,Lower,Upper,dcon=dcon,m=vel,c0=c0,Xmin=Xmin,Xmax=Xmax,tol=1e-5,tol1=0.001,tol2=1.001):
       
        global Minimizer_constrains_Count
        global Minimizer_constrains_ex_time
        start = time.time() 

        df_postive=np.maximum(dcon,0)
        df_negative=np.maximum(-dcon,0)
        
        Xd_inv=np.array([1/Xmax-Xmin]).T
        UX=np.array([Upper-x]).T
        LX=np.array([x-Lower]).T
        
        tol_vector=tol*np.ones((m,1)).T
        tol_matrix=np.dot(Xd_inv,tol_vector).T

        
        p0=tol2*df_postive+tol1*df_negative+tol_matrix
        
        UX_matrix=np.diag(((Upper-x)**2),0)
        LX_matrix=np.diag(((x-Lower)**2),0)
        
        p=(UX_matrix@p0.T).T
        #print('p',p)
        
        q0=tol1*df_postive+tol2*df_negative+tol_matrix
        q=(LX_matrix@q0.T).T
        #print('q',q)
        
        pr=np.dot(p,(1/UX))
        qr=np.dot(q,(1/LX))
        rc= c0-(pr+qr).T #S remove .T
        #print('rc',rc.T)
        stop = time.time()
        Minimizer_constrains_ex_time += (stop - start)
        Minimizer_constrains_Count+=1 
        return p,q,rc.T


    def prime_dual(L,U,alpha,beta,p0,q0,pc,qc,a,b,c,d,n=nel,m=vel,epsimin=1e-7):
        
        global prime_dual_Count
        global prime_dual_ex_time
        pd_start = time.time()

        def initial_condition(alpha=alpha,beta=beta,o=n,k=m,c=c):
            
            global initial_condition_Count
            global initial_condition_ex_time

            ic_start = time.time()

            x=np.array([0.5*(alpha+beta)]).T
            y=np.ones((k,1))
            z=np.array([[1.0]])
            #print(o,k)
            variable_vector=np.ones((o,1))
            minimizer_vector=np.ones((k,1))
            epsi=1
            lamda=minimizer_vector
            s=minimizer_vector
            Zee=z
            eta=np.maximum(1,1/(x-np.array([alpha]).T))
            neta=np.maximum(1,1/(((np.array([beta]).T)-x)))
            nu=np.maximum(lamda,c*0.5)
            ic_stop = time.time()
            initial_condition_ex_time += (ic_stop - ic_start)
            initial_condition_Count+=1 
            return x,y,z,epsi,lamda,s,Zee,eta,neta,nu,variable_vector,minimizer_vector
    
        x,y,z,epsi,lamda,s,Zeta,eta,neta,nu,variable_vector,minimizer_vector=initial_condition()
        #print('initial_condition',initial_condition())
        def optimal_condtition(x,y,z,lamda,s,Zeta,eta,neta,nu,epsi,o='o',U=U,L=L,p0=p0,q0=q0,pc=pc,qc=qc,b=b,variable_vector=variable_vector,minimizer_vector=minimizer_vector):
            
            global optimal_condtition_Count
            global optimal_condtition_ex_time

            oc_start = time.time()

            #5.5
            UX=np.array([U]).T-x
            LX=x-np.array([L]).T
            #print(pc.T*lamda)
            plamda=p0+np.dot(pc.T,lamda)
                #print('plamda',plamda)
            qlamda=q0+np.dot(qc.T,lamda)
                #5.4
            g=np.dot(pc,(1/(UX)))+np.dot(qc,(1/(LX)))
            dphi_dx=(plamda/UX**2)-(qlamda/LX**2)
            #print('g',g)
            #print('dphi_dx',dphi_dx)
            #optimality conditions 5.7
            #print('eta',eta)
            #print('neta',neta)
            dl_dx=dphi_dx-eta+neta
            #print('dl_dx',dl_dx)
            dl_dy=c+d*y-lamda-nu
            dl_dz=a0-Zeta-np.dot(a.T,lamda)
            #print('dl_dy',dl_dy)
            #print('dl_dz',dl_dz)
            residu1 = np.concatenate((dl_dx, dl_dy, dl_dz),axis=0)
            #print('residu1',residu1)
            
            
            #residuals calculation
            #print('a',a)
            #print('z',z)
            #print(np.dot(a.T,z))

            
            r1=g-np.dot(a,z)-y+s-b
            #print('r1',r1)
            r2=(eta*(x-np.array([alpha]).T))-epsi*variable_vector 
            #print('r2',r2)
            r3=(neta*(np.array([beta]).T-x))-epsi*variable_vector
            #print('r3',r3)
            r4=nu*y-epsi*minimizer_vector
            #print('r4',r4)
            r5=Zeta*z-epsi
            #print('r5',r5)
            r6=lamda*s-epsi*minimizer_vector
            #print('r6',r6)
            #print(r1,r2,r3)
            residu2 = np.concatenate((r1, r2, r3, r4, r5, r6), axis = 0)
            residu = np.concatenate((residu1, residu2), axis = 0)
            #print('residu',residu.T)
            residunorm = np.sqrt((np.dot(residu.T,residu)).item())
            #print(residunorm)
            residumax = np.max(np.abs(residu))
            #print(residumax)
            oc_stop = time.time()
            optimal_condtition_ex_time += (oc_stop - oc_start)
            optimal_condtition_Count+=1 
            return residumax,residunorm
        
        def line_search(w,dw,x,y,z,lamda,eta,neta,nu,Zeta,s,dx,dy,dz,dlamda,deta,dneta,dnu,dZeta,ds,resi_norm,epsi,p0=p0,q0=q0,pc=pc,qc=qc,U=U,L=L,alpha=alpha,beta=beta,variable_vector=variable_vector,minimizer_vector=minimizer_vector):
           
            #calculating initial step step
            #dw=np.maximum(dw,1e-5)
            #print(dw)
            '''
            step_size=np.max(-1.01*(dw/w))
            #print(step_size)
            DL=np.max(-1.01*(dx/(x-np.array([alpha]).T)))
            DU=np.max(1.01*(dx/(np.array([beta]).T)-x))
            step_range=max(DL,DU)
            a=1/max(1.0,max(step_size,step_range))
            '''
            global line_search_Count
            global line_search_ex_time

            ls_start = time.time()

            size = -1.01*dw/w

            max_size = np.max(size) 
            stepa =-1.01*(dx/(x-np.array([alpha]).T))
            max_stepa = np.max(stepa)
            stepb = 1.01*(dx/((np.array([beta]).T)-x))
            max_stepb = np.max(stepb)
            max_step = max(max_stepa,max_stepb)
            final_step = max(max_step,max_size)
            step_size = max(final_step,1.0)
            a = 1.0/step_size
            #print('a',a)
            it=0
            max_iteration=200
            while it<max_iteration:
                newx=x+a*dx
                newy=y+a*dy
                newz=z+a*dz
                newlam=lamda+a*dlamda
                neweta = eta+a*deta
                newneta = neta+a*dneta
                newnu = nu+a*dnu
                newZeta = Zeta+a*dZeta
                new_s = s+a*ds
                #np.set_printoptions(precision=4)
                #print('x,y,z',newx,newy,newz)
                #print('\n lamda',newlam)
                #print('\n neweta',neweta)
                #print('\n newneta',newneta)
                #print('\n newnu',newnu)
                #print('\n newZeta',newZeta)
                #print('\n new_s',new_s)
            
                #print('lam,eta,neta,nu,Zeta,s',x,y,z,lamda,s,Zeta,eta,neta,nu)
                new_residualmax,new_residunorm=optimal_condtition(newx,newy,newz,newlam,new_s,newZeta,neweta,newneta,newnu,epsi)
                it+=1
                
                
                #print('line_residual',[new_residualmax,new_residunorm])
                if new_residunorm <(2*resi_norm):
                      ls_stop = time.time()
                      line_search_ex_time += (ls_stop - ls_start)
                      line_search_Count+=1 
                      return newx,newy,newz,newlam,neweta,newneta,newnu,newZeta,new_s,new_residualmax,new_residunorm,it 
                a=a*0.5
                #print('a1',a)
            
        
        def Newton_method(U,L,x,y,z,alpha,beta,p0,q0,pc,qc,epsi,lamda,s,Zeta,eta,neta,nu,residumax,residunorm,variable_vector=variable_vector,minimizer_vector=minimizer_vector):
           
            global Newton_method_Count
            global Newton_method_ex_time
            newton_start = time.time()

            def linear_system_assembly(Dx,Dy,Dlamda,delx,dely,delz,dellamda,G,a,z,Zeta,variable_vector=variable_vector,minimizer_vector=minimizer_vector):
                
                global linear_system_assembly_Count
                global linear_system_assembly_ex_time
                linear_start = time.time()
            

                Dx_inv=1/Dx
                Dy_inv=1/Dy
                Dlamda_y=Dlamda+Dy_inv
                dellamda_y=dellamda+Dy_inv*dely
                if len(variable_vector)>len(minimizer_vector):
                    ###
                    A11=np.asarray(np.diag(Dlamda_y.flatten(),0) \
                        +(np.diag(Dx_inv.flatten(),0).dot(G.T).T).dot(G.T))
                    ###
                    #print(A11)
                    A12=a
                    A21=A12
                    A22=-Zeta/z
                    
                    A=np.concatenate((np.concatenate((A11,A12),axis=1),np.concatenate((A21,A22),axis=0).T),axis=0)
                    #print('A',A)
                    B1=dellamda_y-np.dot(G,(delx*Dx_inv))
                    B2=delz
                
                    B=np.concatenate((B1,B2),axis=0)
                    #print('B',B)
                    X=np.linalg.solve(A,B)
                    dlamda=X[:len(minimizer_vector)]
                    dz=X[len(minimizer_vector):len(minimizer_vector)+1]
                    dx=-(Dx_inv*np.dot(G.T,dlamda))-Dx_inv*delx
                    dy=(Dy_inv*dlamda)-(Dy_inv*dely)

                    linear_stop = time.time()
                    linear_system_assembly_ex_time += (linear_stop - linear_start)
                    linear_system_assembly_Count+=1 
                    return dx,dy,dz,dlamda
            residnorm=residunorm        
            iteration=0
            l_ii=0
            max_iteration=250
            while iteration<max_iteration:
                iteration+=1
                UX=np.array([U]).T-x
                LX=x-np.array([L]).T
                #print('x',x)
                #print('\n U',np.array([U]).T)
                #print('\n UX',UX)
                #print('\n UX',UX**3)
                #print('\n UX_INV',1/UX)
                #print('\n UX_INV2',(1/(UX**2)))
                #print('\n UX_INV3',(1/(UX**3)))
                plamda=p0+np.dot(pc.T,lamda)
                #print('plamda',plamda)
                qlamda=q0+np.dot(qc.T,lamda)
                #5.4
                g=np.dot(pc,(1/(UX)))+np.dot(qc,(1/(LX)))
                dphi_dx=(plamda/UX**2)-(qlamda/LX**2)
                dphi_dxdx=(2*plamda/UX**3)+(2*qlamda/LX**3)
                
                #print('phi',g)
                #print('dphi_dxdx',dphi_dxdx)
                #dphi_dxdx=2*plamda.T*(1/((U-x)**3))+2*qlamda.T*(1/((x-L)**3))
                #print('dphi_dxdx',dphi_dxdx)
                   
                Dx=dphi_dxdx+(eta/(x-np.array([alpha]).T))+(neta/(np.array([beta]).T-x))
                Dy=d+nu/y
                Dlamda=s/lamda
                #print('Dx',Dx)
                #print('Dy',Dy)
                #print('Dlamda',Dlamda)
                #print('dphi_dx',dphi_dx)
                delx=dphi_dx-(1/(x-np.array([alpha]).T))*epsi*variable_vector+(1/(np.array([beta]).T-x))*epsi*variable_vector
                dely=c+d*y-lamda-(epsi*minimizer_vector)/y
                delz=a0-np.dot(lamda.T,a)-epsi/z
                dellamda=g-a*z-y-b+epsi*minimizer_vector/lamda
                #print('delx',delx)
                #print('dely',dely)
                #print('delz',delz)
                #print('dellamda',dellamda)
                Dx_inv=1/Dx
                Dy_inv=1/Dy
                Dlamda_y=Dlamda+Dy_inv
                dellamda_y=dellamda+Dy_inv*dely
   
                inv_UX=1/(U-x.T)**2
                diag_pij=inv_UX[0,:]
                inv_LX=1/(x.T-L)**2
                diag_qij=inv_LX[0,:]
                pij=(np.diag(diag_pij,0).dot(pc.T)).T
                qij=(np.diag(diag_qij,0).dot(qc.T)).T
                G=pij-qij
                #print('G',G)
                
                dx,dy,dz,dlamda=linear_system_assembly(Dx,Dy,Dlamda,delx,dely,delz,dellamda,G,a,z,Zeta)
                #print('dx',dx,'dy',dy,'dz',dz,'dlamda',dlamda)
                AlphaX=x-np.array([alpha]).T
                BetaX=np.array([beta]).T-x
                deta=-((eta*dx)/AlphaX)-eta+((epsi*variable_vector)/AlphaX)
                dneta=((neta*dx)/BetaX)-neta+((epsi*variable_vector)/BetaX)
                #print('dneta',dneta)
                dnu=-(nu*dy/y)-nu+(epsi*minimizer_vector/y)
                dZeta=-((Zeta/z)*dz)-Zeta+(epsi/z)
                ds=-((s*dlamda)/lamda)-s+epsi*minimizer_vector/lamda
                
                w=np.concatenate((y,z,lamda,eta,neta,nu,s,Zeta),axis=0)
                dw=np.concatenate((dy,dz,dlamda,deta,dneta,dnu,ds,dZeta),axis=0)
                #lline search 
                #print('w',np.round(w.T))
                #print('dw',np.round(dw.T))
                oldx=x
                oldy=y
                oldz=z
                oldlamda=lamda
                oldeta=eta
                oldneta=neta
                oldnu=nu
                oldZeta=Zeta
                olds=s
                new_x,new_y,new_z,new_lamda,new_eta,new_neta,new_nu,new_Zeta,new_s,new_residualmax,new_residunorm,ii2=line_search(w,dw,x,y,z,lamda,eta,neta,nu,Zeta,s,dx,dy,dz,dlamda,deta,dneta,dnu,dZeta,ds,residnorm,epsi)
                l_ii+=ii2
                x=new_x
                y=new_y
                z=new_z
                lamda=new_lamda
                eta=new_eta
                neta=new_neta
                nu=new_nu
                Zeta=new_Zeta
                s=new_s
                residumax=new_residualmax
                residnorm=new_residunorm
                xx1=oldx-x
                xx2=oldy-y
                xx3=oldz-z
                xx4=oldlamda-lamda
                xx5=oldeta-eta
                xx6=oldneta-neta
                xx7=oldnu-nu
                xx8=oldZeta-Zeta
                xx9=olds-s
                exit_cond=np.concatenate((xx1,xx2,xx3,xx4,xx5,xx6,xx7,xx8,xx9),axis=0)
                if iteration>=max_iteration:
                    print('line_search',exit_cond.T)
                    print('w',w.T)
                    print('dw',dw.T)
                #print('line residumax:',[residumax,residnorm])
                if residumax<0.9*epsi :#or np.linalg.norm(abs(exit_cond))<1e-4:
                    #print(x,y,z,lamda,eta,neta,nu,Zeta,s)
                    newton_stop = time.time()
                    Newton_method_ex_time += (newton_stop - newton_start)
                    Newton_method_Count+=1 
                    return x,y,z,lamda,eta,neta,nu,Zeta,s,iteration,l_ii
        
                
               

        ii1=0
        l_ii1=0
        while epsi> epsimin:
            #print('x',x)
            residual_max,residunorm=optimal_condtition(x,y,z,lamda,s,Zeta,eta,neta,nu,epsi)
            #print('outerresidual:',[residual_max,residunorm])
            oldx=x
            oldy=y
            oldz=z
            oldlamda=lamda
            oldeta=eta
            oldneta=neta
            oldnu=nu
            oldZeta=Zeta
            olds=s
            x,y,z,lamda,eta,neta,nu,Zeta,s,ii1,l_ii=Newton_method(Upper,Lower,x,y,z,alpha,beta,p0,q0,pc,qc,epsi,lamda,s,Zeta,eta,neta,nu,residual_max,residunorm)
            ii1+=ii1
            l_ii1+=l_ii
            xx1=oldx-x
            xx2=oldy-y
            xx3=oldz-z
            xx4=oldlamda-lamda
            xx5=oldeta-eta
            xx6=oldneta-neta
            xx7=oldnu-nu
            xx8=oldZeta-Zeta
            xx9=olds-s
            epsi=epsi*0.1 
            exit_cond=np.concatenate((xx1,xx2,xx3,xx4,xx5,xx6,xx7,xx8,xx9),axis=0)
            res=np.linalg.norm(abs(exit_cond))
            #if np.linalg.norm(abs(exit_cond))<1e-4:
            #    print(x)
            pd_stop = time.time()
            prime_dual_ex_time += (pd_stop - pd_start)
            prime_dual_Count+=1 
        return x,ii1,l_ii1,res
        
    Lower,Upper,x=Asymptoes()
    c = 10000*np.ones((vel,1))
    #print(c)
    d = np.ones((vel,1))
    a0 = 1
    a = np.zeros((vel,1))
    #calculating alpha and beta
    alpha=np.maximum(Xmin,np.maximum((Lower+m_tol*(x-Lower)),(x-m*(Xmax-Xmin))))
    beta=np.minimum(Xmax,np.minimum((Upper-m_tol*(Upper-x)),(x+m*(Xmax-Xmin))))
    #x=Newton_Method(dfun0,f0,x,Lower,Upper,alpha,beta)
    #calculating dervivative of objective and constrains 
    p0,q0=objective_constrains(x,Lower,Upper)
    pc,qc,rc=Minimizer_constrains(x,Lower,Upper)
    b=-rc
  
    x,exit_i,l_iit,res=prime_dual(Lower,Upper,alpha,beta,p0,q0,pc,qc,a,b,c,d)
    #print(x)
    if True:
        width=120
        TGREEN =  '\033[32;1m' # Green Text
        TBLUE = '\033[34;1m'
        ENDC = '\033[m' 
        print('*'*width)
        fmt='{:^'+str(width)+'}'
        print(TBLUE+fmt.format('Method of Moving Asymptoes')+ENDC)
        print('`'*width)
        fmt='{:^'+str(width)+'}'
        print(TGREEN+fmt.format('Prime-Dual Newton Method')+ENDC)
        print('-'*width)
        print(TBLUE+'             Lower: %f3          Upper:%f3           Alpha:%f3           Beta:%f3 ' %(np.mean(Lower),np.mean(Upper),np.mean(alpha),np.mean(beta))+ENDC) 
        print('-'*width)
        print(TGREEN+'     Newton_iter: %d      Line_search_ite:%d      residual:%f4      vol_constrain:%f6     vol:%f4' %(exit_i,l_iit,res,c0,np.mean(x))+ENDC)  
        print('*'*width)
        print('#'*width)
    stop = time.time()
    Moving_asymptoes_ex_time += (stop - start)
    Moving_asymptoes_Count+=1 
    return x,Lower,Upper


def element_density_slided1(i,CP,nx,ny,nz,element_density,optimizer):
    global element_density_slided1_Count
    global element_density_slided1_ex_time
    start = time.time() 
    pv.set_plot_theme("paraview")
    
    Folder('./results/')
    path1="./results/"+optimizer+"_IGTO/"
    Folder(path1)
    path=path1+optimizer+"_cantilever_"+str(i)+".jpg"
    mesh = pv.StructuredGrid()
# Set the coordinates from the numpy array
    mesh.points = CP
# set the dimensions
    mesh.dimensions = [nx, ny, nz]
    #mesh.cell_arrays["volume"] =element_density

    p = pv.Plotter(shape=(2,2))
# XYZ - show 3D scene first
    p.subplot(1,1)
    no=max(nx,ny,nz)*10
    slices=mesh.slice_along_axis(n=no, axis='x')
    p.add_mesh(slices)
    p.add_text("ISOMETRIC VIEW", font_size=10)
    p.add_mesh(slices,opacity="linear",style='surface')
    p.add_axes(interactive=True)
    p.show_grid()
    #p.camera_position = cpos
# XY
    p.subplot(0,0)
    no=ny*10
    slices=mesh.slice_along_axis(n=no, axis='y')
    p.add_mesh(slices)
    p.add_text("XY", font_size=10)
    p.add_mesh(slices,opacity="linear",style='wireframe')
    p.show_grid()
    p.add_axes(interactive=True)
    p.camera_position = 'xy'
    p.enable_parallel_projection()
# ZY
    p.subplot(0,1)
    no=ny*10
    slices=mesh.slice_along_axis(n=no, axis='y')
    p.add_mesh(slices)
    p.add_text("ZY", font_size=10)
    p.add_mesh(slices,opacity="linear",style='wireframe')
    p.add_axes(interactive=True)
    p.show_grid()
    p.camera_position = 'zy'
    p.enable_parallel_projection()
# XZ
    p.subplot(1,0)
    no=nz*10
    slices=mesh.slice_along_axis(n=no, axis='z')
    p.add_mesh(slices)
    p.add_text("XZ", font_size=10)
    p.add_mesh(slices,opacity="linear",style='wireframe')
    p.add_axes(interactive=True)
    p.show_grid()
    p.camera_position = 'xz'
    p.enable_parallel_projection()

    p.show(title='3D View',screenshot=path,auto_close=True)
    stop = time.time()
    element_density_slided1_ex_time += (stop - start)
    element_density_slided1_Count+=1
    pass

       
def plotting(ii,CC,VV,Mnd,element_density,optimizer,option):
    fig, ax = plt.subplots()
    ax.plot(ii,CC)
    ax.plot(ii[-1], CC[-1],'bo')
    ax.text(ii[-1], CC[-1],str(round(CC[-1],2)),color='b')
    ax.set_xlabel('iteration')
    ax.set_ylabel('Compliance')
    ax.set_xlim(0,ii[-1]+2)
    ax.set_ylim(0,CC[3])
    ax.set_title('Compliance change in each iteration')
    Folder('./results/')
    path="./results/"+optimizer+"_ComplianceVSiteration.png"
    fig.savefig(path)

    fig, ax1 = plt.subplots()
    ax1.plot(ii,VV)
    ax.plot(ii[-1], VV[-1],'bo')
    ax1.text(ii[-1], VV[-1],str(round(VV[-1],2)),color='b')
    ax1.set_xlabel('iteration') 
    ax1.set_ylabel('Volume fraction')
    ax1.set_xlim(0,ii[-1]+2)
#ax.set_ylim(volume_frac-0.1,volume_frac+0.1)
    ax1.set_title('Volume fraction change in each iteration')
    Folder('./results/')
    path="./results/"+optimizer+"_Volume_fractionVSiteration.png"
    fig.savefig(path)
    
    fig, ax2 = plt.subplots()
    number,bins,pat=ax2.hist(element_density,bins=10)
    
    ax2.text(0.25,max(number)+0.5,'Measure of discreteness: '+str(round(Mnd,2)))
    ax2.set_xlabel('volume fraction ') 
    ax2.set_ylabel('Number of elements')
#ax.set_ylim(volume_frac-0.1,volume_frac+0.1)
    ax2.set_title('Discretness of volume fraction')
    Folder('./results/')
    path="./results/"+optimizer+"_discretness.png"
    fig.savefig(path)

##START OF THE MAIN PROGRAM
XI_DEGREE = 1
ETA_DEGREE = 1
NETA_DEGREE = 1


N = nx
P = ny
Q = nz

main_program_start=time.time()
#inputs parameters to build IGA are generated
C = Inputs(length, height, width, N, P, Q, XI_DEGREE, ETA_DEGREE, NETA_DEGREE)

CONTROL_POINTS = C.crtpts_coordinates()
# print(CONTROL_POINTS)
WEIGHTS = CONTROL_POINTS[:, -1]

XI_KNOTVECTOR = C.xi_knotvector()
ETA_KNOTVECTOR = C.eta_knotvector()
NETA_KNOTVECTOR = C.neta_knotvector()
XI_SPAN, XI_KNOTCONNECTIVITY, XI_UNIKNOTS, nU = C.xi_knotspan()
ETA_SPAN, ETA_KNOTCONNECTIVITY, ETA_UNIKNOTS, nV = C.eta_knotspan()
NETA_SPAN, NETA_KNOTCONNECTIVITY, NETA_UNIKNOTS, nW = C.neta_knotspan()

print('\n')

ncp = N * P * Q #number of control point
dof = 3
dofcp = ncp * dof #number of degrees of freedom of the system
nel = nU * nV * nW #number of elements
width1 = 120
print('#' * width1)
fmt = '{:^' + str(width1) + '}'
print(fmt.format('Dimensions of the structure \n'))
print('                   Length       :', length, '               Height     :', height,
      '               Width        :', width, '\n')

print('                   Xi degree    :', XI_DEGREE, '                Eta degree :', ETA_DEGREE,
      '                Neta degree  :', NETA_DEGREE, '\n')
print('                   NX           :', N - XI_DEGREE, '                NY         :', P - ETA_DEGREE,
      '                NZ           :', Q - NETA_DEGREE, '\n')
print('Number of degrees of freedom :', dofcp, '\n')

print('Number of Elements:', nel, '\n')

print('No of control points in each element:', (XI_DEGREE + 1) * (ETA_DEGREE + 1) * (NETA_DEGREE + 1), '\n')

print('>' * width1)
print('Length of the knot vector in respective direction \n')
print('XI Vector        :', list(XI_KNOTVECTOR), '\nETA vector       :', list(ETA_KNOTVECTOR), '\nNETA vector      :',
      list(NETA_KNOTVECTOR), '\n')
print('<' * width1)
K_G = np.zeros((dofcp, dofcp))
F_E = np.zeros(dofcp)
U = np.zeros(dofcp)
print('#' * width1)
fmt = '{:^' + str(width1) + '}'
print(fmt.format('Program has started \n'))

K_disp = True
#generating control point and knot connectivity to build element routine
element_indicies = controlpointassembly(N, P, Q, nU, nV, nW, XI_DEGREE, ETA_DEGREE, NETA_DEGREE, XI_KNOTCONNECTIVITY,
                                        ETA_KNOTCONNECTIVITY, NETA_KNOTCONNECTIVITY)
span_index = knot_connectivity(N, P, Q, XI_KNOTCONNECTIVITY, ETA_KNOTCONNECTIVITY, NETA_KNOTCONNECTIVITY)
print('$' * width1)
fmt = '{:^' + str(width1) + '}'
IGA_start = time.time() 
print(fmt.format('Finite Element Analysis based on ISO-Geometric analysis(NURBS)\n'))
#looped based on number of elements
for i in range(0, nel):
    el_in = element_indicies[i, :]
    sp_in = span_index[i, :]
    X = CONTROL_POINTS[el_in, 0]
    Y = CONTROL_POINTS[el_in, 1]
    Z = CONTROL_POINTS[el_in, 2]
    weights = CONTROL_POINTS[el_in, 3]
    Uspan = XI_SPAN[sp_in[0], :]
    Vspan = ETA_SPAN[sp_in[1], :]
    Wspan = NETA_SPAN[sp_in[2], :]
    #element stiffness matrix is obtained
    K_E, NURBS, R = element_routine(X, Y, Z, weights, Youngs_modulus, poission_ratio, Uspan, Vspan, Wspan, XI_DEGREE,
                                    XI_KNOTVECTOR, ETA_DEGREE, ETA_KNOTVECTOR, NETA_DEGREE, NETA_KNOTVECTOR)
    #global stiffness matrix is built by mapping element stiffness matrix 
    K_G = assemble(K_G, K_E, el_in, ncp, K_disp)
    K_disp = False

bc_disp = False
abc_disp = True
#boundary conditions are called 
BC = BC_Switcher(CONTROL_POINTS, length, height, width, bc_disp)
fixed_dof, load_dof, fixed_pts, load_pts = BC.indirect(option)
#boundary coditions are applied
reduced_k=np.delete(np.delete(K_G, fixed_dof, 0),fixed_dof , 1)
reduced_F = apply_BC(F_E, fixed_dof, load_dof, load, abc_disp)
#displacements are calculated
U = np.linalg.solve(reduced_k, reduced_F)
print('Calculating Displacements \n')
for j in fixed_dof:
    U = np.insert(U, j, 0)
#mapping displacements
F_E[load_dof] = load
IGA_stop = time.time() 
U_new = np.array((U.reshape(len(CONTROL_POINTS), 3)), dtype='float64')
IGA_ex_time=(IGA_stop-IGA_start)
print('Execution time for IGA analysis at 100% volume :',IGA_ex_time,'\n')
New_control_points = CONTROL_POINTS[:, :-2] + U.reshape(len(CONTROL_POINTS), 3)
Ux = U_new[:, 0]
Uy = U_new[:, 1]
Uz = U_new[:, 2]
energy_stored = np.dot(0.5, U @ F_E) #strain energy stored by structure due to deformation
print('\nThe structure is not optimised and has 100% volume \n')
print('The strain energy of the structure               :', energy_stored)
print('$' * width1)
CP = CONTROL_POINTS[:, :-2]

#START OF TOPOLOGY OPTIMIZATION
Emin = 1e-09
E0 = 1
#intialization of dimension for Global stiffness matrix, external force vector  and displacements

K_G = np.zeros((dofcp, dofcp))
F_E = np.zeros(dofcp)
U = np.zeros(dofcp)
print('+' * width1)
fmt = '{:^' + str(width1) + '}'
print(fmt.format('Structural Topology optimization using IGA \n'))
print('\n                                            Optimization has started \n')

print('                                     Density of the material       :', density)
print('                                     Youngs Modulus                :', Youngs_modulus)
print('                                     Poission ratio                :', poission_ratio, '\n')
fmt = '{:^' + str(width1) + '}'
print(fmt.format('The percentage of volume which has to remain after optimization \n'))
print('                                          ', volume_frac)
print('+' * width1)
#initialzing dimension and initial values of variables used in toplogy optimization
density_basis = np.zeros(nel)
ele_den_filter = np.zeros(nel)
element_density = np.ones(nel) * volume_frac
density_basis_dx = np.zeros(nel)
dcompliance = np.zeros(nel)
compliance = 0
# performing sensitivity analysis i.e giving weights to the respective elements.
nfilter = int(nel * ((2 * (np.ceil(rmin) - 1) + 1) ** 2))
#Weight factor are obtained from the below function
H, DH = Knearestneighbours(rmin, nU, nV, nW)
loop = 0
change = 1
g = 1
CC = []
ii = []
VV = []
# penal=max(15*((1-poission_ratio)/(7-5*poission_ratio)),(3/2)*((1-poission_ratio)/(1-2*poission_ratio)))
oc_disp = True
bc_disp = True
fil_disp = True
max_iterations = 250
beta =1
filter_N = np.zeros(((XI_DEGREE + 1) * (ETA_DEGREE + 1) * (NETA_DEGREE + 1), nel))
#intializing dimension and initial value of the variables.
Xmin = np.zeros(nel)
Xmax = np.ones(nel)
Lower = Xmin
Upper = Xmin
E1 = element_density
E2 = element_density
TO_start=time.time()
Total_time=0
OC_residual=0
# loop run until the termination condition is satisified i.e change in compliance from previous iteration 

while change > 0.01:
        #intializing the dimensions of global stiffness matrix, external force vector, compliance,change in compliance for toplogy optimization in each iteration.
    loop_start=time.time()
    K_G = np.zeros((dofcp, dofcp))
    F_E = np.zeros(dofcp)
    U = np.zeros(dofcp)
    dcompliance = np.zeros(nel)
    compliance = 0
    # nodal density are calculated based on equ. 4.20
    node_density = np.ones((nel, (XI_DEGREE + 1) * (ETA_DEGREE + 1) * (NETA_DEGREE + 1)))
    for h in range(nel):
        node_density[h, :] = node_density[h, :] * element_density[h]
     #looped over number of elements
    for i in range(0, nel):
        el_in = element_indicies[i, :]
        sp_in = span_index[i, :]
        X = CONTROL_POINTS[el_in, 0]
        Y = CONTROL_POINTS[el_in, 1]
        Z = CONTROL_POINTS[el_in, 2]
        weights = CONTROL_POINTS[el_in, 3]
        Uspan = XI_SPAN[sp_in[0], :]
        Vspan = ETA_SPAN[sp_in[1], :]
        Wspan = NETA_SPAN[sp_in[2], :]

        K_E, NURBS, R = element_routine(X, Y, Z, weights, Youngs_modulus, poission_ratio, Uspan, Vspan, Wspan,
                                        XI_DEGREE, XI_KNOTVECTOR, ETA_DEGREE, ETA_KNOTVECTOR, NETA_DEGREE,
                                        NETA_KNOTVECTOR)
        element_density[i] = np.dot(node_density[i, :], NURBS)
        filter_N[:, i] = NURBS
        density_basis[i] = Emin + (element_density[i] ** penal) * (E0 - Emin)
        K_E = density_basis[i] * K_E
        K_G = assemble(K_G, K_E, el_in, ncp)

    BC = BC_Switcher(CONTROL_POINTS, length, height, width, bc_disp)
    fixed_dof, load_dof, fixed_pts, load_pts = BC.indirect(option)
    reduced_k=np.delete(np.delete(K_G, fixed_dof, 0),fixed_dof , 1)
    reduced_F = apply_BC(F_E, fixed_dof, load_dof, load)

    U = np.matmul(np.linalg.inv(reduced_k), reduced_F)

    for j in fixed_dof:
        U = np.insert(U, j, 0)

    F_E[load_dof] = load
    # print(U@F_E)
    # Untill now, The displacements of the optimized structure are calculated whose dispalcements are required to compute compliance and change in 
    # compliance w.r.t element density. 
    #looped over number of no of element to calculate compliance and dcompliance 
    for k in range(0, nel):
        el_in = element_indicies[k, :]
        sp_in = span_index[k, :]
        X = CONTROL_POINTS[el_in, 0]
        Y = CONTROL_POINTS[el_in, 1]
        Z = CONTROL_POINTS[el_in, 2]
        weights = CONTROL_POINTS[el_in, 3]
        Uspan = XI_SPAN[sp_in[0], :]
        Vspan = ETA_SPAN[sp_in[1], :]
        Wspan = NETA_SPAN[sp_in[2], :]

        K_E, NURBS, R = element_routine(X, Y, Z, weights, Youngs_modulus, poission_ratio, Uspan, Vspan, Wspan,
                                        XI_DEGREE, XI_KNOTVECTOR, ETA_DEGREE, ETA_KNOTVECTOR, NETA_DEGREE,
                                        NETA_KNOTVECTOR)
        #Calculating element density based on equ. 4.20                                                               
        element_density[k] = np.dot(node_density[k, :], NURBS)
        # Implemenation of SIMP method based on equ. 4.21
        density_basis[k] = Emin + (element_density[k] ** penal) * (E0 - Emin)
                #derivative of equ. 4.21 w.r.t to element density
        density_basis_dx[k] = -penal * (element_density[k] ** (penal - 1)) * (E0 - Emin)
        dof_index = np.sort(np.concatenate((el_in * dof, dof * el_in + 1, dof * el_in + 2)))
                #Calculating compliance and change in compliance
        compliance += np.transpose(U[dof_index]) @ (density_basis[k] * K_E) @ U[dof_index]
        dcompliance[k] = np.transpose(U[dof_index]) @ (density_basis_dx[k] * K_E) @ U[dof_index]
     #Initializing the change in volume fraction V0/V
    dv = np.ones(nel)

    element_density = np.round(element_density, 5)
    old_el_density = element_density

    constrain = nel * volume_frac
        #To solve constrained based probelm, we used methods like penality method(OC) and active set strategy(MMA) to satisfy KKT conditions
    if optimizer == 'OC':
        
        dcompliance = (1 / np.maximum(1e-3, element_density) * DH) * np.matmul(H, (element_density * dcompliance))
        dv = np.matmul(H, dv / DH)
        
        element_density_updated,OC_residual = optimality_criteria(dcompliance, dv, element_density, constrain,OC_residual, H, DH, oc_disp,
                                                      g)
        element_density = element_density_updated
    if optimizer == 'MMA':
        dcompliance = np.matmul(H, (dcompliance / DH))
        dv = np.matmul(H, dv / DH)

        v = (np.sum(element_density) / nel) - volume_frac
        dv_dx = (dv / (volume_frac * nel))
        
        dfun0 = dcompliance
        dcon = dv_dx
        f0 = compliance
        c0 = v
        element_density_updated, Lower, Upper = Moving_asymptoes(dfun0, dcon, f0, c0, element_density, E1, E2, Lower,
                                                                 Upper, loop, nel, 1, Xmin, Xmax, True)
        E2 = E1.copy()
        E1 = element_density.copy()
        element_density = np.round(element_density_updated[:, 0], 4)

    if (loop % 50) == 0:
        beta *= 2
    #Compliance and volume after each iteration are stored for analysis
    CC.append(compliance)
    ii.append(loop)
    VV.append(np.mean(element_density))
    change = np.linalg.norm(element_density - old_el_density)

    if loop == 0:
        initial_compliance = compliance
    loop += 1
    TYELLOW =  '\033[33;1m' # Green Text
    TRED = '\033[31;1m'
    ENDC = '\033[m'
    print(TYELLOW+'     Iteration: %d       p :%f      optimizer:%s      OBJ=%f6       Vol=%f       CHG=%f6      ' % (
        loop, penal, optimizer, compliance, np.mean(element_density), change)+ENDC)
    print('#' * width1)
    
    
    CPS = CONTROL_POINTS[:, :-2]
    loop_stop=time.time()
    loop_ex_time=loop_stop-loop_start
    Total_time+=loop_ex_time #time taken to run the toplogy optimization loop is calculated
     
    print('       Execution time of this iteration :',loop_ex_time,'sec          Total execution Time:',Total_time,'sec') 
    print('=' * width1)
    print('\n')
    if  (change<0.01 or (loop in [1,5,10,20,40,60,80,100,120,140,160,180,200,220,250])) and iterative_display is True:
        element_density_slided1(loop,CP,nx,ny,nz,element_density,optimizer)
    if loop >= max_iterations:
        print('~' * width1)
        fmt = '{:^' + str(width1) + '}'
        print(fmt.format('Maximum iteration has been reached'))
        print('~' * width1)
        break

TO_stop=time.time()  
TO_execution_time=  TO_stop-TO_start
print('     The time taken to run Topology optimization:',TO_execution_time,'sec')
print('+' * width1)

#Measure of discretness - Calculated to show the efficiency of the method's abitlity to penalize the element desnsity as 0 or 1
Mnd = np.dot(4 * element_density, (1 - element_density)) / nel * 100
print('                                        Measure of discreteness: ', Mnd)

element_density = np.round(element_density, 1) # FINAL OPTIMIZED STRUCTURE IS OBTAINED


print('\n                               Final Volume of the optimised structure  :', np.mean(element_density))
print('\n                               Mass of the beam at 100% volume          :',
      (length * width * height) * density)
print('\n                               Optimized mass of the beam               :',
      (length * width * height) * density * np.mean(element_density))
energy_stored = np.dot(0.5, np.matmul(U.transpose(), np.matmul(U, K_G)))
print('\n                               Initial Compliance without optimization  :', initial_compliance)
final_compliance = np.dot(U, F_E)
print('\n                               Final Compliance with optimization       :', final_compliance, '\n')

#VTK file is genetated
VTK(CONTROL_POINTS,element_density,nU,nV,nW,"Cantilever_beam")

plotting(ii,CC,VV,Mnd,element_density,optimizer,option)
#element density are stored in txt format
np.savetxt("element_density.txt", element_density) 
#TIME ANALYSIS
main_program_stop=time.time() 
main_program_execution_time=(main_program_stop-main_program_start) #total time taken  by the program
print('                       Total execution time of the whole program:',main_program_execution_time,'sec')
#MMA and OC have different function when called based which the log file is created
if optimizer=='MMA':
      time_analysis_array=np.array([[' Folder ', Folder_Count , Folder_ex_time  , Folder_ex_time / Folder_Count ],
                              [' knot index ', knot_index_Count , knot_index_ex_time  , knot_index_ex_time / knot_index_Count ],
                              [' bspline basis ', bspline_basis_Count , bspline_basis_ex_time  , bspline_basis_ex_time / bspline_basis_Count ],
                              [' derbspline basis ', derbspline_basis_Count , derbspline_basis_ex_time  , derbspline_basis_ex_time / derbspline_basis_Count ],
                              [' trilinear der ', trilinear_der_Count , trilinear_der_ex_time  , trilinear_der_ex_time / trilinear_der_Count ],
                              [' gauss quadrature ', gauss_quadrature_Count , gauss_quadrature_ex_time  , gauss_quadrature_ex_time / gauss_quadrature_Count ],
                              [' unittoparametric ', unittoparametric_Count , unittoparametric_ex_time  , unittoparametric_ex_time / unittoparametric_Count ],
                              [' jacobian ', jacobian_Count , jacobian_ex_time  , jacobian_ex_time / jacobian_Count ],
                              [' strain displacement ', strain_displacement_Count , strain_displacement_ex_time  , strain_displacement_ex_time / strain_displacement_Count ],
                              [' Compliance matrix ', Compliance_matrix_Count , Compliance_matrix_ex_time  , Compliance_matrix_ex_time / Compliance_matrix_Count ],
                              [' element routine ', element_routine_Count , element_routine_ex_time  , element_routine_ex_time / element_routine_Count ],
                              [' assemble ', assemble_Count , assemble_ex_time  , assemble_ex_time / assemble_Count ],
                              [' apply BC ', apply_BC_Count , apply_BC_ex_time  , apply_BC_ex_time / apply_BC_Count ],
                              [' Knearestneighbours ', Knearestneighbours_Count , Knearestneighbours_ex_time  , Knearestneighbours_ex_time / Knearestneighbours_Count ],
                              [' Moving asymptoes ', Moving_asymptoes_Count , Moving_asymptoes_ex_time  , Moving_asymptoes_ex_time / Moving_asymptoes_Count ],
                              [' Asymptoes ', Asymptoes_Count , Asymptoes_ex_time  , Asymptoes_ex_time / Asymptoes_Count ],
                              [' objective constrains ', objective_constrains_Count , objective_constrains_ex_time  , objective_constrains_ex_time / objective_constrains_Count ],
                              [' Minimizer constrains ', Minimizer_constrains_Count , Minimizer_constrains_ex_time  , Minimizer_constrains_ex_time / Minimizer_constrains_Count ],
                              [' prime dual ', prime_dual_Count , prime_dual_ex_time  , prime_dual_ex_time / prime_dual_Count ],
                              [' linear system_assembly ', linear_system_assembly_Count , linear_system_assembly_ex_time  , linear_system_assembly_ex_time / linear_system_assembly_Count ],
                              [' initial condition ', initial_condition_Count , initial_condition_ex_time  , initial_condition_ex_time / initial_condition_Count ],
                              [' optimal condtition ', optimal_condtition_Count , optimal_condtition_ex_time  , optimal_condtition_ex_time / optimal_condtition_Count ],
                              [' line search ', line_search_Count , line_search_ex_time  , line_search_ex_time / line_search_Count ],
                              [' Newton method', Newton_method_Count , Newton_method_ex_time  , Newton_method_ex_time / Newton_method_Count ]])

if optimizer=='OC':
      time_analysis_array=np.array([[' Folder ', Folder_Count , Folder_ex_time  , Folder_ex_time / Folder_Count ],
                              [' knot index ', knot_index_Count , knot_index_ex_time  , knot_index_ex_time / knot_index_Count ],
                              [' bspline basis ', bspline_basis_Count , bspline_basis_ex_time  , bspline_basis_ex_time / bspline_basis_Count ],
                              [' derbspline basis ', derbspline_basis_Count , derbspline_basis_ex_time  , derbspline_basis_ex_time / derbspline_basis_Count ],
                              [' trilinear der ', trilinear_der_Count , trilinear_der_ex_time  , trilinear_der_ex_time / trilinear_der_Count ],
                              [' gauss quadrature ', gauss_quadrature_Count , gauss_quadrature_ex_time  , gauss_quadrature_ex_time / gauss_quadrature_Count ],
                              [' unittoparametric ', unittoparametric_Count , unittoparametric_ex_time  , unittoparametric_ex_time / unittoparametric_Count ],
                              [' jacobian ', jacobian_Count , jacobian_ex_time  , jacobian_ex_time / jacobian_Count ],
                              [' strain displacement ', strain_displacement_Count , strain_displacement_ex_time  , strain_displacement_ex_time / strain_displacement_Count ],
                              [' Compliance matrix ', Compliance_matrix_Count , Compliance_matrix_ex_time  , Compliance_matrix_ex_time / Compliance_matrix_Count ],
                              [' element routine ', element_routine_Count , element_routine_ex_time  , element_routine_ex_time / element_routine_Count ],
                              [' assemble ', assemble_Count , assemble_ex_time  , assemble_ex_time / assemble_Count ],
                              [' apply BC ', apply_BC_Count , apply_BC_ex_time  , apply_BC_ex_time / apply_BC_Count ],
                              [' Knearestneighbours ', Knearestneighbours_Count , Knearestneighbours_ex_time  , Knearestneighbours_ex_time / Knearestneighbours_Count ],
                              [' optimality criteria ', optimality_criteria_Count , optimality_criteria_ex_time  , optimality_criteria_ex_time / optimality_criteria_Count ]])
time_analysis_array_2=time_analysis_array
time_analysis_array=time_analysis_array[time_analysis_array[:,-1].argsort()] 
stdoutOrigin=sys.stdout 
#generation of log file
log_file_name="./log_files/log_"+optimizer+".txt"
sys.stdout = open(log_file_name, "w")
print('AUTHOR : YASA VISWAMBHAR REDDY \n')
import datetime;
ts = datetime.datetime.now().timestamp()
print('!#',ts,' Topology Optimization using Iso-Geometric Analysis \n')
print('                                        Measure of discreteness: ', Mnd)
print('\n                               Final Volume of the optimised structure  :', np.mean(element_density))
print('\n                               Mass of the beam at 100% volume          :',
      (length * width * height) * density)
print('\n                               Optimized mass of the beam               :', (length * width * height) * density * np.mean(element_density))
print('\n                               Initial Compliance without optimization  :', initial_compliance)
print('\n                               Final Compliance with optimization       :', final_compliance, '\n')

print('Total execution time of the whole program:',main_program_execution_time,'sec \n')

print('The time taken to run Topology optimization:',TO_execution_time,'sec \n')

print('Execution time for IGA analysis at 100% volume :',IGA_ex_time,'\n')

no_of_function,values=time_analysis_array.shape

print('Top 5 function which have high execution time \n')
for j in range((no_of_function-1),(no_of_function-6),-1):
      print(time_analysis_array[j,0],' ')

print('\n +++++++++++The function are ordered in decreasing time of execution+++++++++++ \n')

for i in range((no_of_function-1),0,-1):
    print('---------',time_analysis_array[i,0],'---------')
    print('Total Number of time "',time_analysis_array[i,0],'" was called ',time_analysis_array[i,1],'times.' )
    print('Average time taken by the "',time_analysis_array[i,0],'" function for one run',time_analysis_array[i,3],'seconds.')
    print('Total time taken by the "',time_analysis_array[i,0],'" function ',time_analysis_array[i,2],'seconds. \n')
         
sys.stdout.close()
sys.stdout=stdoutOrigin
print("                                         Log file is generated")

sorted=time_analysis_array[time_analysis_array[:,1].argsort()]
x=sorted[:12,0]
y=sorted[:12,1]
#plotting of pie chart
time_analysis_plotting(x,y,optimizer)
fig, ax = plt.subplots() 
data=sorted[:5,-1]
label=sorted[:5,0]
colors = ['b', 'g', 'r', 'c', 'm']
explode = (0.2, 0, 0, 0, 0)
x=np.linspace(0,5,5)
plt.xticks(x, label)
plt.title("Time analysis Average execution time") 
plt.scatter(x, data)
path="./results/"+optimizer+"_time_analysis_execution_time.png"

fig.savefig(path)
