import numpy as np

class Task:
    def __init__(self,task_id,task_size,arrive_time,deadline):
        self.task_id = task_id
        self.task_size = task_size
        self.arrive_time = arrive_time
        self.deadline = arrive_time + deadline
        # machine 
        self.p_cur_h = -1
        self.p_cur_v = -1
        self.b_cur_h = -1
        self.b_cur_v = -1
        # time slot 
        self.p_start_time = -1
        self.p_finish_time = -1
        self.b_start_time = -1
        self.b_finish_time = -1
        # status
        self.p_allocated = False
        self.b_allocated = False
        self.finish = False

class Vm:
    def __init__(self, v_id, h, mips, t_cancel):
        self.v_id = v_id
        self.mips = mips
        self.cur_h = h
        self.t_cancel = t_cancel
        # time_slot = [[task.start_time,task.finish_time],...]
        self.time_slot = []
        # time_ls = [task.task_id,...]
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
        vm = Vm(v_id, h, vm_mips, 400)
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
            # #=============different with FESTAL START==============
            # # By following AEAP rule, we should allocate primary task on the no p task host.
            # if len(h_k.vm_ls) == 0:
            #     v = self.scaleUp(task)
            #     delay = 15
            #     if v != None:
            #         find = True
            #         break
            # #=============different with FESTAL END==============
            for v_id in h_k.vm_ls:
                # Calculate the earliest finish time
                EFT_kl,_ = self.calculateEFT(h_k.vm_ls[v_id],task)
                if EFT_kl <= task.deadline:
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
    
    def scheduleBTask(self,task):
        # Sort Ha in an increasing order by the count of scheduled primaries;
        host_cand = sorted(self.host_ls,key=lambda x: x.p_task_num,reverse=True)
        # initialization
        find = False
        LST = 0
        v = None
        delay = 0
        for h_k in host_cand:
            # rule check
            if self.rulecheck1(h_k,task):
                continue
            for v_id in h_k.vm_ls:
                # Calculate the earliest finish time
                LST_kl,f_time = self.calculateLST(h_k.vm_ls[v_id],task,delay)
                # passive mode
                if (f_time <= task.deadline) & (LST_kl >= task.p_finish_time):
                # # active mode
                # if (f_time <= task.deadline) & (LST_kl >= task.arrive_time):
                    find = True
                    if LST_kl > LST:
                        LST = LST_kl
                        v = h_k.vm_ls[v_id]
        if find == False:
            v = self.BscaleUp(task)
            delay = 15
            if v != None:
                find = True
        if find == True:
            self.Ballocate(v,task,delay)

    
    def calculateLST(self,v,task,delay):
        calculation_time = task.task_size/v.mips
        f_time = task.deadline
        LST = task.deadline - calculation_time
        time_duration = [LST,f_time]
        time_slot = v.time_slot[::-1]
        for slot in time_slot:
            if time_duration[0] > slot[-1]:
                break
            else:
                f_time = slot[0]
                LST = f_time - calculation_time
                time_duration = [f_time,LST]

        return LST,f_time
    
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
                time_duration = [s_time,EFT]
        return EFT,s_time
    
    def BscaleUp(self,task):
        # Sort Ha in a decreasing order by the remaining MIPS;
        h_cand = sorted(self.host_ls,key=lambda x: x.remain_mips,reverse=True)
        # Select a kind of newVm satisfying the equation (5);
        vm_mips = None
        for mips in self.vm_cand:
            # as late as possible
            if self.rulecheck2(task,mips):
                vm_mips = mips
            else:
                break
            # scan
            for h_k in h_cand:
                # rule check
                if self.rulecheck1(h_k,task):
                    continue
                if vm_mips < h_k.remain_mips:
                    # create VM on Host
                    v = self.createVm(h_k,self.v_id,vm_mips)
                    self.v_id +=1
                    return v
        print('Allocate B-task#%d failure'%(task.task_id))
        # Reject task B and task P
        self.reject(task)
        return None
    
    def scaleUp(self,task):
        # Sort Ha in a decreasing order by the remaining MIPS;
        h_cand = sorted(self.host_ls,key=lambda x: x.remain_mips,reverse=True)
        # Select a kind of newVm satisfying the equation (5);
        vm_mips = None
        for mips in self.vm_cand:
            # as early as possible
            if task.task_size/mips + 15 <= (task.deadline - task.arrive_time):
                vm_mips = mips
            # scan
            for h_k in h_cand:
                if vm_mips < h_k.remain_mips:
                    # create VM on Host
                    v = self.createVm(h_k,self.v_id,vm_mips)
                    self.v_id +=1
                    return v
        print('Allocate P-task#%d failure'%(task.task_id))
        return None

    def Ballocate(self,v,task,delay=0):
        s_time,f_time = self.calculateLST(v,task,delay)
        ## Update task 
        # machine number
        task.b_cur_h = v.cur_h
        task.b_cur_v = v
        # time slot 
        task.b_start_time = s_time
        task.b_finish_time = f_time
        # status
        task.b_allocated = True
        ## Update vm
        v.time_slot.append([task.b_start_time,task.b_finish_time])
        v.time_slot.sort()
        v.t_cancel = max(v.t_cancel,f_time+200)
        print('Allocate B-task#%d on vm#%d of host#%d'%(task.task_id,task.b_cur_v.v_id,task.b_cur_h.h_id))


    def allocate(self,v,task,delay=0):
        f_time,s_time = self.calculateEFT(v,task,delay)
        ## Update task 
        # machine number
        task.p_cur_h = v.cur_h
        task.p_cur_v = v
        # time slot 
        task.p_start_time = s_time
        task.p_finish_time = f_time
        # status
        task.p_allocated = True
        ## Update vm
        v.time_slot.append([task.p_start_time,task.p_finish_time])
        v.time_slot.sort()
        v.task_ls.append(task.task_id)
        v.t_cancel = max(v.t_cancel,f_time+200)
        ## Update host
        v.cur_h.p_task_num += 1
        print('Allocate P-task#%d on vm#%d of host#%d'%(task.task_id,task.p_cur_v.v_id,task.p_cur_h.h_id))

 
    def reject(self,task):
        ## remove p_task from p_vm
        p_v = task.p_cur_v
        p_v.time_slot.remove([task.p_start_time,task.p_finish_time])
        p_v.task_ls.remove(task.task_id)
        ## Update task status
        # machine 
        task.p_cur_h = -1
        task.p_cur_v = -1
        task.b_cur_h = -1
        task.b_cur_v = -1
        # time slot 
        task.p_start_time = -1
        task.p_finish_time = -1
        task.b_start_time = -1
        task.b_finish_time = -1
        # status
        task.p_allocated = False
        task.b_allocated = False 

    def rulecheck1(self,h,task):
        # host conflict check
        if task.p_cur_h == h:
            return True
        return False
    def rulecheck2(self,task,mips):
        # finish time check
        if (task.deadline - task.task_size/mips) >= task.p_finish_time:
            if (task.deadline - task.task_size/mips) >= task.arrive_time + 15:
                return True
        return False

def processTask(task_ls,time):
    for task in task_ls:
        if task.p_finish_time <= time:
            ### task finished
            ## remove p_task from p_vm
            p_v = task.p_cur_v
            p_v.time_slot.remove([task.p_start_time,task.p_finish_time])
            p_v.task_ls.remove(task.task_id)
            b_v = task.b_cur_v
            b_v.time_slot.remove([task.b_start_time,task.b_finish_time])

            # status
            task.finish = True
            print('Task#%d finished!'%(task.task_id))
            ## remove task in task_onboard
            task_ls.remove(task)


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

# Dynamic Simulation Backup mode: Passive
if __name__ == "__main__":
    # Step 1: generate tasks queue
    task_count = 5000
    task_queue = generateTask(task_count)
    # Step 2: initialize datacenter
    D = Datacenter([2000,2000,3000,3000],[250,500,1000])
    task_onboard = []
    print('========Time:0 s ========')
    for task in task_queue:
        # Step 3: Processing the task allocated
        TIME = task.arrive_time
        processTask(task_onboard,TIME)
        # Step 4: Primary schedule
        D.schedulePTask(task)
        if task.p_allocated == True:
            # Step 4: Backup schedule
            D.scheduleBTask(task)
        if task.b_allocated == True:
            task_onboard.append(task)
        print('========Time:%d s ========'%(TIME))
    processTask(task_onboard,float('inf'))
    print('========Time:inf s ========')
    # Step 5: Calculate guarantee ratio
    success_count = 0
    for task in task_queue:
        success_count += 1 if task.finish == True else 0
        gd = success_count/task_count
    print('GD: %.2f' % (gd))


# # Static Simulation Backup mode: Active
# if __name__ == "__main__":
#     # Step1: generate tasks queue
#     task_count = 10000
#     task_queue = generateTask(task_count)
#     # Step2: initialize datacenter
#     D = Datacenter([2000,2000,3000,3000],[250,500,1000])
#     # Step3: Primary schedule 
#     for task in task_queue:
#         D.schedulePTask(task)
#         if task.p_allocated == True:
#             D.scheduleBTask(task)
#     # Step4: Start Simulation
#     print('=============Simulation Start==============')
#     for task in task_queue:
#         if task.p_allocated == True:
#             print('|Host: %02d |VM: %02d |P-task_id: %04d |start_time: %5d | finish_time: %5d | SUCCESS |'\
#                 % (task.p_cur_h.h_id,task.p_cur_v.v_id,task.task_id,task.p_start_time,task.p_finish_time))
#             print('|Host: %02d |VM: %02d |B-task_id: %04d |start_time: %5d | finish_time: %5d | SUCCESS |'\
#                 % (task.b_cur_h.h_id,task.b_cur_v.v_id,task.task_id,task.b_start_time,task.b_finish_time))
#         else:
#             print('|Host: -- |VM: -- |X-task_id: %04d |start_time: ----- | finish_time: ----- | FAILURE |'\
#                 % (task.task_id))
#     print('=============Simulation END==============')
#     # Step5: Calculate guarantee ratio
#     success_count = 0
#     for task in task_queue:
#         success_count += 1 if task.p_allocated == True else 0
#     gd = success_count/task_count
#     print('GD: %.2f' % (gd))
        

        


