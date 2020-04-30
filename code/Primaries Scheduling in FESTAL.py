import numpy as np

class Task:
    def __init__(self,task_id,task_size,arrive_time,deadline):
        self.task_id = task_id
        self.task_size = task_size
        self.arrive_time = arrive_time
        self.deadline = arrive_time + deadline
        # machine number
        self.cur_h_id = -1
        self.cur_v_id = -1
        # time slot 
        self.start_time = 0
        self.finish_time = 0
        # status
        self.allocated = False

class Vm:
    def __init__(self, v_id, mips, h_id, t_cancel):
        self.v_id = v_id
        self.mips = mips
        self.cur_h_id = h_id
        self.t_cancel = t_cancel
        # time_slot = [[task.start_time,task.finish_time],...]
        self.time_slot = []
        # time_ls = [task.task_id:task,...]
        self.task_ls = []

class Host:
    def __init__(self, h_id, mips):
        self.h_id = h_id
        self.mips = mips
        self.remain_mips = mips
        self.vm_ls = {}
        self.p_task_num = 0
        self.active = True
    

class Datacenter:
    v_id = 0
    host_ls = []
    vm_cand = []
    def __init__(self,host_kinds,vm_kinds):
        for i,mips in enumerate(host_kinds):
            print('Initialize host#%d mips:%d'%(i,mips))
            self.host_ls.append(self.__inithost(i,mips))
        self.vm_cand = sorted(vm_kinds,reverse=True)
        print('Vm categories: ',self.vm_cand,' mips')

    def __inithost(self,h_id,mips):
        h = Host(h_id,mips)
        return h
    
    def createVm(self, h, v_id, vm_mips):
        vm = Vm(v_id, vm_mips, h.h_id, 400)
        h.vm_ls[v_id] = vm
        h.remain_mips -= vm.mips
        print('Create vm#%d misp:%d on host#%d'%(v_id, vm.mips, h.h_id))
        return vm
    
    def schedulePTask(self,task):
        # increasing order by the count of scheduled primaries
        host_cand = sorted(self.host_ls,key=lambda x: x.p_task_num)
        # initialization
        find = False
        EFT = float("inf")
        v = None
        delay = 0
        for h_k in host_cand:
            # ## ANAP part
            # if len(h_k.vm_ls) == 0:
            #     v = self.scaleUp(task)
            #     if v != None:
            #         find = True
            #         delay = 15
            #         break
            for v_id in h_k.vm_ls:
                # Calculate the earliest finish time
                EFT_kl,_ = self.calculateEFT(h_k.vm_ls[v_id],task)
                if EFT_kl < task.deadline:
                    find = True
                    if EFT_kl < EFT:
                        EFT = EFT_kl
                        v = h_k.vm_ls[v_id]
        if find == False:
            v = self.scaleUp(task)
            delay = 15
            if v != None:
                find = True
        if find == True:
            self.allocate(v,task,delay)

    def scaleUp(self,task):
        # Sort Ha in a decreasing order by the remaining MIPS;
        h_cand = sorted(self.host_ls,key=lambda x: x.remain_mips,reverse=True)
        # Select a kind of newVm satisfying the equation (5);
        vm_mips = None
        for mips in self.vm_cand:
            if task.task_size/mips + 15 <= (task.deadline - task.arrive_time):
                vm_mips = mips
            # scan
            for h_k in h_cand:
                if vm_mips < h_k.remain_mips:
                    # create VM on Host
                    v = self.createVm(h_k,self.v_id,vm_mips)
                    self.v_id +=1
                    return v
        print('Allocate task#%d failure'%(task.task_id))
        return None
                
    def calculateEFT(self,v,task,delay=0):
        calculation_time = task.task_size/v.mips
        EFT = task.arrive_time+calculation_time + delay
        s_time = task.arrive_time + delay
        time_duration = [s_time,EFT]
        time_slot = v.time_slot 
        for slot in time_slot:
            if time_duration[-1] < slot[0]:
                break
            else:
                s_time = slot[-1]
                EFT = slot[-1]+calculation_time
                time_duration = [slot[-1],EFT]
        return EFT,s_time
        

    def allocate(self,v,task,delay=0):
        f_time,s_time = self.calculateEFT(v,task,delay)
        ## Update task 
        # machine number
        task.cur_h_id = v.cur_h_id
        task.cur_v_id = v.v_id
        # time slot 
        task.start_time = s_time
        task.finish_time = f_time
        # status
        task.allocated = True
        ## Update vm
        v.time_slot.append([task.start_time,task.finish_time])
        v.task_ls.append(task.task_id)
        v.t_cancel = max(v.t_cancel,f_time+200)
        print('Allocate task#%d on vm#%d of host#%d'%(task.task_id,task.cur_v_id,task.cur_h_id))



def generateTask(num_task):
    np.random.seed(720) 
    task_count = 0
    arrive_time = 0
    queue = []
    while True:
        arrive_time += 1
        interval_time = 8 + np.random.randint(3) # 8~10
        s = np.random.poisson(1/interval_time)
        for _ in range(s):
            task_size = 1e5 + np.random.randint(11)*1e4 # 1e5~2e5
            deadline = 400 + np.random.randint(5)*100 # 400~800
            queue.append(Task(task_count,task_size,arrive_time,deadline))
            task_count += 1
        if task_count >= num_task:
            break
    return queue

if __name__ == "__main__":
    # Step1: generate tasks queue
    task_count = 10
    task_queue = generateTask(task_count)
    # Step2: initialize datacenter
    D = Datacenter([2000,2000,3000,3000],[250,500,1000])
    # Step3: Primary schedule 
    for task in task_queue:
        D.schedulePTask(task)
    # Step4: Start Simulation
    print('=============Simulation Start==============')
    for task in task_queue:
        if task.allocated == True:
            print('|Host: %02d |VM: %02d |task_id: %04d |start_time: %5d | finish_time: %5d | SUCCESS |'\
                % (task.cur_h_id,task.cur_v_id,task.task_id,task.start_time,task.finish_time))
        else:
            print('|Host: -- |VM: -- |task_id: %04d |start_time: ----- | finish_time: ----- | FAILURE |'\
                % (task.task_id))
    print('=============Simulation END==============')
    # Step5: Calculate guarantee ratio
    success_count = 0
    for task in task_queue:
        success_count += 1 if task.allocated == True else 0
    gd = success_count/task_count
    print('GD: %.2f' % (gd))
    # if host #2 break down
    success_count = 0
    for task in task_queue:
        success_count += 1 if (task.allocated == True and task.cur_h_id != 1) else 0
    gd_crash = success_count/task_count
    print('if host #2 break down, GD: %.2f' % (gd_crash))
    


