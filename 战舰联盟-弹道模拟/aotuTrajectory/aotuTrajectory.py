import math as M
from matplotlib import pyplot as plt
from multiprocessing import Pool
from matplotlib.font_manager import FontProperties
from matplotlib import animation
from scipy import integrate as int
import numpy as np
import random
import time





class Trajectory:
    '弹道'


    def __init__(self,name,belong,type,caliber,weight,speed,k,kmode,xf,xfmode,theta,data,timeC = 2.57,g = 9.8):
        self.name = name#舰名
        self.belong = belong#从属国籍
        self.type = type#舰种
        self.caliber = caliber#口径
        self.weight = weight#弹重
        self.speed = speed#初速
        self.k = k#风阻系数
        self.kmode = (kmode - 1)/2#风阻与速度指数
        self.xf = xf#矫正系数
        self.xfmode = xfmode#矫正指数
        self.theta = theta#射角
        self.data = data#样本点距离-时间数据
        self.data1 = {}#储存距离-射角数据
        self.data2 = {}#存储距离-末端弹速数据
        self.data3 = {}#存储距离-落角数据
        self.data4 = {}#存储距离-时间数据
        self.data5 = {}#存储特殊距离的距离-射角数据
        self.timeC = timeC#时间修正系数
        self.g = g
        for i in range(1,10):
            if i*5000 < list(data.keys())[-1] - 4000:
                self.data5[i*5000] = 0
            else:
                self.data5[list(data.keys())[-1]] = 0


    #弹道微分方程
    def ode(self,w,t):
        x,vx,y,vy = w[0],w[1],w[2],w[3]
        dx = vx - 1e-2*self.xf*x**self.xfmode
        dvx = -self.k/self.weight*vx*((vx**2+vy**2)**self.kmode)
        dy = vy
        dvy = -self.k/self.weight*vy*((vx**2+vy**2)**self.kmode) - self.g
        return(dx,dvx,dy,dvy)



    #利用data5画特殊距离的弹道
    def drawFar(self,save):
        font = FontProperties(fname=r"c:\windows\fonts\simsun.ttc", size=15)
        for i in list(self.data5.keys()):
            t = np.linspace(0,90,9001)
            x0 = 0
            theta1 = self.data5[i]/100
            theta1 = theta1*M.pi/180
            if self.type == 'DD':
                y0 = 5
            elif self.type == 'BB':
                y0 = 20
            else:
                y0 = 10
            overAll = np.array(
                int.odeint(self.ode,
                           (x0,self.speed*M.cos(theta1),y0,self.speed*M.sin(theta1))
                           ,t
                           )
                )
            overAll = overAll[np.where(overAll[:,2] > 0)]
            x = overAll[:,0]
            y = overAll[:,2]
            plt.plot(x,y,color = 'black')
            length = 0
            #calcu whole length of trajectory
            #z = M.floor((len(x)-1)/20)
            #for j in range(z):
            #    length += M.sqrt((x[j*20+20]-x[j*20])**2+(y[j*20+20]-y[j*20])**2)
            #print(length,i)
        plt.axis('equal')
        plt.grid()
        plt.title('部分距离弹道示意图',fontproperties=font)
        if save:
            plt.savefig('C:/Users/von SolIII/Desktop/新建文件夹/{}/{}/{}.png'.format(self.belong,self.type,self.name+'1'))
        else:
            plt.show()
        plt.close()


    def gifMaker(self,save = 0):
        self.compare()
        dist = list(self.data5.keys())[-2]
        print(self.data5)
        t = np.linspace(0,90,9001)
        x0 = 0
        theta1 = self.data5[dist]/100
        theta1 = theta1*M.pi/180
        if self.type == 'DD':
            y0 = 5
        elif self.type == 'BB':
            y0 = 20
        else:
            y0 = 10
        overAll = np.array(
            int.odeint(self.ode,
                        (x0,self.speed*M.cos(theta1),y0,self.speed*M.sin(theta1))
                        ,t
                        )
            )
        overAll = overAll[np.where(overAll[:,2] > 0)]
        xData = overAll[:,0]
        print(len(xData))
        yData = np.ones(len(xData))
        fig,ax=plt.subplots()  
        line,=plt.plot([],[],'b,')
        def init():
            #ax.axis('equal')
            ax.grid()
            ax.set_xlim(0,2e4)
            ax.set_ylim(0,2)
            return line,

        def update(i):
            i = i
            x = xData[0:i]
            y = yData[0:i]
            line.set_data(x, y)
            return line,
        ani=animation.FuncAnimation(fig=fig,func=update,frames=round(len(xData)),interval=0.01,init_func=init,blit=True)
        ax.scatter([5e3,10e3,15e3,20e3],[1,1,1,1],marker = 'x')
        if save:
            ani.save("charle1.gif",writer='pillow')
        else:
            plt.show()
        return
        

    #指定射角，画出弹道并输出详细参数
    def angle(self,theta,draw):
        t = np.linspace(0,90,9001)
        x0 = 0
        theta1 = theta/100
        theta1 = theta1*M.pi/180
        if self.type == 'DD':
            y0 = 5
        elif self.type == 'BB':
            y0 = 20
        else:
            y0 = 10
        overAll = np.array(
            int.odeint(self.ode,
                       (x0,self.speed*M.cos(theta1),y0,self.speed*M.sin(theta1))
                       ,t
                       )
            )
        overAll = overAll[np.where(overAll[:,2] > 0)]
        time = len(overAll)/100
        x = overAll[:,0]
        vx = overAll[:,1][-1]
        y = overAll[:,2]
        vy = overAll[:,3][-1]
        v = M.sqrt(vx**2+vy**2)
        theta1 = -M.atan(vy/(vx-self.xf*x[-1]**self.xfmode*0.01))*180/M.pi
        plt.plot(x,y)
        plt.axis('equal')
        if draw:
            plt.show()
        else:
            print(theta/100,v,x[-1],theta1,time/self.timeC,vy)
        plt.close()


    #同angle，只return距离和时间
    def tryangle(self,theta):
        t = np.linspace(0,90,9001)
        x0 = 0
        theta1 = theta/100-1
        theta1 = theta1*M.pi/180
        if self.type == 'DD':
            y0 = 5
        elif self.type == 'BB':
            y0 = 20
        else:
            y0 = 10
        overAll = np.array(
            int.odeint(self.ode,
                       (x0,self.speed*M.cos(theta1),y0,self.speed*M.sin(theta1))
                       ,t
                       )
            )
        overAll = overAll[np.where(overAll[:,2] > 0)]
        time = len(overAll)/100
        x = overAll[:,0][-1]
        return [x,time/self.timeC]


    #废弃
    def write(self,theta):
        f = open('current.txt','a')
        t = np.linspace(0,90,9001)
        x0 = 0
        theta1 = theta/100-1
        theta1 = theta1*M.pi/180
        if self.type == 'DD':
            y0 = 5
        elif self.type == 'BB':
            y0 = 20
        else:
            y0 = 10
        overAll = np.array(
            int.odeint(self.ode,
                       (x0,self.speed*M.cos(theta1),y0,self.speed*M.sin(theta1))
                       ,t
                       )
            )
        overAll = overAll[np.where(overAll[:,2] > 0)]
        time = len(overAll)/100
        x = overAll[:,0][-1]
        vx = overAll[:,1][-1]
        vy = overAll[:,3][-1]
        v = M.sqrt(vx**2+vy**2)
        theta1 = -M.atan(vy/(vx-self.xf*x**self.xfmode*0.01))*180/M.pi
        f.write(str(theta/100-1)+','+str(v)+','+str(x)+','+str(-theta1)+','+str(time/self.timeC)+'\n')
       

    #按射角写入数据
    def buildSin(self,theta):
        t = np.linspace(0,90,9001)
        x0 = 0
        theta1 = theta/100
        theta1 = theta1*M.pi/180
        if self.type == 'DD':
            y0 = 5
        elif self.type == 'BB':
            y0 = 20
        else:
            y0 = 10
        overAll = np.array(
            int.odeint(self.ode,
                       (x0,self.speed*M.cos(theta1),y0,self.speed*M.sin(theta1))
                       ,t
                       )
            )
        overAll = overAll[np.where(overAll[:,2] > 0)]
        time = len(overAll)/100
        x = overAll[:,0][-1]
        vx = overAll[:,1][-1]
        vy = overAll[:,3][-1]
        theta1 = -M.atan(vy/(vx-self.xf*x**self.xfmode*0.01))*180/M.pi
        self.data1[x] = theta/100
        self.data2[x] = M.sqrt(vx**2+vy**2)
        self.data3[x] = theta1
        self.data4[x] = time/self.timeC


    #根据数据画图
    def drawAll(self,start,end,save):
        font = FontProperties(fname=r"c:\windows\fonts\simsun.ttc", size=15)
        plt.figure(figsize = (12,8))
        plt.subplot(2,2,1).set_title('射程(m)-炮射角(°)',fontproperties=font)
        plt.subplot(2,2,2).set_title('射程(m)-末端弹速(m/s)',fontproperties=font)
        plt.subplot(2,2,3).set_title('射程(m)-落角(°)',fontproperties=font)
        plt.subplot(2,2,4).set_title('射程(m)-时间(s)',fontproperties=font)
        for i in range(start,end):
            self.buildSin(i)
        plt.subplot(2,2,1).plot(list(self.data1.keys()),list(self.data1.values()),color = 'black')
        plt.subplot(2,2,2).plot(list(self.data2.keys()),list(self.data2.values()),color = 'black')
        plt.subplot(2,2,3).plot(list(self.data3.keys()),list(self.data3.values()),color = 'black')
        plt.subplot(2,2,4).plot(list(self.data4.keys()),list(self.data4.values()),color = 'black')
        plt.subplot(2,2,1).grid()
        plt.subplot(2,2,2).grid()
        plt.subplot(2,2,3).grid()
        plt.subplot(2,2,4).grid()
        if save:
            plt.savefig('C:/Users/von SolIII/Desktop/新建文件夹/{}/{}/{}.png'.format(self.belong,self.type,self.name))
        else:
            plt.show()
        plt.close()


    #输出所有数据，若无数据则生成再输出
    def showAll(self):
        diff,start,end = self.compare()
        if self.data1:
            print('射程(m)-炮射角(°):')
            print(self.data1)
            print('射程(m)-末端弹速(m/s):')
            print(self.data2)
            print('射程(m)-攻角(°):')
            print(self.data3)
            print('射程(m)-时间(s):')
            print(self.data4)
        else:
            for i in range(start,end):
                self.buildSin(i)
            print('射程(m)-炮射角(°):')
            print(self.data1)
            print('射程(m)-末端弹速(m/s):')
            print(self.data2)
            print('射程(m)-攻角(°):')
            print(self.data3)
            print('射程(m)-时间(s):')
            print(self.data4)


    #与样本对比，输出误差，起点，终点
    def compare(self,mode = 0):
        keys = list(self.data.keys())
        values = list(self.data.values())
        #print(len(keys))
        keys1 = []
        values1 = []
        diff = [[],[]]
        count = 0
        if self.type == 'DD' or self.type == 'CA':
            step = 50
        else:
            step = 50
        for i in range(0,self.theta,50):
            #print(i)
            x,time = self.tryangle(i)
            #print(x)
            if abs(x-keys[count])<step:
                if count == 0:
                    start = i
                count += 1
                keys1.append(x)
                values1.append(time)
                if keys[count-1] in list(self.data5.keys()):
                    self.data5[keys[count-1]] = i-100
                if count == len(keys):
                    end = i 
                    break
            elif x > keys[count]:
                for j in range(200):
                    #print(i-j,end='')
                    x,time = self.tryangle(i-j)
                    if abs(x-keys[count])<step:
                        if count == 0:
                            start = i-j
                        if keys[count] in list(self.data5.keys()):
                            self.data5[keys[count]] = i- j - 100
                        count += 1
                        keys1.append(x)
                        values1.append(time)
                        break
                if count == len(keys):
                    end = i-j
                    break
        #print(keys1,values1)
        for i in range(len(keys)):
            diff[0].append(abs(values[i]-values1[i])*100)
            diff[1].append((values[i]/values1[i]-1)*100)
        if mode:
            print(diff)
        return diff,start-100,end-100


    #输出归一化风阻-形状参数
    def guiyi(self):
        print(self.k/self.weight*self.caliber)


    #输出衰减参数-初始加速度
    def shuaijian(self):
        print(self.k/self.weight*self.speed**self.kmode)


    #完成参数调整，一揽子输出
    def done(self):
        diff,start,end = self.compare()
        print(diff,start,end)
        self.guiyi()
        self.shuaijian()
        self.drawAll(start,end)
        self.drawFar()


    #误差
    def loss(self,mode):
        diff,start,end = self.compare(1)
        loss = 0
        if mode:
            for i in diff[0][0:-2]:
                loss += i
        else:
            for i in diff[0][-1:-3:-1]:
                loss += i
        if max(diff[0][-1:1:-1]) > 6:
            result = 0
        else:
            result = 1
        if result:
            return 0
        else:
            return loss


    #坐标下降法-调整风阻
    def onlyK(self,step = 5e-6,epoch = 5):
        delta = self.k/8
        count = 0
        min = [1E10,1]
        while count < epoch:
            loss = self.loss(1)
            print(loss,self.k)
            if loss < min[0]:
                min = [loss,self.k]
                if min[0] < 5.1:
                    break
            self.k = self.k+delta
            loss1 = self.loss(1)
            print(loss1,self.k)
            if loss1 < min[0]:
                min = [loss1,self.k]
                if min[0] < 5.1:
                    break
            if loss1 < loss:
                self.k += step
                step = step/2
            elif loss1 > loss:
                self.k -= step
                step = step/2
            else:
                break
            count += 1
        print(min[1])


    #坐标下降法-调整矫正
    def onlyFx(self,step,epoch = 5):
        delta = self.xf/8
        count = 0
        min = [1E10,1]
        while count < epoch:
            loss = self.loss(0)
            print(loss,self.xf)
            if loss < min[0]:
                min = [loss,self.xf]
                if min[0] < 5.1:
                    break
            self.xf = self.xf+delta
            loss1 = self.loss(0)
            print(loss1,self.xf)
            if loss1 < min[0]:
                min = [loss1,self.xf]
                if min[0] < 5.1:
                    break
            if loss1 < loss:
                self.xf += step
                step = step/2
            elif loss1 > loss:
                self.xf -= step
                step = step/2
            else:
                break
            count += 1
        print(min[1])



if __name__ == '__main__':
    '''
    tra0 = Trajectory('MTN','USN','BB',406,1225,762,5.05e-5,3,6E-14,4,4500,
    {1e3:0.5,5e3:2.7,10e3:5.9,15e3:9.6,20e3:14.5,24.2e3:22.6})
    tra1 = Trajectory('IOWA','USN','BB',406,1225,762,5.18e-5,3,6.45e-14,4,4500,
    {1e3:0.5,5e3:2.8,10e3:5.9,15e3:9.7,20e3:14.7,23.3e3:20.6})
    tra2 = Trajectory('MS','USN','BB',406,1225,701,5.85e-5,3,3.9E-16,4.5,4500,
    {1e3:0.55,5e3:3.0,10e3:6.5,15e3:10.6,20e3:16.4,23e3:23.3})
    tra3 = Trajectory('SY','IJN','BB',510,2000,780,6.44e-5,3,10E-17,4.5,4500,
    {1e3:0.5,5e3:2.7,10e3:5.6,15e3:8.9,20e3:12.7,25e3:17.6,27.6e3:21})
    tra4 = Trajectory('YMT','IJN','BB',460,1460,780,5e-5,3,1.12E-16,4.5,4500,
    {1e3:0.5,5e3:2.7,10e3:5.6,15e3:8.9,20e3:12.9,25e3:18,26.6E3:20.2})
    tra5 = Trajectory('AMG','IJN','BB',410,1000,806,4.8e-5,3,5E-20,5.5,4500,
    {1e3:0.5,5e3:2.7,10e3:5.7,15e3:9.5,19.8e3:15.4})
    tra5_1 = Trajectory('AMG_1','IJN','BB',410,1000,806,4.22e-5,3,8.18E-14,4,4500,
    {1e3:0.5,5e3:2.6,10e3:5.6,15e3:9.2,20e3:14.3,21.7e3:16.9})
    tra6 = Trajectory('NGT','IJN','BB',410,1000,806,4.5e-5,3,11E-14,4,4500,
    {1e3:0.5,5e3:2.6,10e3:5.7,15e3:9.4,20e3:15.2,20.4e3:15.9})
    tra7 = Trajectory('FS','IJN','BB',356,635,775,2.9e-5,3,6.25E-16,4.5,4500,
    {1e3:0.5,5e3:2.7,10e3:5.9,15e3:9.7,20e3:15.2,21.8e3:18.8})
    tra8 = Trajectory('L3','HMS','BB',457,1506,762,6.23e-5,3,7e-23,6,4500,
    {1e3:0.5,5e3:2.8,10e3:5.9,15e3:9.5,20e3:14.0,25e3:21.4,25.2e3:22})
    tra9 = Trajectory('LION','HMS','BB',406,1180,725,5.38e-5,3,6.35e-14,4,4500,
    {1e3:0.5,5e3:2.9,10e3:6.2,15e3:10.3,20e3:15.8,22.8e3:21.6})
    tra10 = Trajectory('KGV','HMS','BB',356,721,757,3.32e-5,3,5.4E-16,4.5,4500,
    {1e3:0.5,5e3:2.8,10e3:6.0,15e3:9.9,20e3:15.4,22.1e3:19.5})
    tra11 = Trajectory('NS','HMS','BB',406,929,788,4.65e-5,3,24E-12,3.5,4500,
    {1e3:0.5,5e3:2.7,10e3:5.9,15e3:10.2,18.8e3:15.9})
    tra12 = Trajectory('H42','KMS','BB',480,1625,805,6.45e-5,3,2.15E-18,5,4500,
    {1e3:0.5,5e3:2.6,10e3:5.6,15e3:9,20e3:13.3,24e3:18.7})
    tra13 = Trajectory('H422','KMS','BB',420,1250,820,4.6e-5,3,5.6E-14,4,4500,
    {1e3:0.5,5e3:2.5,10e3:5.4,15e3:8.8,20e3:13.1,24e3:18.4})
    tra14 = Trajectory('H39','KMS','BB',406,1030,810,3.89e-5,3,5.8E-14,4,4500,
    {1e3:0.5,5e3:2.6,10e3:5.5,15e3:8.9,20e3:13.4,23.6e3:18.3})
    tra15 = Trajectory('BSM','KMS','BB',380,800,820,3.6e-5,3,6.8E-16,4.5,4500,
    {1e3:0.5,5e3:2.6,10e3:5.6,15e3:9.2,20e3:14.5,21.2e3:16.6})
    tra16 = Trajectory('SU','SN','BB',406,1108,869,3.01e-5,3,0,0,4500,
    {1E3:0.5,15e3:7.8,20e3:11.0,26.2e3:15.7})
    tra17 = Trajectory('L747','HMS','BB',406,1180,747,5.58e-5,3,3.12E-18,5,4500,
    {1e3:0.5,5e3:2.8,10e3:6.1,15e3:10.0,20e3:15.4,22.8e3:21.0})
    tra18 = Trajectory('CR','USN','BB',406,1017,768,5.872e-5,3,24.3e-14,4,4500,
    {1e3:0.5,5e3:2.8,10e3:6.2,15e3:11,17.8e3:16.5})
    tra19 = Trajectory('NM','USN','BB',356,680,823,2.55e-5,3,98.8E-8,2.5,4500,
    {1e3:0.5,5e3:2.6,10e3:5.6,15e3:10.9,16.5e3:14.3})
    tra20 = Trajectory('GN','KMS','BB',356,800,819,3.6e-5,3,27E-10,3,4500,
    {1e3:0.5,5e3:2.6,10e3:5.6,15e3:9.6,19.5e3:15.3})
    tra21 = Trajectory('RC','MNF','BB',380,890,850,3.6e-5,3,1.05E-22,6,4500,
    {1e3:0.5,5e3:2.5,10e3:5.3,15e3:8.6,20e3:12.7,24.3e3:18.6})
    tra22 = Trajectory('DK','MNF','BB',330,560,869,2.25e-5,3,4.5E-22,6,4500,
    {1e3:0.5,5e3:2.4,10e3:5.2,15e3:8.6,18.4e3:11.7})
    tra23 = Trajectory('AD','RM','BB',320,525,830,2.3e-5,3,11E-14,4,4500,
    {1e3:0.5,5e3:2.6,10e3:5.5,15e3:9.2,17.5e3:11.5})
    tra24 = Trajectory('HOOD','HMS','BC',380,879,752,4.6e-5,3,1.37E-13,4,4500,
    {1e3:0.5,5e3:2.8,10e3:6.2,15e3:10.5,18.8e3:15.7})
    tra25 = Trajectory('G3','HMS','BC',406,929,797,4.11e-5,3,3.4E-18,5,4500,
    {1e3:0.5,5e3:2.6,10e3:5.7,15e3:9.3,20e3:14.2,22e3:17.3})
    tra26 = Trajectory('VG','HMS','BC',380,879,803,4.11e-5,3,9.15E-14,4,4500,
    {1e3:0.5,5e3:2.6,10e3:5.7,15e3:9.5,20e3:15.1,20.6e3:16})
    tra27 = Trajectory('VV','RM','BB',381,885,880,3.1e-5,3,2.1E-14,4,4500,
    {1e3:0.5,2e3:0.9,3e3:1.4,4e3:1.9,5e3:2.4,6e3:2.9,7e3:3.4,8e3:3.9,9e3:4.5,10e3:5.0,11e3:5.6,12e3:6.2,14e3:6.8,14e3:7.4,15e3:8.1,16e3:8.8,17e3:9.4,18e3:10.2,19e3:11,20e3:11.8,20.1e3:11.9})
    tra28 = Trajectory('FR','MNF','BB',450,885,880,3e-5,3,2.45E-16,4.5,4500,
    {1e3:0.5,5e3:2.4,10e3:5.0,15e3:8.1,20e3:11.8,25e3:16.9,26.3e3:18.9})
    tra29 = Trajectory('AL','MNF','BB',380,890,850,3.7e-5,3,3.45E-18,5,4500,
    {1e3:0.5,5e3:2.5,10e3:5.3,15e3:8.7,20e3:13.2,23.2e3:18.2})
    tra30 = Trajectory('JB','MNF','BB',380,890,850,3.4e-5,3,2.55E-18,5,4500,
    {1e3:0.5,5e3:2.5,10e3:5.3,15e3:8.5,20e3:12.7,24.5e3:18.9})
    tra31 = Trajectory('GA','MNF','BB',380,890,850,3.5e-5,3,2.86E-18,5,4500,
    {1e3:0.5,5e3:2.5,10e3:5.3,15e3:8.6,20e3:12.8,24.1e3:18.9})
    tra32 = Trajectory('LY','MNF','BB',340,540,794,2.95e-5,3,12.2E-18,5,4500,
    {1e3:0.5,5e3:2.7,10e3:5.9,15e3:10.2,18.6e3:16.7})
    tra33 = Trajectory('H41','KMS','BB',420,1250,820,4.65e-5,3,5.9E-14,4,4500,
    {1e3:0.5,5e3:2.5,10e3:5.4,15e3:8.8,20e3:13.2,23.7e3:18.1})
    tra34 = Trajectory('LA','USN','BB',406,954,914,2.5e-5,3,8.9E-19,5,4500,
    {1e3:0.4,5e3:2.3,10e3:4.7,15e3:7.5,20e3:10.6,25e3:14.4,26.7e3:16})

    tra100 = Trajectory('DM','USN','CA',203,152,762,10.2e-6,3,3.02E-15,4.5,4500,
    {1e3:0.5,5e3:2.9,10e3:6.4,15e3:12.3,16e3:14.9})
    tra101 = Trajectory('BM','USN','CA',203,152,762,10.4e-6,3,2.18E-17,5,4500,
    {1e3:0.5,5e3:2.9,10e3:6.4,15e3:12.0,15.8e3:13.7})
    tra102 = Trajectory('NO','USN','CA',203,118,853,7.2e-6,3,2.218E-17,5,4500,
    {1e3:0.5,5e3:2.5,10e3:5.7,15e3:10.4,16.1e3:12.3})
    tra103 = Trajectory('PC','USN','CA',203,118,853,7.2e-6,3,2.76E-17,5,4500,
    {1e3:0.5,5e3:2.5,10e3:5.7,15e3:10.8,15.6e3:11.9})
    tra104 = Trajectory('IBK','IJN','CA',203,126,920,4.5e-6,3,4.5E-18,5,4500,
    {1e3:0.4,5e3:2.3,10e3:4.9,15e3:7.9,18e3:10.2})
    tra105 = Trajectory('IBK2','IJN','CA',203,126,840,5.188e-6,3,4.5E-18,5,4500,
    {1e3:0.5,5e3:2.5,10e3:5.4,15e3:8.8,18e3:11.4})
    tra106 = Trajectory('TK','IJN','CA',203,126,840,5.5e-6,3,2E-15,4.5,4500,
    {1e3:0.5,5e3:2.5,10e3:5.5,15e3:9.4,16.1e3:10.5})
    tra107 = Trajectory('MK','IJN','CA',203,126,840,5.95e-6,3,2.3E-13,4,4500,
    {1e3:0.5,5e3:2.5,10e3:5.6,15e3:9.6,15.5e3:10.1})
    tra108 = Trajectory('Algerie','MNF','CA',203,134,820,7.5e-6,3,14.8e-18,5,4500,
    {1e3:0.5,5e3:2.6,10e3:5.8,15e3:10.1,18e3:15.6})
    tra109 = Trajectory('Algerie-1','MNF','CA',203,134,820,5.7e-6,3,3.8E-18,5,4500,
    {1e3:0.5,5e3:2.6,10e3:5.5,15e3:9.1,18e3:11.7})
    tra110 = Trajectory('Kronshtadt','SN','CA',305,471,920,2.03e-5,3,2.0E-13,4,4500,
    {1e3:0.4,5e3:2.3,10e3:5.0,15e3:8.6,19.4e3:14.1})

    
    tra300 = Trajectory('GR','USN','DD',127,25,792,2.15e-6,3,16.8E-13,4,4500,
    {1e3:0.5,5e3:2.9,7.5E3:4.7,10e3:7.3,11.1e3:9.3})
    tra301 = Trajectory('AZ','IJN','DD',100,13,1000,7.2e-7,3,850E-15,4,4500,
    {1e3:0.4,2e3:0.8,3e3:1.2,4e3:1.7,5e3:2.2,6e3:2.7,7e3:3.2,8e3:3.8,9e3:4.4,10e3:5.1,12e3:6.7})
    tra302 = Trajectory('47','SN','DD',130,33,950,1.995e-6,3,600E-15,4,4500,
    {1e3:0.4,2.5e3:1.1,5e3:2.3,7.5E3:3.7,10e3:5.3,11.2e3:6.3})
    tra303 = Trajectory('SK','IJN','DD',127,23,915,1.8e-6,3,1.6E-12,4,4500,
    {1e3:0.4,5e3:2.5,9.8e3:6.0}) 
    tra304 = Trajectory('FT','USN','DD',127,25,792,2e-6,3,1.37E-12,4,4500,
    {1e3:0.5,5e3:2.8,7.5E3:4.6,10e3:7,11.7e3:9.8})
    tra305 = Trajectory('LF','USN','DD',127,25,792,1.9e-6,3,6E-13,4,4500,
    {1e3:0.5,5e3:2.8,7.5E3:4.5,10e3:6.5,11.6e3:8.2})
    tra306 = Trajectory('BS','USN','DD',127,25,792,2e-6,3,17.5E-11,3.5,4500,
    {1e3:0.5,5e3:2.8,7.5E3:4.7,10e3:7.2,11.5e3:10.3})
    tra307 = Trajectory('MH','USN','DD',127,25,792,2.15e-6,3,15.2E-13,4,4500,
    {1e3:0.5,5e3:2.9,7.5E3:4.7,10e3:7.2,11.6e3:10.3})
    tra308 = Trajectory('SM','USN','DD',127,25,792,2.1e-6,3,9.2E-13,4,4500,
    {1e3:0.5,5e3:2.8,10e3:6.8,12.8e3:11.4})
    tra309 = Trajectory('KR','IJN','DD',127,23,915,1.8e-6,3,2.2E-12,4,4500,
    {1e3:0.4,5e3:2.5,9.4e3:5.8}) 
    tra310 = Trajectory('FK','IJN','DD',127,23,915,1.8e-6,3,1.6E-12,4,4500,
    {1e3:0.4,5e3:2.5,9.7e3:5.9}) 
    tra311 = Trajectory('FK','IJN','DD',127,23,915,1.8e-6,3,1.6E-12,4,4500,
    {1e3:0.4,5e3:2.5,9.9e3:6.1}) 
    tra312 = Trajectory('HH','IJN','DD',127,23,915,1.8e-6,3,4.6E-12,4,4500,
    {1e3:0.4,5e3:2.5,8.4e3:5.2}) 
    tra313 = Trajectory('TK','SN','DD',130,33,869,1.9e-6,3,3.8E-13,4,4500,
    {1e3:0.5,2.5e3:1.2,5e3:2.5,7.5E3:3.9,10e3:5.6,12.8e3:7.9})
    tra314 = Trajectory('LG','SN','DD',130,33,869,2.1e-6,3,8E-13,4,4500,
    {1e3:0.5,2.5e3:1.2,5e3:2.5,7.5E3:4,10e3:5.9,11.2e3:6.9})
    tra315 = Trajectory('AZ-1','IJN','DD',100,13,1000,8.125e-7,3,1300E-15,4,4500,
    {1e3:0.4,2e3:0.8,3e3:1.2,4e3:1.7,5e3:2.2,6e3:2.8,7e3:3.3,8e3:3.9,9e3:4.6,10e3:5.3,11e3:6.3,12e3:7.5})
    tra316 = Trajectory('AZ-2','IJN','DD',100,13,1000,8.6e-7,3,17.5E-13,4,4500,
    {1e3:0.4,2e3:0.8,3e3:1.3,4e3:1.7,5e3:2.2,6e3:2.8,7e3:3.4,8e3:4,9e3:4.7,10e3:5.6,11e3:6.7,12e3:8.6})
    
    
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        
    '''
    
    tra2 = Trajectory('MTN','USN','BB',406,1225,762,3.5e-2,2,0,0,4600,
    {1e3:0.5,5e3:2.7,10e3:5.9,15e3:9.6,20e3:14.5,24.2e3:22.6},2.57,20)
    tra100 = Trajectory('DM','USN','CA',203,152,762,3.2e-4,2.5,0,0,4500,
    {1e3:0.5,5e3:2.9,10e3:6.4,15e3:12.3,16e3:14.9})
    #print(tra2.data5)
    #print(tra2.tryangle(4500))
    tra2.angle(4500,0)
    #tra2.gifMaker()
    tra2.onlyK(1e-5)
    #tra2.onlyFx(1E-13,10)                                                                                                                                                                                                                                                                                                                              
    #tra2.done()
    #tra0.drawFar(2693)
    #tra0.drawAll(10,2693)
    #print(tra5.compare())
    diff,start,end = tra2.compare()
    print(diff,start,end)
    #tra2.drawAll(start,end,0)
    for i in range(start,end):
        tra2.buildSin(i)
    tra2.drawFar(0)