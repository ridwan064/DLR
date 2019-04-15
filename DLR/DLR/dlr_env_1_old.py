# gym req
import gym
from gym import error, spaces, utils
from gym.utils import seeding

# env req
import numpy as np
import os
from datetime import datetime
from subprocess import Popen, PIPE
from selenium import webdriver
from bs4 import BeautifulSoup
import glob
import time
import re

############  PARAMS HELPER  ############

VMSTAT_NODE_NAMES = ['node1', 'node2', 'node4',
                     'node5', 'node6', 'node7', 'node8', 'node9']
SYSBENCH_NODE_NAMES = ['node1', 'node2', 'node4',
                       'node5']
ALL_NODE_NAMES = ['cosbench', 'admin'] + VMSTAT_NODE_NAMES
NUM_NODES = len(VMSTAT_NODE_NAMES)  # cluster size excluding master node
VMSTAT_LOGS_DIR = '/home/ceph-user/vmstat_logs'
COSBENCH_LOGS_DIR = '/home/ceph-user/cos/archive'
PHANTOMJS_PATH = '/usr/local/share/phantomjs-2.1.1-linux-x86_64/bin/phantomjs'
COSBENCH_WEBGUI_URL_BASE = 'http://129.114.33.85:19088/controller/workload.html?id='
TOTAL_MEM = 4048288
NUM_STATS = 3  # number of system stats to consider
WAIT = 20  # in secondss


############  INTERACT  HELPER ############

class ClusterEnvironment:
    def __init__(self):
        """all the class variables that might be required in the cluster
        declared here"""
        self.num_stats = NUM_STATS + 1  # one extra for using affinity
        self.total_mem = TOTAL_MEM
        self.vmstat_node_names = VMSTAT_NODE_NAMES
        self.node_num = NUM_NODES
        self.sysbench_node_names = SYSBENCH_NODE_NAMES
        self.all_nodes = ALL_NODE_NAMES
        self.vmstat_log_dir = VMSTAT_LOGS_DIR
        self.cosbench_log_folder = COSBENCH_LOGS_DIR
        self.phantomjs_path = PHANTOMJS_PATH
        self.cosbench_url = COSBENCH_WEBGUI_URL_BASE

        self.step_count = 0
        self.start_cluster()

    def start_cluster(self):
        """THIS IS THE ENTRY POINT FOR ALL BENCHMARKS RUN: all setup processes
        for cluster done here
        :return: True when ready for agent to start working"""

        timestamp = '-'.join(datetime.today().__str__().split())[:-7]
        extnsn = 'cos_h'
        new_fileName = '{}.{}'.format(timestamp, extnsn)

        # VMSTAT
        vmstat_node_names = ",".join(self.vmstat_node_names)
        vmstat_cmd = "pdsh -w {} 'vmstat 20 13' > /home/ceph-user/vmstat_logs/{} &".format(
            vmstat_node_names, new_fileName)

        print('Running vmstat with cmd: {}'.format(vmstat_cmd))
        p1 = Popen(vmstat_cmd, shell=True)
        print('Sleeping for 40s...')
        time.sleep(40)

        # COSBENCH
        cosbench_cmd = "pdsh -w cosbench 'cd /home/ceph-user/cos; sh cli.sh submit conf/workload2.xml' &"
        print('Running cosbench with cmd: {}'.format(cosbench_cmd))
        p2 = Popen(cosbench_cmd, shell=True)

        time.sleep(1)
        # SYSBENCH
        sysbench_node_names = ",".join(self.sysbench_node_names)
        sysbench_cmd = "pdsh -w {} 'sysbench --test=memory --memory-total-size=800G --num-threads=256 --memory-oper=write run' &".format(
            sysbench_node_names)

        print('Running sysbench with cmd: {}'.format(sysbench_cmd))
        p3 = Popen(sysbench_cmd, shell=True)
        return True

    def stop_cluster(self):
        """stop every task related processes on cluster, bring them to default state
        :return: True when done"""

        # SYSBENCH
        kill_sysbench_cmd = "pdsh -w {} 'pkill -9 sysbench'".format(
            ','.join(self.sysbench_node_names))
        print('Killing sysbench with cmd: {}'.format(kill_sysbench_cmd))
        p1 = Popen(kill_sysbench_cmd, shell=True)

        # VMSTAT
        kill_vmstat_cmd = "pdsh -w {} 'pkill -9 vmstat'".format(
            ','.join(self.vmstat_node_names))
        print('Killing vmstat with cmd: {}'.format(kill_vmstat_cmd))
        p2 = Popen(kill_vmstat_cmd, shell=True)

        # COSBENCH

        # get running job id
        cosbench_info_command = "pdsh -w cosbench 'sh /home/ceph-user/cos/cli.sh info'"
        p3 = Popen(cosbench_info_command, stdout=PIPE, shell=True)
        text = p3.stdout.read().strip()
        job_id = text.splitlines()[5].strip().split(":")[
            1].strip().split()[0].strip()

        if job_id != "Total":
            cosbench_kill_cmd = "pdsh -w cosbench 'sh /home/ceph-user/cos/cli.sh cancel {}'".format(
                job_id)
            print('Killing Cosbench Job: {}'.format(job_id))
            print('Killing Cosbench with cmd: {}'.format(cosbench_kill_cmd))
            Popen(cosbench_kill_cmd, shell=True)
            print('Killed Cosbench Job: {}'.format(job_id))
        else:
            print("All set no cosbench Job is running..")

        # Sleep ?
        print('Sleep for 30s..')
        time.sleep(30)
        clear_cache_cmd = "pdsh -w {} 'sync && echo 3 | sudo tee /proc/sys/vm/drop_caches'".format(
            ','.join(self.all_nodes))

        print('Clearing cache with cmd: {}'.format(clear_cache_cmd))
        p4 = Popen(clear_cache_cmd, shell=True)
        print('Stopped Cluster...')
        return True

    def get_affinities(self):
        """get affinities of the cluster at any given time
        :return: a numpy 1D vector of shape (num_nodes, 1) containing
        affinities of the given cluster"""
        command = ['ceph', 'osd', 'tree']
        p = Popen(command, stdout=PIPE)
        text = p.stdout.read()
        retcode = p.wait()

        affinity_list = []
        node_list = [n[-1] for n in self.vmstat_node_names]
        # print (type(node_list))
        d = dict.fromkeys(node_list, 0)
        # print (type(OrderedDict(d)))
        n = 20
        i = 0
        # print (self.node_num)
        while n < (20 + self.node_num * 10) and i < self.node_num:
            affinity_list.insert(i, text.split()[n])
            n = n + 10
            i = i + 1
        affinity_array = np.array(affinity_list)
        # print (affinity_array)
        return affinity_array

    def get_vmstat_all_nodes(self):
        """to get vmstat scores as well as affinity of self.step_count timestep
        :return: a numpy ndarray with shape (num_nodes, num_stats) where the
        0th column is affinities"""
        self.step_count += 20
        affinity_array = self.get_affinities()
        # VMSTATs Latest

        # get latest vmstat log file
        list_of_files = glob.glob(self.vmstat_log_dir + '/*')
        latest_file = max(list_of_files, key=os.path.getctime)

        # memory usage
        raw_data = Popen(['tail', '-n', '8', latest_file],
                         shell=False, stdout=PIPE)
        data = raw_data.stdout.read().strip()

        exp = r'(node[1-9]):( )+([0-9]+?)( )+([0-9]+?)( )+([0-9]+?)( )+([0-9]+?)( )+([0-9]+?)( )+([0-9]+?)( )+([0-9]+?)( )+([0-9]+?)( )+([0-9]+?)( )+([0-9]+?)( )+([0-9]+?)( )+([0-9]+?)( )+([0-9]+?)( )+([0-9]+?)( )+([0-9]+?)( )+([0-9]+?)( )+([0-9]+?)'
        finds = re.findall(exp, data)

        new_data = []
        for f in finds:
            dat = []
            number = 0
            for d in f:
                if d.startswith('node'):
                    number = d[-1]
                elif d != ' ':
                    dat.append(d)

            new_data.append((number, dat))
        # sorting
        new_data = sorted(new_data, key=lambda t: t[0])
        total_mem = self.total_mem
        # total_mem = 4048288
        mem_usage_list = []
        cpu_usage_list = []
        io_wait_list = []

        for k, v in new_data:
            mem = float(v[3])
            cpu1 = float(v[12])
            cpu2 = float(v[13])
            io = float(v[15])

            mem_usage_list.append(1.0 - mem / total_mem)
            cpu_usage_list.append((cpu1 + cpu2) / 100)
            io_wait_list.append(io / 100)

        mem_usage_array = np.array(mem_usage_list)
        cpu_usage_array = np.array(cpu_usage_list)
        io_wait_array = np.array(io_wait_list)

        obs = np.array([affinity_array, mem_usage_array,
                        cpu_usage_array, io_wait_array]).T
        # print (obs)
        return obs

    def get_cosbench(self):
        """returns the cosbench scores of self.step_count timestep which will
        be used to calculate the reward
        :return: Response Time
        """
        # get latest job_id

        cmd = "pdsh -w cosbench 'cd {}; echo $(ls -dt w*/ | head -1)'".format(
            self.cosbench_log_folder)  # cosbench: w802-workmix2/
        # print (cmd)
        var = Popen(cmd, shell=True, stdout=PIPE).stdout.read(
        ).strip().split()[1]  # w802-workmix2/
        # regular expression can be used
        job_id = var[var.index('w'):var.index('-')]  # w802

        cosbench_url = self.cosbench_url
        url = cosbench_url + job_id

        # get RTs from web UI
        driver = webdriver.PhantomJS(executable_path=self.phantomjs_path)
        driver.get(url)
        html = driver.page_source

        soup = BeautifulSoup(html, 'html.parser')

        tag_list = (soup.find_all('td'))
        numbers = [d.text.encode('utf-8') for d in tag_list]

        # read_response time
        rd_rt = numbers[11].strip().split()[0]  # unit is in ms

        # bandwidth unit is in MB/s
        if numbers[14].strip().split()[1] == 'KB/S':
            rd_bw = (float(numbers[14].strip().split()[0]) / 1000.0)
        else:
            rd_bw = numbers[14].strip().split()[0]

        wr_rt = numbers[19].strip().split()[0]

        if numbers[22].strip().split()[1] == 'KB/S':
            wr_bw = (float(numbers[22].strip().split()[0]) / 1000.0)
        else:
            wr_bw = numbers[22].strip().split()[0]

        cos_data = np.array([rd_rt, rd_bw, wr_rt, wr_bw])
        # print (cos_data)
        TOTAL_RT = sum([float(rd_rt), float(rd_bw),
                        float(wr_rt), float(wr_bw)])
        # print (TOTAL_RT)
        return TOTAL_RT

    def check_all_nodes_running(self):
        """to check the status of nodes at any given time,
        :return: True(all runningwith desired processes runnning) or False"""

        command = ['ceph', 'osd', 'tree']
        p = Popen(command, stdout=PIPE)
        text = p.stdout.read()
        retcode = p.wait()

        status_list = []
        node_list = [n[-1] for n in self.vmstat_node_names]
        d = dict.fromkeys(node_list, 0)
        n = 18
        i = 0

        while n < (20 + self.node_num * 10) and i < self.node_num:
            status_list.insert(i, text.split()[n])
            n = n + 10
            i = i + 1

        j = 0
        flag = 0
        while j < len(status_list):
            if status_list[j] == 'down':
                flag = flag + 1
            j = j + 1

        if flag == 1:
            # print ("cluster down")
            return False
        # print ("cluster working")
        return True

    def act(self, new_affinities):
        """change the affinities of nodes in the cluster to received input

        :param new_affinities: numpy array with new affinities,
                               a 1D array of shape(num_nodes, 1)
        :return: True(when done)
        """
        assert new_affinities.shape[0] == self.node_num
        for i in range(0, self.node_num):
            p = Popen('ceph osd primary-affinity %d %f' %
                      (i, float(new_affinities[i])), shell=True)
            retcode = p.wait()
        return True


############  MAIN ENV  ############

class DlrEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self):
        # will start the required processes in the cluster
        self.env = ClusterEnvironment()

        # actions here will be weights which when multiplied with previous affinity_col gives new affinity_col
        # (n_nodes, 1)
        self.action_space = spaces.Box(low=0,
                                       high=1,
                                       shape=(NUM_NODES, 1))

        # (n_nodes, n_params)
        self.observation_space = spaces.Box(low=0,
                                            high=1,
                                            shape=(NUM_NODES, NUM_STATS + 1))  # +1 for affinity as a stat

        self.status = self.env.check_all_nodes_running()

    def _step(self, action):
        """Change affinities, set them in cluster, wait for observation 21s, return (ob, reward, episode_over, empyt_dict)"""
        # take action
        new_aff = self._change_affinities(action)
        assert np.all(self.env.get_affinities().reshape(-1, 1) ==
                      new_aff.reshape(-1, 1)), "Affinities not set or get correctly by interact.py"
        # wait
        time.sleep(21)
        # check the status and observe the status of nodes
        self.status = self.env.check_all_nodes_running()
        assert self.status, "interact.py says node status is not Good. Check it."

        ob = self.env.get_vmstat_all_nodes()
        # simultatneously get the performance metrics
        RT = self.env.get_cosbench()

        reward = 1. / RT
        done = self.env.step_count == 180  # when step_count == 180 done
        return ob, reward, done, {'RT': RT}

    def _change_affinities(self, action):
        """Change use action space to get new affinities, change the affinities of cluster"""
        # W(n, n) x OldAffinities(n, 1)
        # TODO: Check this theory else discrete low medium high very high
        new_aff = np.dot(action,
                         self.env.get_affinities())  # new_aff = action dot old affinities
        self.env.act(new_aff)
        return new_aff

    def _reset(self):
        self.env = ClusterEnvironment()
        obs = self.env.get_vmstat_all_nodes()
        return obs

    def _render(self, mode='human', close=False):
        pass


if __name__ == '__main__':
    # ce = ClusterEnvironment()
    # print(ce.get_affinities())
    # print (ce.get_vmstat_all_nodes())
    # print(ce.check_all_nodes_running())
    # affinity_array = np.array([0.9, 0.8, 0.7, 0.6 , 1.0, 1.0, 1.0, 1.0])
    # print(ce.act(affinity_array))
    # print(ce.get_cosbench())
    # ce.start_cluster()
    # ce.stop_cluster()
    pass
