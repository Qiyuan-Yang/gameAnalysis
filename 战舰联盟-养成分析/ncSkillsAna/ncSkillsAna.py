import sklearn
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
import matplotlib.animation as animation



def twoDimNormDis(a,b,sigma,mode):
    alpha = 100#打散参数
    mean = np.array([0,0])#均值
    conv = np.array([[a*alpha/sigma, 0.0],
                     [0.0, b*alpha/sigma]])#协方差矩阵

    fig = plt.subplot(111, aspect='equal')
    #原始散布圈
    ell = Ellipse((0,0), a*2, b*2, 0,ec = 'red',fill = None)
    fig.add_artist(ell)

    skills = [1,0.93,0.90,0.93*0.90]

    #实际散布圈
    a = a*skills[mode]
    b = b*skills[mode]
    ell = Ellipse((0,0), a*2, b*2, 0,ec = 'black',fill = None)
    fig.add_artist(ell)

    #第一次散布
    x1, y1 = np.random.multivariate_normal(mean=mean, cov=conv, size=1000).T

    #判断是否在圈内
    value = x1**2/a**2+y1**2/b**2
    x_in = [x1[index] for index in range(len(value)) if value[index] <= 1]
    y_in = [y1[index] for index in range(len(value)) if value[index] <= 1]
    acc1 = len(x1)#第一次准确数
    plt.scatter(x_in,y_in,s = 1,c = 'blue')

    #判断是否在圈外
    x_out = [x1[index] for index in range(len(value)) if value[index] > 1]
    y_out = [y1[index] for index in range(len(value)) if value[index] > 1]
    plt.scatter(x_out,y_out,s = 1,c = 'red')

    #出圈的进行一次重掷
    x2,y2 = np.random.multivariate_normal(mean=mean, cov=conv, size=len(x_out)).T
    plt.scatter(x2,y2,s = 1,c = 'green')

    #判断是否在圈内
    value = x2**2/a**2+y2**2/b**2
    x2_in = [x2[index] for index in range(len(value)) if value[index] <= 1]
    acc2  =len(x2_in)#重掷增加准确数
    print(acc2/acc1)

    #画图
    plt.axis('equal')
    plt.show()


def shipTurn(start,urbberTime0,turnCircle,maxSpeed,speedLoss):
    #init
    maxSpeed = maxSpeed*2.5722
    step = 0.01
    skills = [0.85,0.835,0.82,
              0.95*0.85,0.95*0.835,0.95*0.82,
              0.8*0.85,0.8*0.835,0.8*0.82,
              0.95*0.8*0.85,0.95*0.8*0.835,0.95*0.8*0.82]

    for mode in skills:
        #init
        done = 1
        theta = start
        x,y = 0,0
        xData,yData,speedData = [],[],[]
        if mode == skills[0]:
            timeData = []
        time = 0
        urbberTime = urbberTime0*mode
        output = 1


        while done:
            time +=  step
            degree = np.min([time/urbberTime,1])#转舵幅度

            #转向掉速，线性近似
            if degree < 0.5:
                speed = maxSpeed - degree*2*speedLoss[0]*maxSpeed
            else:
                speed = maxSpeed*(1-speedLoss[0]) - (degree - 0.5)*2*speedLoss[1]*maxSpeed

            turnRadius = turnCircle/degree
            move = speed*step
            theta += move/turnRadius
            x += move*np.sin(theta)
            y += move*np.cos(theta)

            # output when turn half
            if theta > np.pi/2 and output:
                print(round(x,2),round(y,2),round(time,2),end=' ')
                output = 0

            #save data
            xData.append(x)
            yData.append(y)
            speedData.append(speed)

            #以最长时间为基准
            if mode == skills[0]:
                timeData.append(time)

            #转180度
            if theta > np.pi:
                done = 0

        print(round(x,2),round(y,2),end=' ')
        print(round(len(xData)*step,2))
        #如果不是最长时间则补全数据
        if len(xData) != timeData:
            length = len(xData)
            xData = np.pad(xData,(0,len(timeData)-length),'constant')
            yData = np.pad(yData,(0,len(timeData)-length),'constant')



        plt.scatter(xData,yData,c = timeData,s = 0.1)

    plt.colorbar()
    plt.axis('equal')
    plt.grid()
    plt.show()



    #vectorlize
def shipTurnMulti(start,target,urbberTime,turnCircle,maxSpeed,speedLoss,draw):
    #init
    epsilon = 1e-2
    maxSpeed = maxSpeed*2.5722
    skills = np.array([0.85,
              0.95*0.85,
              0.8*0.85,
              0.95*0.8*0.85])
    size = len(skills)
    step = np.ones(size)*epsilon
    turnCircle = np.ones(size)*turnCircle

    #init
    done = 1
    theta = np.ones(size)*start
    x,y = np.zeros(size),np.zeros(size)
    xData,yData,speedData = np.zeros(size),np.zeros(size),np.zeros(size)
    timeData = np.zeros(size)
    time = np.zeros(size)
    urbberTime = urbberTime*skills


    while done:
        time +=  step
        degree1 = np.ones(size)
        degree = time/urbberTime
        index = degree1 < degree
        degree[index] = degree1[index]

        #转向掉速，线性近似
        speed = np.ones(size)*maxSpeed
        half_st = degree <= np.ones(size)/2
        half_nd = degree > np.ones(size)/2
        speed[half_st] = speed[half_st] - degree[half_st]*2*speedLoss[0]*maxSpeed
        speed[half_nd] = speed[half_nd]*(1-speedLoss[0]) - (degree[half_nd]-np.ones(size)[half_nd]*0.5)*2*speedLoss[1]*maxSpeed
        
        

        #都达到target则终止循环
        end = theta > np.ones(size)*target
        speed[end] = np.zeros(size)[end]
        if end.all():
            done = 0


        turnRadius = turnCircle/degree
        move = speed*step
        theta += move/turnRadius
        x += move*np.sin(theta)
        y += move*np.cos(theta)

        # output when turn half
        #if theta > np.pi/2 and output:
        #    print(round(x,2),round(y,2),time,end=' ')
        #    output = 0

        #save data
        xData = np.vstack([xData,x])
        yData = np.vstack([yData,y])
        #speedData.append(speed)


    if draw:
        colorBar = np.array(range(len(xData)))*epsilon
        plt.axis('equal')

        for i in range(size):
            plt.scatter(xData[:,i],yData[:,i],s = 0.1,c = colorBar)
        plt.colorbar()
        plt.grid()
        plt.show()
        plt.close()

    return xData,yData
    
def swiftTurn(start,target,urbberTime,turnCircle,maxSpeed,speedLoss,draw):
    #init
    epsilon = 1e-2
    maxSpeed = maxSpeed*2.5722
    skills = np.array([0.85,
              0.95*0.85,
              0.8*0.85,
              0.95*0.8*0.85])
    size = len(skills)
    step = np.ones(size)*epsilon
    turnCircle = np.ones(size)*turnCircle

    #init
    done = 1
    theta = np.ones(size)*start
    x,y = np.zeros(size),np.zeros(size)
    xData,yData,speedData = np.zeros(size),np.zeros(size),np.zeros(size)
    thetaData = theta
    timeData = np.zeros(size)
    time = np.zeros(size)
    urbberTime = urbberTime*skills

    right = np.ones(size)#打舵方向，1为向右，-1为向左


    while done:
        time +=  step*right#打舵时长
        degree1 = np.ones(size)
        degree = time/urbberTime
        index = abs(degree) > degree1
        degree[index] = degree1[index]*(degree[index]/abs(degree[index]))

        #转向掉速，线性近似
        speed = np.ones(size)*maxSpeed
        half_st = abs(degree) <= np.ones(size)/2
        half_nd = abs(degree) > np.ones(size)/2
        speed[half_st] = speed[half_st] - abs(degree[half_st])*2*speedLoss[0]*maxSpeed
        speed[half_nd] = speed[half_nd]*(1-speedLoss[0]) - (abs(degree[half_nd])-np.ones(size)[half_nd]*0.5)*2*speedLoss[1]*maxSpeed
        
        
        #转超过90%target则回舵
        beyong = theta >= np.ones(size)*target*0.6
        right[beyong] = -np.ones(size)[beyong]#只会赋值为-1，即使不满足条件也不会改回1
        #print(beyong,right)

        #都回正到0度则终止循环
        end = theta < np.zeros(size)
        speed[end] = np.zeros(size)[end]
        if end.all():
            done = 0


        turnRadius = turnCircle/degree
        move = speed*step
        theta += move/turnRadius
        x += move*np.sin(theta)
        y += move*np.cos(theta)

        # output when turn half
        #if theta > np.pi/2 and output:
        #    print(round(x,2),round(y,2),time,end=' ')
        #    output = 0

        #save data
        xData = np.vstack([xData,x])
        yData = np.vstack([yData,y])
        thetaData = np.vstack([thetaData,theta])
        #speedData.append(speed)
        
    for i in range(size):
        print(thetaData[:,i].max()/np.pi*180)


    if draw:
        colorBar = np.array(range(len(xData)))*epsilon
        plt.axis('equal')

        for i in range(size):
            plt.scatter(xData[:,i],yData[:,i],s = 0.1,c = colorBar)
        plt.colorbar()
        plt.grid()
        plt.show()
        plt.close()

    return xData,yData




#for i in range(4):
#    twoDimNormDis(300,500,2,i)
#shipTurn(0,16,1270,30.9,[0.068,0.052])






#charlemagne
#shipTurnMulti(0,np.pi,11.4,1570,32,[0.069,0.050],True)
#swiftTurn(0,np.pi*0.25,11.4,1570,32,[0.069,0.050],True)


#gif maker
fig,ax=plt.subplots()  
xData,yData = swiftTurn(0,np.pi*0.25,114,1570,32,[0.069,0.050],True)
#xData,yData = shipTurnMulti(0,np.pi,11.4,1570,32,[0.069,0.050],True)
line,=plt.plot([],[],'b,')
def init():
    ax.axis('equal')
    ax.grid()
    ax.set_xlim(-100,2300)
    ax.set_ylim(-400,2000)
    return line,

def update(i):
    i = i*15
    x = xData[0:i,:]
    y = yData[0:i,:]
    line.set_data(x, y)
    return line,
 
ani=animation.FuncAnimation(fig=fig,func=update,frames=round(len(xData)/15),interval=1,init_func=init,blit=True)
ani.save("charle1.gif",writer='pillow')
plt.show()