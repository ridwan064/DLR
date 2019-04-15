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
        # self.driver = webdriver.PhantomJS(executable_path=self.phantomjs_path)
        self.step_count = 0
        # self.stop_cluster()
        #self.start_cluster()

    def start_cluster(self):
        """THIS IS THE ENTRY POINT FOR ALL BENCHMARKS RUN: all setup processes
        for cluster done here
        :return: True when ready for agent to start working"""
        print("Starting cluster")
        timestamp = '-'.join(datetime.today().__str__().split())[:-7]
        extnsn = 'cos_h'
        new_fileName = '{}.{}'.format(timestamp, extnsn)

        # VMSTAT
        vmstat_node_names = ",".join(self.vmstat_node_names)
        vmstat_cmd = "pdsh -w {} 'vmstat 20 20' > /home/ceph-user/vmstat_logs/{} &".format(
            vmstat_node_names, new_fileName)

        print('Running vmstat with cmd: {}'.format(vmstat_cmd))
        p1 = Popen(vmstat_cmd, shell=True)
        p1.communicate()
        p1.wait()
        print('Sleeping for 40s..Else no obs data..ERROR in agent: SHAPE')
        time.sleep(40)

        # COSBENCH
        cosbench_cmd = "pdsh -w cosbench 'cd /home/ceph-user/cos; sh cli.sh submit conf/workload2.xml' &"
        print('Running cosbench with cmd: {}'.format(cosbench_cmd))
        p2 = Popen(cosbench_cmd, shell=True)
        p2.communicate()
        p2.wait()

        time.sleep(3)
        # TODO: SYSBENCH vary random unifrom: mem, io, cpu
        sysbench_node_names = ",".join(self.sysbench_node_names)
        sysbench_cmd = "pdsh -w {} 'sysbench --test=memory --memory-total-size=1000G --num-threads=1 --memory-oper=write run' &".format(
            sysbench_node_names)

        print('Running sysbench with cmd: {}'.format(sysbench_cmd))
        p3 = Popen(sysbench_cmd, shell=True)
        p3.communicate()
        p3.wait()
        return True

    def stop_cluster(self):
        """stop every task related processes on cluster, bring them to default state
        :return: True when done"""

        # SYSBENCH
        kill_sysbench_cmd = "pdsh -w {} 'pkill -9 sysbench'".format(
            ','.join(self.sysbench_node_names))
        print('Killing sysbench with cmd: {}'.format(kill_sysbench_cmd))
        p1 = Popen(kill_sysbench_cmd, shell=True)
        p1.communicate()
        p1.wait()

        # VMSTAT
        kill_vmstat_cmd = "pdsh -w {} 'pkill -9 vmstat'".format(
            ','.join(self.vmstat_node_names))
        print('Killing vmstat with cmd: {}'.format(kill_vmstat_cmd))
        p2 = Popen(kill_vmstat_cmd, shell=True)
        p2.communicate()
        p2.wait()

        # COSBENCH

        # get running job id
        cosbench_info_command = "pdsh -w cosbench 'sh /home/ceph-user/cos/cli.sh info'"
        p3 = Popen(cosbench_info_command, stdout=PIPE, shell=True)
        text = p3.stdout.read().strip()
        text = str(text).strip()
        p3.communicate()
        p3.wait()
        # print (text)
        # job_id = text.splitlines()[5].strip().split(":")[1].strip().split()[0].strip()
        wexp = r': (w[0-9]+)'
        finds = re.findall(wexp, text)
        found_job = len(finds) != 0
        if found_job:
            print("jobs found ", len(finds))
            for job_id in finds:
                cosbench_kill_cmd = "pdsh -w cosbench 'sh /home/ceph-user/cos/cli.sh cancel {}'".format(
                    job_id)
                print('Killing Cosbench Job: {}'.format(job_id))
                print('Killing Cosbench with cmd: {}'.format(cosbench_kill_cmd))
                p4 = Popen(cosbench_kill_cmd, shell=True)
                p4.communicate()
                p4.wait()
                print('Killed Cosbench Job: {}'.format(job_id))
        else:
            print("All set no cosbench Job is running..")

        # Sleep ?
        print('Sleep for 30s..')
        time.sleep(30)
        clear_cache_cmd = "pdsh -w {} 'sync && echo 3 | sudo tee /proc/sys/vm/drop_caches'".format(
            ','.join(self.all_nodes))

        print('Clearing cache with cmd: {}'.format(clear_cache_cmd))
        p5 = Popen(clear_cache_cmd, shell=True)
        p5.communicate()
        p5.wait()

        print('Killing Zombie PhantomjS Process...')

        kill_pjs = "kill -9 `ps -ef | grep phantomjs  | grep -v grep | awk '{print $2}'`"
        p6 = Popen(kill_pjs, stdout=PIPE, shell=True)
        p6.communicate()
        p6.wait()

        # self.driver.quit()
        print('Stopped Cluster...')
        return True

    def get_affinities(self):
        """get affinities of the cluster at any given time
        :return: a numpy 1D vector of shape (num_nodes, 1) containing
        affinities of the given cluster"""
        command = ['ceph', 'osd', 'tree']
        p = Popen(command, stdout=PIPE)
        text = p.stdout.read()
        p.communicate()
        p.wait()
        affinity_list = []
        # node_list = [n[-1] for n in self.vmstat_node_names]
        # print (type(node_list))
        # d = dict.fromkeys(node_list, 0)
        # print (type(OrderedDict(d)))
        n = 20
        i = 0
        # print (self.node_num)
        while n < (20 + self.node_num * 10) and i < self.node_num:
            affinity_list.insert(i, text.split()[n])
            n = n + 10
            i = i + 1
        affinity_array = np.array(affinity_list, dtype=np.float32)
        # print (affinity_array)
        return affinity_array

    def get_vmstat_all_nodes(self):
        """to get vmstat scores as well as affinity of self.step_count timestep
        :return: a numpy ndarray with shape (num_nodes, num_stats) where the
        0th column is affinities"""
        # self.step_count += 20
        affinity_array = self.get_affinities()
        # VMSTATs Latest

        # get latest vmstat log file
        list_of_files = glob.glob(self.vmstat_log_dir + '/*')
        latest_file = max(list_of_files, key=os.path.getctime)

        # memory usage
        print('v' * 60)
        print("VMSTAT LOG FILE: {}".format(latest_file))
        print('v' * 60)
        raw_data = Popen(['tail', '-n', '8', latest_file],
                         shell=False, stdout=PIPE)
        data = raw_data.stdout.read().strip()
        raw_data.communicate()
        raw_data.wait()
        data = str(data)
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

    def parse_html_for_cosbench(self, url):
        # get RTs from web UI
        driver = webdriver.PhantomJS(executable_path=self.phantomjs_path)
        driver.get(url)
        html = driver.page_source

        soup = BeautifulSoup(html, 'html.parser')
        try:
            table = soup.find('table', attrs={'class': 'info-table'})

            rows = []
            # read index = 0, write index = 1
            for row in table.find_all("tr")[1:]:
                datapoints = [td.get_text().strip()
                              for td in row.find_all("td")]
                rows.append(datapoints)

        except AttributeError as e:
            print(e)
            print('Retrying Parsing...')
            time.sleep(3)
            rows = self.parse_html_for_cosbench(url)

        print('Number of rows found, 3 total for 2nd stage: {}/3'.format(len(rows)))
        print('Cosbench Data: ', rows)

        return rows

    def check_get_rows_and_get_obs(self, rows, job_id, url, fetch=False):
        rt_index = 3
        bw_index = 6
        rd_rt, rd_bw, wr_rt, wr_bw = None, None, None, None
        try:
            retries = 1
            # if not in read_write_del stage while
            while len(rows) != 3 and retries < 999999:
                retries += 1
                print('NO COSBENCH DATA FOUND FOR: {} retrying {} ..'.format(job_id,
                                                                             retries))
                rows = self.parse_html_for_cosbench(url)
                time.sleep(1)
            else:  # if in read_write_del stage
                if retries < 999999:
                    print('COSBENCH DATA FOUND FOR: {} after {} attempts..'.format(job_id,
                                                                                   retries))
                    if fetch:  # only when there was ValueError
                        print('FETCHED AGAIN: {} time'.format(retries))
                        rows = self.parse_html_for_cosbench(url)
                    print(rows)

            # read data:
            read_row = rows[0]
            rd_rt = float(read_row[rt_index].strip().split()[0].strip())
            rd_bw = read_row[bw_index]

            if rd_bw.strip().split()[1] == 'KB/S':
                rd_bw = float(rd_bw.strip().split()[0]) / 1000.0
            else:
                rd_bw = float(rd_bw.strip().split()[0])

            # write data:
            write_row = rows[1]
            wr_rt = float(write_row[rt_index].strip().split()[0].strip())
            wr_bw = write_row[bw_index]
            if wr_bw.strip().split()[1] == 'KB/S':
                wr_bw = float(wr_bw.strip().split()[0]) / 1000.0
            else:
                wr_bw = float(wr_bw.strip().split()[0])

        except ValueError as e:
            print(e)
            print('Retrying Parsing...')
            rd_rt, rd_bw, wr_rt, wr_bw = self.check_get_rows_and_get_obs(rows,
                                                                         job_id,
                                                                         url,
                                                                         fetch=True)
        except TypeError as e:
            print(e)
            print('Retrying Parsing...')
            rd_rt, rd_bw, wr_rt, wr_bw = self.check_get_rows_and_get_obs(rows,
                                                                         job_id,
                                                                         url,
                                                                         fetch=True)
        except AttributeError as e:
            print(e)
            print('Retrying Parsing...')
            time.sleep(3)
            rd_rt, rd_bw, wr_rt, wr_bw = self.check_get_rows_and_get_obs(rows,
                                                                         job_id,
                                                                         url,
                                                                         fetch=True)

        finally:
            return rd_rt, rd_bw, wr_rt, wr_bw

    def get_cosbench(self):
        """returns the cosbench scores of self.step_count timestep which will
        be used to calculate the reward
        :return: Response Time
        """
        # get latest job_id

        cmd = "pdsh -w cosbench 'cd {}; echo $(ls -dt w*/ | head -1)'".format(
            self.cosbench_log_folder)  # cosbench: w802-workmix2/
        # print (cmd)
        # w802-workmix2/
        p = Popen(cmd, shell=True, stdout=PIPE)
        var = p.stdout.read().strip()
        p.communicate()
        p.wait()
        # regular expression can be used
        #print(var)
        var = str(var).strip().split()[1]
        #print(var)
        job_id = var[var.index('w') + 1:var.index('-')]  # w802
        job_id = int(job_id) + 1
        job_id = 'w' + str(job_id)
        #print(job_id)
        cosbench_url = self.cosbench_url
        url = cosbench_url + job_id
        #print(url)

        rows = self.parse_html_for_cosbench(url)
        # get floats
        rd_rt, rd_bw, wr_rt, wr_bw = self.check_get_rows_and_get_obs(rows,
                                                                     job_id,
                                                                     url)

        TOTAL_RT = sum([rd_rt / 1000,
                        wr_rt / 1000])  # unit in seconds
        return TOTAL_RT

    def check_all_nodes_running(self):
        """to check the status of nodes at any given time,
        :return: True(all runningwith desired processes runnning) or False"""

        command = ['ceph', 'osd', 'tree']
        p = Popen(command, stdout=PIPE)
        text = p.stdout.read()
        p.communicate()
        p.wait()

        status_list = []
        # node_list = [n[-1] for n in self.vmstat_node_names]
        # d = dict.fromkeys(node_list, 0)
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
            p.communicate()
            p.wait()
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
        new_aff = self._change_affinities(action).flatten()
        # got_aff = self.env.get_affinities().flatten()
        # print (got_aff, new_aff)
        # assert np.all(new_aff == got_aff), "Affinities not set or get correctly by interact.py"
        # print (got_aff, new_aff)
        # wait
        print('@' * 60)
        print('Sleeping for 21s..inside step..before collecting stats')
        time.sleep(21)
        print('@' * 60)
        # check the status and observe the status of nodes
        self.status = self.env.check_all_nodes_running()
        assert self.status, "interact.py says node status is not Good. Check it."

        ob = self.env.get_vmstat_all_nodes()
        # simultatneously get the performance metrics
        try:
            RT = self.env.get_cosbench()
        except IndexError as e:
            print('-' * 60)
            print("Error: IndexError Sleep for 3s for prepare..")
            time.sleep(3)
            print('-' * 60)
            RT = self.env.get_cosbench()
        except TypeError as e:
            print('-' * 60)
            print("Error: TypeError Sleep for 3s for prepare..")
            time.sleep(3)
            print('-' * 60)
            RT = self.env.get_cosbench()
        except Exception as e:
            print('Error: ', e)
            print('-' * 60)
            print("Sleep for 3s for prepare..")
            time.sleep(3)
            print('-' * 60)
            RT = self.env.get_cosbench()

        reward = 1. / RT
        done = self.env.step_count == 180  # when step_count == 180 done
        return ob, reward, done, {'RT': RT}

    def _change_affinities(self, action):
        """Change use action space to get new affinities, change the affinities of cluster"""
        # W(n, n) x OldAffinities(n, 1)
        # TODO: Check this theory else discrete low medium high very high
        # new_aff = np.dot(action,
        #                 self.env.get_affinities())  # new_aff = action dot old affinities
        new_aff = action.reshape(-1)
        self.env.act(new_aff)
        self.env.step_count += 20

        return new_aff

    def _reset(self):
        print('@' * 60)
        print('Stopping Cluster..Inside reset..')
        print('@' * 60)
        self.env.stop_cluster()
        print('@' * 60)
        print('Sleeping for 15s..inside reset..after stop cluster')
        time.sleep(15)
        print('@' * 60)
        print('Will start cluster inside reset..')
        self.env = ClusterEnvironment()

        print('Reset aff. to 1. and collect obs....')
        self.env.act(np.ones(shape=(8,)))
        obs = self.env.get_vmstat_all_nodes()

        while len(obs.shape) != 2:
            time.sleep(1)
            print('ERROR: Collecting vmstat again because observation shape: ', obs.shape)
            obs = self.env.get_vmstat_all_nodes()
        return obs

    def _render(self, mode='human', close=False):
        pass


if __name__ == '__main__':
    ce = ClusterEnvironment()
    # print(ce.get_affinities())
    # print (ce.get_vmstat_all_nodes())
    # print(ce.check_all_nodes_running())
    # affinity_array = np.array([0.9, 0.8, 0.7, 0.6 , 1.0, 1.0, 1.0, 1.0])
    # print(ce.act(affinity_array))
    ce.get_cosbench()
    # ce.start_cluster()
    # ce.stop_cluster()
    pass
