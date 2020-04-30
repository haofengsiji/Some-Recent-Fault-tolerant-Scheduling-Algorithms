# This is readme file about how to run PS and BS algorithms.

## Preparation

  Numpy package is needed:
    $:pip install numpy

## PS

  Run:
    $: python Primaries Scheduling in FESTAL.py

  Main parameters:

    task_count:
	Line 166, int, contorl the number of task.
    
  Main methods:
    
    generateTask(num_Task):
	Generate tasks by following the rules in report.
	input:
	  num_Task,int,the number of tasks
	return:
	  queue,list,a list contains Task class
    
    Datacenter.schedulePTask(self,task):
	Schedule primary task by using PS algorithm.
	input:
	  task,class,Task class
	return:None
	
    Datacenter.scaleUp(self,task):
	Create new VM elastically stasifying the rules in paper.
	input:
	  task,class,Task class
	return:
	  v,class,Vm class
	
    Datacenter.calculateEFT(self,v,task,delay):
	Calculate earliest finish time and corresponding start time on the giving Vm.
	input:
	  v,class,Vm class
	  task,class,Task clas
	  delay,int,the time needed to create a new VM
	return:
	  EFT,int,earliest finish time
	  s_time,int, corresponding start time
	
### How to add ANAP part

  Change line 70~76:
            # ## ANAP part
            # if len(h_k.vm_ls) == 0:
            #     v = self.scaleUp(task)
            #     if v != None:
            #         find = True
            #         delay = 15
            #         break
  To:
            ## ANAP part
            if len(h_k.vm_ls) == 0:
                v = self.scaleUp(task)
                if v != None:
                    find = True
                    delay = 15
                    break

## BS


  Run:
    $: python Backups Scheduling in FESTAL.py

  Main parameters:

    task_count:
	Line 319, int, contorl the number of task.

  Main methods:
    
    generateTask(num_Task):
	Generate tasks by following the rules in report.
	input:
	  num_Task,int,the number of tasks
	return:
	  queue,list,a list contains Task class
    
    Datacenter.scheduleBTask(self,task):
	Schedule backup task by using PS algorithm.
	input:
	  task,class,Task class
	return:None
	
    Datacenter.BscaleUp(self,task):
	Create new VM elastically stasifying the rules in paper.
	input:
	  task,class,Task class
	return:
	  v,class,Vm class
	
    Datacenter.calculateLST(self,v,task,delay):
	Calculate lastest start time and corresponding finish time on the giving Vm.
	input:
	  v,class,Vm class
	  task,class,Task clas
	  delay,int,the time needed to create a new VM
	return:
	  LST,int,lastest start time
	  f_time,int, corresponding finish time

### How to change as active mode(default: passive mode)

  Change:
    line 116~119:
	# passive mode
       	if (f_time <= task.deadline) & (LST_kl >= task.p_finish_time):
	# # active mode
       	# if (f_time <= task.deadline) & (LST_kl >= task.arrive_time):
    line 316~376:
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
	#             print('|Host: %02d |VM: %02d |P-task_id: %04d |start_time: %5d | 	finish_time: %5d | SUCCESS |'\
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

  To:
    line 116~119:
	# # passive mode
       	# if (f_time <= task.deadline) & (LST_kl >= task.p_finish_time):
	# active mode
       	if (f_time <= task.deadline) & (LST_kl >= task.arrive_time):
    line 316~376:
	# # Dynamic Simulation Backup mode: Passive
	# if __name__ == "__main__":
	#     # Step 1: generate tasks queue
	#     task_count = 5000
	#     task_queue = generateTask(task_count)
	#     # Step 2: initialize datacenter
	#     D = Datacenter([2000,2000,3000,3000],[250,500,1000])
	#     task_onboard = []
	#     print('========Time:0 s ========')
	#     for task in task_queue:
	#         # Step 3: Processing the task allocated
	#         TIME = task.arrive_time
	#         processTask(task_onboard,TIME)
	#         # Step 4: Primary schedule
	#         D.schedulePTask(task)
	#         if task.p_allocated == True:
	#             # Step 4: Backup schedule
	#             D.scheduleBTask(task)
	#         if task.b_allocated == True:
	#             task_onboard.append(task)
	#         print('========Time:%d s ========'%(TIME))
	#     processTask(task_onboard,float('inf'))
	#     print('========Time:inf s ========')
	#     # Step 5: Calculate guarantee ratio
	#     success_count = 0
	#     for task in task_queue:
	#         success_count += 1 if task.finish == True else 0
	#         gd = success_count/task_count
	#     print('GD: %.2f' % (gd))
	
	
	# Static Simulation Backup mode: Active
	if __name__ == "__main__":
	    # Step1: generate tasks queue
	    task_count = 10000
	    task_queue = generateTask(task_count)
	    # Step2: initialize datacenter
	    D = Datacenter([2000,2000,3000,3000],[250,500,1000])
	    # Step3: Primary schedule 
	    for task in task_queue:
	        D.schedulePTask(task)
	        if task.p_allocated == True:
	            D.scheduleBTask(task)
	    # Step4: Start Simulation
	    print('=============Simulation Start==============')
	    for task in task_queue:
	        if task.p_allocated == True:
	            print('|Host: %02d |VM: %02d |P-task_id: %04d |start_time: %5d | 	finish_time: %5d | SUCCESS |'\
	                % (task.p_cur_h.h_id,task.p_cur_v.v_id,task.task_id,task.p_start_time,task.p_finish_time))
	            print('|Host: %02d |VM: %02d |B-task_id: %04d |start_time: %5d | finish_time: %5d | SUCCESS |'\
	                % (task.b_cur_h.h_id,task.b_cur_v.v_id,task.task_id,task.b_start_time,task.b_finish_time))
	        else:
	            print('|Host: -- |VM: -- |X-task_id: %04d |start_time: ----- | finish_time: ----- | FAILURE |'\
	                % (task.task_id))
	    print('=============Simulation END==============')
	    # Step5: Calculate guarantee ratio
	    success_count = 0
	    for task in task_queue:
	        success_count += 1 if task.p_allocated == True else 0
	    gd = success_count/task_count
	    print('GD: %.2f' % (gd))