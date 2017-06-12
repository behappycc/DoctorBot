#!/usr/bin/env python
import tensorflow as tf
import sys
import random
import numpy as np
import re
#############################


from collections import deque
sys.path.append('../user_simulator')
from CompleteUser import *
sys.path.append('../LU_model')
import db
sys.path.append('../data_resource')
import CrawlerTimeTable
sys.path.append('../joint_model')
import get_lu_pred
lu_model = get_lu_pred.LuModel()

DB_IP = "localhost"  # doctorbot GCP ip
DB_PORT = 27017  # default MongoDB port
DB_NAME = "doctorbot"  # use the collection

############ SETTINGS #############

GAME = 'ICB' # the name of the game being played for log files
GAMMA = 0.99 # decay rate of past observations
N_SAVE_PROGRESS = 1000 # save progress every 1000 iteration
OBSERVE = 100 # 100000. # timesteps to observe before training
EXPLORE = 2000000. # frames over which to anneal epsilon
FINAL_EPSILON = 0.0001 # final value of epsilon
INITIAL_EPSILON = 0.5 #0.0001 # starting value of epsilon
REPLAY_MEMORY = 50000 # number of previous transitions to remember
BATCH = 32 # size of minibatch
ACTIONS = 12 # number of valid actions
STATES = 15 # number of states
n_hidden_1 = 256  # 1st layer number of features
n_hidden_2 = 256  # 2nd layer number of features
n_input = STATES  # MNIST data input (img shape: 28*28)
n_classes = ACTIONS # MNIST total classes (0-9 digits)
NDEBUG = False# if False print dialogue detail

def get_dbinfo(slot1,slot2, choose):
    client = db.MongoClient(DB_IP, DB_PORT)

    collection_division = client[DB_NAME]["division"]
    collection_disease = client[DB_NAME]["disease"]
    slot1 = slot1[0]
    #use disease to find division
    if slot2 == "department":
        for data in collection_disease.find({"disease_c": {"$regex": slot1}}):
            return  data['department']
    #use disease to find doctors
    elif slot2 == "doctor" and choose == 0:
        for data in collection_division.find({"$and": [{"disease": {"$regex": slot1}},
                                                       {"department": {"$regex": ""}}]}):
            return data['doctor']
    #use division to find doctors
    elif slot2 == "doctor" and choose == 1:
        for data in collection_division.find({"$and": [{"disease": {"$regex": ''}},
                                                       {"department": {"$regex": slot1}}]}):
            return data['doctor']

def end(DM):
    DM['request'] = 'end'
def inform(slot, DM):
    DM['request'] = 'inform'
    DM['slot'] = [slot]

def select(slot, DM):
    DM['request'] = 'choose'
    if slot == "division":
        DM['slot'] = ["division"]
        if DM["state"]["disease"] != []:
            DM["state"]["division"] = get_dbinfo(DM["state"]["disease"],"department",0)
        else:
           inform("disease",DM)
    elif slot == "doctor":
        DM['slot'] = ["doctor"]
        if DM["state"]["division"] != []:
            DM["state"]["doctor"] = get_dbinfo(DM["state"]["division"],"doctor",1)
        elif DM["state"]["disease"] != []:
            DM["state"]["doctor"] = get_dbinfo(DM["state"]["disease"],"doctor",0)
        else:
            inform("division",DM)
    elif slot == "time":
        DM["slot"] = ["time"]
        if DM["state"]["doctor"] != []:
            DM["state"]["time"] = CrawlerTimeTable.Timetable(str(DM["state"]["doctor"])).get_time()
        else:
           inform("doctor", DM)


def confirm(slot, DM):
    DM['request'] = 'confirm'
    DM['slot'] = [slot]
#  state = [] #5intent 5state 5confirm

action_dict = {0:end,
        1:lambda s:inform("disease",s),     # inform
        2:lambda s:inform("division",s),
        3:lambda s:inform("doctor",s),
        4:lambda s:inform('time',s),
        5:lambda s:select("division",s),    # choose
        6:lambda s:select("doctor",s),
        7:lambda s:select("time",s),
        8:lambda s:confirm("disease",s),    # confirm
        9:lambda s:confirm("division",s),
        10:lambda s:confirm("doctor",s),
        11:lambda s:confirm("time",s)
        }
example_answer = [[],[1,0],[1,0],[1,5,0],[3,0],[3,4,0]]
slot_dict = {
    "intent":1,
    "disease":2,
    "division":3,
    "doctor":4,
    "time":5
}


def state_initial():
    return np.zeros(STATES)

def state_verbose_initial():
    return {"intent":[], "disease":[], "division":[], "doctor":[], "time":[]}

def state_update(observation, semantic_frame, old_state=None, old_state_verbose = None):
    ##  arguments:
    ##      observation is user's response
    ##      semantic_frame is a slot-detecting and intent-detecting function
    ##      old_state 由三部份組成的binary list：照順序是intent(5)是哪個，state(5)有沒有，confirm(5)過了沒
    ##      old_state_verbose
    ##  return:
    ##      state: updated binary list
    ##      state_verbose: updated dictionary
    ##      LU_frame
    addRulebase = True
    LU_frame = semantic_frame(observation)

    if(old_state==None):
        state = state_initial()
        state_verbose = state_verbose_initial()
    else:
        state = old_state.copy()
        state_verbose = old_state_verbose
    if LU_frame['intent']!= '':
        if state_verbose['intent']==[]:
            if "我想要掛門診" in observation and addRulebase:
                state_verbose['intent'] = [5]
            else:
                state_verbose['intent'] = [int(LU_frame['intent'])]
            state[int(LU_frame['intent'])-1] = 1 ######must bugs here zzz
    for key,value in LU_frame['slot'].items(): #state
        if value!='':
            state_verbose[key] = [value]
            state[slot_dict[key]+4] = 1
    pattern = re.compile("[0-9]+\.[0-9]+\.[0-9]+")
    match = pattern.search(observation)
    if match:
        state_verbose["time"] = [observation[match.start():match.end()]]
    return state, state_verbose, LU_frame

def action_affect_state(action_index, state):
    if action_index >= 8 and action_index <= 11:
        state[action_index + 2] = 1

def generate_DM_frame(state_verbose, action):
    assert state_verbose != None
    DM_frame = {}
    DM_frame["state"] = state_verbose
    #  print(DM_frame)
    # the intent in state is a list, while intent in intent is an int
    if state_verbose["intent"] != []:
        DM_frame["intent"] = state_verbose["intent"][0]
    else:
        DM_frame["intent"] = None
    action(DM_frame) # deal with "request" and "slot"
    return DM_frame

def weight_variable(shape):
    initial = tf.truncated_normal(shape, stddev = 0.01)
    return tf.Variable(initial)

def bias_variable(shape):
    initial = tf.constant(0.01, shape = shape)
    return tf.Variable(initial)

def conv2d(x, W, stride):
    return tf.nn.conv2d(x, W, strides = [1, stride, stride, 1], padding = "SAME")

def max_pool_2x2(x):
    return tf.nn.max_pool(x, ksize = [1, 2, 2, 1], strides = [1, 2, 2, 1], padding = "SAME")

def createNetwork():
    s = tf.placeholder("float", [None, n_input])
    weights = {
        'h1': tf.Variable(tf.random_normal([n_input, n_hidden_1])),
        'h2': tf.Variable(tf.random_normal([n_hidden_1, n_hidden_2])),
        'out': tf.Variable(tf.random_normal([n_hidden_2, n_classes]))
    }
    biases = {
        'b1': tf.Variable(tf.random_normal([n_hidden_1])),
        'b2': tf.Variable(tf.random_normal([n_hidden_2])),
        'out': tf.Variable(tf.random_normal([n_classes]))
    }
    # network weights
    layer_1 = tf.add(tf.matmul(s, weights['h1']), biases['b1'])
    layer_1 = tf.nn.relu(layer_1)
    # Hidden layer with RELU activation
    layer_2 = tf.add(tf.matmul(layer_1, weights['h2']), biases['b2'])
    layer_2 = tf.nn.relu(layer_2)# h1_fc
    # Output layer with linear activation
    readout = tf.matmul(layer_2, weights['out']) + biases['out']
    var = [item for key,item in weights.items()] + [item for key, item in biases.items()]
    return s, readout, layer_2, var

def trainNetwork(s, readout, h_fc1, sess, var):
    # define the cost function
    # readout is the action-predicting net
    start_training = False
    a = tf.placeholder("float", [None, ACTIONS]) # placeholder for the chosen action
    y = tf.placeholder("float", [None])          # placeholder for reward
    readout_action = tf.reduce_sum(tf.multiply(readout, a), reduction_indices=1)
    cost = tf.reduce_mean(tf.square(y - readout_action))
    train_step = tf.train.AdamOptimizer(1e-6).minimize(cost, var_list=var)


    # open up a game state to communicate with emulator
    sim_user = CompleteUser()

    # store the previous observations in replay memory
    D = deque()
    n_success = 0
    n_fail = 0
    # printing
    #a_file = open("logs_" + GAME + "/readout.txt", 'w')
    #h_file = open("logs_" + GAME + "/hidden.txt", 'w')

    # get the first state by doing nothing and preprocess the image to 80x80x4
    do_nothing = None
    x_t, r_0, Terminal, Success = sim_user.step(do_nothing)
    s_t, s_t_verbose, LU_frame = state_update(x_t, lu_model.semantic_frame, old_state=None, old_state_verbose=None)

    # saving and loading networks
    saver = tf.train.Saver()
    sess.run(tf.initialize_all_variables())
    checkpoint = tf.train.get_checkpoint_state("saved_networks")
    if checkpoint and checkpoint.model_checkpoint_path:
        saver.restore(sess, checkpoint.model_checkpoint_path)
        print("Successfully loaded:", checkpoint.model_checkpoint_path)
    else:
        print("Could not find old network weights")

    # the training loop
    epsilon = INITIAL_EPSILON
    t = 0
    while "intelligent bot" != "idiotic bot":
        # choose an action epsilon greedily
        readout_t = readout.eval(feed_dict={s : [s_t]}, session= sess)[0]
        a_t = np.zeros([ACTIONS])
        action_index = 0
        #if t % FRAME_PER_ACTION == 0:
        if random.random() <= epsilon:
            print("----------Random Action----------")
            action_index = random.randrange(ACTIONS)
            a_t[random.randrange(ACTIONS)] = 1
        else:
            action_index = np.argmax(readout_t)
            a_t[action_index] = 1
        if not NDEBUG: print("\033[1;33;40mUser: ", x_t,"\033[0m")
        if not NDEBUG: print("LU: ",LU_frame)
        # some function using action_index and state_verbose to generate
        # semantic frame for the user simulator or the NLG module
        DM_frame = generate_DM_frame(s_t_verbose, action_dict[action_index])
        if not NDEBUG: print("DoctorBot: ",DM_frame)

        # scale down epsilon
        if epsilon > FINAL_EPSILON and t > OBSERVE:
            epsilon -= (INITIAL_EPSILON - FINAL_EPSILON) / EXPLORE

        # run the selected action and observe next state and reward
        x_t1, r_t, Terminal, Success = sim_user.step(DM_frame)
        s_t1, s_t_verbose, LU_frame = state_update(x_t1, lu_model.semantic_frame, s_t,s_t_verbose)
        action_affect_state(action_index, s_t1)

        # store the transition in D
        D.append((s_t, a_t, r_t, s_t1, Terminal))
        if len(D) > REPLAY_MEMORY:
            D.popleft()

        # only train if done observing
        if t > OBSERVE:
            if not start_training:
                start_training = True
                print('\033[93m' + "--- after observation, start training ---" + '\033[0m')
            # sample a minibatch to train on
            minibatch = random.sample(D, BATCH)
            # get the batch variables
            s_j_batch  = [d[0] for d in minibatch]
            a_batch    = [d[1] for d in minibatch]
            r_batch    = [d[2] for d in minibatch]
            s_j1_batch = [d[3] for d in minibatch]

            y_batch = []
            readout_j1_batch = readout.eval(feed_dict = {s : s_j1_batch}, session = sess)
            for i in range(0, len(minibatch)):
                terminal = minibatch[i][4]
                # if terminal, only equals reward
                if terminal:
                    y_batch.append(r_batch[i])
                else:
                    y_batch.append(r_batch[i] + GAMMA * np.max(readout_j1_batch[i]))

            # perform gradient step
            train_step.run(feed_dict = {
                y : y_batch,
                a : a_batch,
                s : s_j_batch},
                session = sess
            )


        # update the old values
        s_t = s_t1
        x_t = x_t1
        t += 1

        if Terminal == True:
            n_success = n_success + 1 if     Success else n_success
            n_fail    = n_fail + 1    if not Success else n_fail
            print("User: ", x_t)
            print("==============================>ENDING", r_t)
            print("n_success: ", n_success,"\nn_fail: ", n_fail)
            print("--- initializing user simulator ---")
            sim_user.initial()
            do_nothing = None
            x_t, r_0, Terminal, Success = sim_user.step(do_nothing)
            s_t,s_t_verbose, LU_frame = state_update(x_t,
                    lu_model.semantic_frame, old_state=None, old_state_verbose=None)
            #  print('\033[93m' + "User: " + '\033[0m' + x_t)

        # save progress every N_SAVE_PROGRESS iterations
        if t % N_SAVE_PROGRESS == 0:
            saver.save(sess, 'saved_networks/' + GAME + '-dqn', global_step = t)

        # print info
        state = ""
        if t <= OBSERVE:
            state = "observe"
        elif t > OBSERVE and t <= OBSERVE + EXPLORE:
            state = "explore"
        else:
            state = "train"

        print("TIMESTEP", t, "/ STATE", state, \
            "/ EPSILON", epsilon, "/ ACTION", action_index, "/ REWARD", r_t, \
            "/ Q_MAX %e" % np.max(readout_t))
        # write info to files
        '''
        if t % 10000 <= 100:
            a_file.write(",".join([str(x) for x in readout_t]) + '\n')
            h_file.write(",".join([str(x) for x in h_fc1.eval(feed_dict={s:[s_t]})[0]]) + '\n')
            cv2.imwrite("logs_tetris/frame" + str(t) + ".png", x_t1)
        '''
def UserSimDebug():
    sim_user = CompleteUser()
    for i in range(1,6):
        print("--- initializing user simulator ---")
        CompleteUser.initial(i)
        answers = example_answer[CompleteUser.user_intent]
        do_nothing = None
        x_t, r_0, Terminal, Success = sim_user.step(do_nothing)
        s_t, s_t_verbose, LU_frame = state_update(x_t, lu_model.semantic_frame, old_state=None, old_state_verbose=None)
        for a in answers:
            a_t = np.zeros([ACTIONS])
            a_t[a] = 1
            print("\033[1;33;40mUser: ", x_t,"\033[0m")
            print("LU: ",LU_frame)
            # some function using action_index and state_verbose to generate
            # semantic frame for the user simulator or the NLG module
            DM_frame = generate_DM_frame(s_t_verbose, action_dict[a])
            print("DoctorBot: ",DM_frame)
            x_t1, r_t, Terminal, Success = sim_user.step(DM_frame)
            s_t1, s_t_verbose, LU_frame = state_update(x_t1, lu_model.semantic_frame, s_t,s_t_verbose)
            action_affect_state(a, s_t1)
            print("/ ACTION", a, "/ REWARD", r_t,)
            s_t = s_t1
            x_t = x_t1
        print("\033[1;33;40mUser: ", x_t,"\033[0m")

def playGame():
    sess = tf.Session()
    s, readout, h_fc1, var = createNetwork()
    trainNetwork(s, readout, h_fc1, sess, var)

def main():
    UserSimDebug()
    #  playGame()

if __name__ == "__main__":
    main()
