#User Simulation
from random import shuffle
from random import choice
from random import uniform

def extract_time(s):
    return s.replace("."," ").replace("("," ").replace(")","").split()

# if you use python 3.6 , this function can be
# replaced with random.choices()
def weighted_choice(option):
    option = list(option)
    total  = sum(w for c, w in option)
    print(total)
    print(option)
    r = uniform(0, total)
    print("r = ",r)
    upto = 0
    for c, w in option:
        if upto + w >= r:
            return c
        upto += w
        print("upto = ",upto)
    assert False, "Shouldn't get here"

class User(object):
    reward_per_response = -1
    reward_repeat = -3
    reward_success = 20
    reward_fail = -100
    SUCCESS_CHECK = [lambda x: x["disease"] != None,
                     lambda x: x["disease"] != None,
                     lambda x: x["disease"] != None or x["division"] != None,
                     lambda x: x["doctor"]  != None,
                     lambda x: x["doctor"]  != None and x["time"] != None]
    ERROR_RATE = {"intent":0, "disease":0, "division":0, "doctor": 0, "time":0 }
    WRONG_DOCTOR_LIST = ["李琳山", "李宏毅", "陳縕儂", "廖世文", "楊佳玲"]
    day = ["一","二","三","四","五","六","日"]
    inv_day = {}
    for idx, i in enumerate(day):
        inv_day[i] = idx
    @staticmethod
    def error_time(s):
        if s in User.day:
            return User.day[choice([1,2,3,4,5,6]) + User.inv_day[s] % 7]
        else:
            return "一"
    def __init__(self, intent = None, slot = None):
        # default:  randomly pick up an intent if intent == None
        if intent != None and slot != None:
            self.intent = intent
            self.slot   = slot
        else:
            self.intent = 5
            self.slot   = { "disease": "過敏性鼻炎", "division": "耳鼻喉科", "doctor": "林怡岑", "time": "105.5.12" }
        self.state = {"disease": False, "division": False, "doctor": False, "time": False}
        self.observation = None
        self.reward_accumalation = 0
        if self.slot["time"] != None:
            self.time = extract_time(self.slot["time"])
    def error_date(self):
        wrong_date = str(int(self.time[2]) + choice([-3,-2,-1,1,2,3]))
        return self.time[0] + "." + self.time[1] + "." + wrong_date

    # for NLG
    def nlg_intent_1(self,response_slot):
        pattern_dic = {
        "disease":[self.slot["disease"]+"會怎樣",self.slot["disease"],"我想問"+self.slot["disease"],
        self.slot["disease"]+"會有什麼症狀"]
        }
        if response_slot in ['disease']:
            return choice(pattern_dic[response_slot])
        else:
            return "不要亂問"
    def nlg_intent_2(self,response_slot):
        pattern_dic = {
        "disease":[self.slot["disease"]+"要看什麼科",self.slot["disease"],"我想問"+self.slot["disease"],
        self.slot["disease"]+"屬於哪科",
        ]
        }
        if response_slot in ['disease']:
            return choice(pattern_dic[response_slot])
        else:
            return "不要亂問"
    def nlg_intent_3(self,response_slot):
        pattern_dic = {
        "disease":[self.slot["disease"]+"要看什麼科",self.slot["disease"],"我想問"+self.slot["disease"],
        self.slot["disease"]+"要看哪科"
        ],
        "time":[self.slot["time"]+"有誰可以",self.slot["time"],self.slot["time"]+"哪些醫生可以",
        self.slot["time"]+"有哪些醫生可以","我"+self.slot["time"]+"可以","我"+self.slot["time"]+"有空"
        ]
        }
        if response_slot in ['disease','time']:
            return choice(pattern_dic[response_slot])
        else:
            return "不要亂問"
    def nlg_intent_4(self,response_slot):
        if weighted_choice(zip([True, False],[User.ERROR_RATE["doctor"], 1 - User.ERROR_RATE["doctor"]])):
            doctor = choice(User.WRONG_DOCTOR_LIST)
        else:
            doctor = self.slot["doctor"]
        if weighted_choice(zip([True, False],[User.ERROR_RATE["time"], 1- User.ERROR_RATE["time"]])):
            time = self.error_date(self.time)
        else:
            time = ".".join(self.time[:3])
        pattern_dic = {
        "disease":[self.slot["disease"]+"的",self.slot["disease"],self.slot["disease"]],
        "doctor":["我要掛" + doctor + "的" + "門診時間表" ],
        "time":[ time +"的", time, time +"的時刻表"],
        "division":[self.slot["division"]+"的",self.slot["division"]]
        }
        if response_slot in ['intent']:
            return '不要亂'
        else:
            return choice(pattern_dic[response_slot])
    def nlg_intent_5(self,response_slot):
        if weighted_choice(zip([True, False],[User.ERROR_RATE["doctor"], 1 - User.ERROR_RATE["doctor"]])):
            doctor = choice(User.WRONG_DOCTOR_LIST)
        else:
            doctor = self.slot["doctor"]
        if weighted_choice(zip([True, False],[User.ERROR_RATE["time"], 1- User.ERROR_RATE["time"]])):
            time = self.error_date(self.time)
        else:
            time = ".".join(self.time[:3])
        pattern_dic = {
        "disease":["我得了"+self.slot["disease"],self.slot["disease"],"我有"+self.slot["disease"],
        self.slot["disease"]
        ],
        "time":[time+"的",time,"我"+time+"可以","我"+time+"有空"
        ],
        "doctor":["我要掛"+doctor],
        "division": self.slot['division']
        }
        if response_slot in ['intent']:
            return "幹"
        else:
            return choice(pattern_dic[response_slot])

    def check_if_something_wrong(self):
        # check if observation is consistent with users intent and slots
        wrong = False
        reward = User.reward_per_response
        response = ""
        for key in self.slot:
            if (self.state[key] == True
            and self.observation['state'][key] != None
            and self.observation['state'][key] != []):
                if self.slot[key] != self.observation['state'][key][0]:
                    if key == "disease" or key == "division":
                        wrong = True
                        response = "我是說" + self.slot[key]
                        break
                    if key == "time" and ".".join(self.time[:3]) != self.observation['state']['time'][0]:
                        wrong = True
                        response = "我是說" + ".".join(self.time[:3])
                    if key == "doctor":
                        wrong = True
                        response = "我是說我要掛" + self.slot[key]
        return wrong, response, reward;

    def say_intent_again(self):
        if self.intent == 1:
            self.state["disease"] = True
            response, reward = "我是說請問得"+self.slot["disease"]+"會怎樣", -1
        if self.intent == 2:
            self.state["disease"] = True
            response, reward = "我是說請問"+self.slot["disease"]+"要看哪一科", -1
        if self.intent == 3:
            self.state["time"] = True
            response, reward = "我是說請問"+self.slot["time"]+"有哪些醫生可以", -1
        if self.intent == 4:
            response, reward = "請問門診時間", -1
        if self.intent == 5:
            response, reward = "我想要掛號", -1
        return response, reward



    def response_dm_request(self):
        # if the slot request by DM is provided before, more punishment will be sent.
        # intent 3 and 5 are basically the same, only different in booking action.
        slot_to_respond = []
        if self.intent == 1:
            for slot in self.observation["slot"]:
                if self.slot[slot] != None:
                    slot_to_respond.append(slot)
            shuffle(slot_to_respond)
            if(self.state[slot_to_respond[0]]==True):
                return self.nlg_intent_1(slot_to_respond[0]), User.reward_repeat
            else:
                self.state[slot_to_respond[0]] = True
            return self.nlg_intent_1(slot_to_respond[0]), -1

        elif self.intent == 2:
            for slot in self.observation["slot"]:
                if self.slot[slot] != None:
                    slot_to_respond.append(slot)
            shuffle(slot_to_respond)
            if(self.state[slot_to_respond[0]]==True):
                return self.nlg_intent_2(slot_to_respond[0]), User.reward_repeat
            else:
                self.state[slot_to_respond[0]] = True
            return self.nlg_intent_2(slot_to_respond[0]), -1

        elif self.intent == 3:
            for slot in self.observation["slot"]:
                if self.slot[slot] != None:
                    slot_to_respond.append(slot)
            shuffle(slot_to_respond)
            if(self.state[slot_to_respond[0]]==True):
                return self.nlg_intent_3(slot_to_respond[0]), User.reward_repeat
            else:
                self.state[slot_to_respond[0]] = True
            return self.nlg_intent_3(slot_to_respond[0]), -1
        elif self.intent == 4:
            for slot in self.observation["slot"]:
                if self.slot[slot] != None:
                    slot_to_respond.append(slot)
            shuffle(slot_to_respond)
            if(self.state[slot_to_respond[0]]==True):
                return self.nlg_intent_4(slot_to_respond[0]), User.reward_repeat
            else:
                self.state[slot_to_respond[0]] = True
            return self.nlg_intent_4(slot_to_respond[0]), -1
        elif self.intent == 5:
#            print("++++++++ASKING+++++++")
            for slot in self.observation["slot"]:
                print(slot)
                if self.slot[slot] != None:
                    slot_to_respond.append(slot)
            shuffle(slot_to_respond)
            if(self.state[slot_to_respond[0]]==True):
                return self.nlg_intent_5(slot_to_respond[0]), User.reward_repeat
            else:
                self.state[slot_to_respond[0]] = True
            return self.nlg_intent_5(slot_to_respond[0]), -1
        # def response_dm_confirm(self):
        # def response_dm_inform(self):
    def response_dm_choose(self):
        print('++++++++++++++++++++++++++++++++++++++++++++++++')
        choose_slot = self.observation["slot"][0]
        if not self.observation['state'][choose_slot]:
            return self.say_intent_again()
        if self.slot[choose_slot] in self.observation["state"][choose_slot]:
            if choose_slot == "time":
                self.state["time"] = True
                return ".".join(self.time[0:3]), User.reward_per_response
            else:
                self.state[choose_slot] = True
                return self.slot[choose_slot], User.reward_per_response
        else:
            return self.say_intent_again() # I don't know if it is appropriate to say user's intent again when the slot is not in choose list
        #choosing principle?
        #1. random
        #2. base on other slot(flexible)?
    def response_dm_confirm(self):
        correct = True
        check_slots = self.observation["slot"]
        print(check_slots)
        for s in check_slots:
            if not self.observation['state'][s]:
                return "你沒查問屁問哦幹", User.reward_per_response
            elif self.observation['state'][s][0] != self.slot[s]:
                if s == "doctor":
                    return choice(["我是說我要掛","不，我是說我要掛"]) + str(self.slot[s]) + " 不是" + str(self.observation['state'][s]), User.reward_per_response
                return choice(["我是說","不，我是說"]) + self.slot[s] + " 不是" + str(self.observation['state'][s]), User.reward_per_response
        if correct:
            return choice(["對","是的","沒錯","就是這樣"]), User.reward_per_response

    def response_dm_end(self):
        #check if mission complete
        #1. intent compare
        #2. slot compare
        #INTENT CHANGING? 問到醫生之後再問時間?
        #answer checking
        self.success = True
        if(self.intent == self.observation["intent"]):
            if User.SUCCESS_CHECK[self.intent-1](self.observation["state"]):
                for key in self.slot:
                    if self.observation['state'][key] != None and self.observation['state'][key] !=[] and key != 'division':
                        if self.slot[key] != self.observation['state'][key][0]:
                            if not(key == "time" and ".".join(self.time[:3]) == self.observation['state']['time']):
                                self.success = False
                                break
        else:
            self.success = False
        if(self.success):
            return "謝謝", User.reward_success, True, True
        else:
            return "我病得更嚴重了", User.reward_fail, True, False

    def respond(self,observation):
        reward = -1
        end = False
        Success = False
        self.observation = observation
        wrong, response, reward = self.check_if_something_wrong()
        if wrong and self.observation["request"] != 'confirm':
            return response, reward, False, False
        if self.observation == None or self.observation["intent"] == None:
            if self.intent == 1:
                self.state["disease"] = True
                response, reward = "請問得"+self.slot["disease"]+"會怎樣", -1
            elif self.intent == 2:
                self.state["disease"] = True
                response, reward = "請問"+self.slot["disease"]+"要看哪科", -1
            elif self.intent == 3:
                self.state["time"] = True
                response, reward = "我想看"+self.slot["disease"]+"有哪些醫生可以", -1
            elif self.intent == 4:
                response, reward = "請問門診時間", -1
            elif self.intent == 5:
                response, reward = "我想要掛門診", -1
#        elif self.observation["intent"] != self.intent:
#            response, reward = self.say_intent_again()
        elif self.observation["request"] == "inform": # request
            response, reward = self.response_dm_request()
        elif self.observation["request"] == "choose":
            response, reward = self.response_dm_choose()
        elif self.observation["request"] == "confirm":
            response, reward = self.response_dm_confirm()
        elif self.observation["request"] == "end":
            response, reward, end, Success = self.response_dm_end()
        return response, reward, False, Success
                # respond DM's confirm, inform, or request
